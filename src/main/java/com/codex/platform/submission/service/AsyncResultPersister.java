package com.codex.platform.submission.service;

import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.entity.SubmissionResult;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.UUID;

/**
 * Persists execution results to PostgreSQL asynchronously, AFTER the result has
 * already been cached in Redis and the SSE event has been sent to the client.
 *
 * <p>This decouples the user-facing latency (Redis + SSE, sub-millisecond) from
 * the DB write latency (tens of milliseconds over the network to Supabase).
 *
 * <p>On success: evicts the Redis cache entry so future REST reads go to the DB.
 * <p>On failure: logs the error; the Redis entry will expire after its TTL (1 h)
 *   and continue serving reads until then. A retry or alerting mechanism can be
 *   added as a follow-up.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AsyncResultPersister {

    private final ResultProcessor resultProcessor;
    private final SubmissionCacheService cacheService;

    /**
     * Runs on the {@code submissionPersistExecutor} thread pool (configured in
     * application properties). Calls {@link ResultProcessor#saveResult} which
     * performs 2–3 DB writes inside a transaction, then evicts the Redis entry.
     *
     * @param submission  managed entity (detached after hand-off — re-attached by
     *                    the new transaction opened inside ResultProcessor)
     * @param result      the populated SubmissionResult to persist
     * @param finalStatus the terminal verdict
     */
    @Async("submissionPersistExecutor")
    public void saveAsync(Submission submission, SubmissionResult result, SubmissionStatus finalStatus) {
        UUID submissionId = submission.getId();
        log.info("Async DB persist starting for submission: {} status={}", submissionId, finalStatus);

        try {
            resultProcessor.saveResult(submission, result, finalStatus);
            log.info("Async DB persist succeeded for submission: {}", submissionId);

            // Evict Redis entry — DB is now the source of truth
            cacheService.evict(submissionId);

        } catch (Exception e) {
            log.error("Async DB persist FAILED for submission: {} — result remains in Redis cache until TTL expires",
                    submissionId, e);
            // Do NOT re-throw — this runs in a background thread; the SSE event has
            // already been delivered to the client.
        }
    }
}
