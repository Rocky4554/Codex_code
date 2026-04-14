package com.codex.platform.submission.service;

import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.submission.dto.SubmissionResultDto;
import com.codex.platform.submission.entity.SubmissionResult;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RBucket;
import org.redisson.api.RedissonClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.Optional;
import java.util.UUID;

/**
 * Handles caching of submission results in Redis.
 *
 * <p>Key scheme: {@code submission:result:{submissionId}}
 * <p>TTL: configurable via {@code submission.cache.result-ttl-seconds} (default 3600 s = 1 h)
 *
 * <p>Lifecycle:
 * <ol>
 *   <li>Execution finishes → {@link #cacheResult} writes the verdict to Redis.</li>
 *   <li>{@link SseService} fires the SSE event immediately after (result already in cache).</li>
 *   <li>{@link AsyncResultPersister} persists to PostgreSQL in the background.</li>
 *   <li>After successful DB persist → {@link #evict} removes the Redis entry so future
 *       REST queries go to the canonical DB source.</li>
 *   <li>If DB persist fails the entry naturally expires after TTL, acting as a safety net.</li>
 * </ol>
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class SubmissionCacheService {

    private static final String KEY_PREFIX = "submission:result:";

    private final RedissonClient redissonClient;
    private final ObjectMapper objectMapper;

    @Value("${submission.cache.result-ttl-seconds:3600}")
    private long resultTtlSeconds;

    // ── Write ──────────────────────────────────────────────────────────────────

    /**
     * Cache the full result immediately after execution, before the DB write.
     */
    public void cacheResult(UUID submissionId, SubmissionStatus status, SubmissionResult result) {
        SubmissionResultDto dto = SubmissionResultDto.builder()
                .submissionId(submissionId)
                .status(status)
                .executionTimeMs(result.getExecutionTimeMs())
                .memoryUsedMb(result.getMemoryUsedMb())
                .passedTestCases(result.getPassedTestCases())
                .totalTestCases(result.getTotalTestCases())
                .stdout(result.getStdout())
                .stderr(result.getStderr())
                .build();

        try {
            String json = objectMapper.writeValueAsString(dto);
            RBucket<String> bucket = redissonClient.getBucket(KEY_PREFIX + submissionId);
            bucket.set(json, Duration.ofSeconds(resultTtlSeconds));
            log.debug("Cached result for submission {} (TTL={}s)", submissionId, resultTtlSeconds);
        } catch (Exception e) {
            // Non-fatal — fall back to DB only
            log.warn("Failed to cache result for submission {}: {}", submissionId, e.getMessage());
        }
    }

    /**
     * Cache a status-only result (e.g. RUNTIME_ERROR with no full result object).
     */
    public void cacheStatus(UUID submissionId, SubmissionStatus status) {
        SubmissionResultDto dto = SubmissionResultDto.builder()
                .submissionId(submissionId)
                .status(status)
                .build();

        try {
            String json = objectMapper.writeValueAsString(dto);
            RBucket<String> bucket = redissonClient.getBucket(KEY_PREFIX + submissionId);
            bucket.set(json, Duration.ofSeconds(resultTtlSeconds));
            log.debug("Cached status-only result for submission {} -> {}", submissionId, status);
        } catch (Exception e) {
            log.warn("Failed to cache status for submission {}: {}", submissionId, e.getMessage());
        }
    }

    // ── Read ───────────────────────────────────────────────────────────────────

    /**
     * Retrieve cached result — used by REST GET /api/submissions/{id} as cache-aside.
     */
    public Optional<SubmissionResultDto> getCachedResult(UUID submissionId) {
        try {
            RBucket<String> bucket = redissonClient.getBucket(KEY_PREFIX + submissionId);
            String json = bucket.get();
            if (json == null) {
                return Optional.empty();
            }
            SubmissionResultDto dto = objectMapper.readValue(json, SubmissionResultDto.class);
            log.debug("Cache HIT for submission {}", submissionId);
            return Optional.of(dto);
        } catch (Exception e) {
            log.warn("Failed to read cache for submission {}: {}", submissionId, e.getMessage());
            return Optional.empty();
        }
    }

    // ── Evict ─────────────────────────────────────────────────────────────────

    /**
     * Remove the cached entry after successful DB persist.
     * Safe to call even if the key no longer exists.
     */
    public void evict(UUID submissionId) {
        try {
            redissonClient.getBucket(KEY_PREFIX + submissionId).delete();
            log.debug("Evicted cache for submission {}", submissionId);
        } catch (Exception e) {
            log.warn("Failed to evict cache for submission {}: {}", submissionId, e.getMessage());
        }
    }
}
