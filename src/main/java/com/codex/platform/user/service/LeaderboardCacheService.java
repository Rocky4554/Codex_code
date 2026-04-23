package com.codex.platform.user.service;

import com.codex.platform.user.dto.LeaderboardEntryResponse;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RBucket;
import org.redisson.api.RedissonClient;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
@Slf4j
public class LeaderboardCacheService {

    private static final Duration CACHE_TTL = Duration.ofMinutes(5);
    private static final String LEADERBOARD_KEY_PREFIX = "leaderboard:top:";

    private final RedissonClient redissonClient;
    private final ObjectMapper objectMapper;

    public Optional<List<LeaderboardEntryResponse>> getLeaderboard(int limit) {
        try {
            RBucket<String> bucket = redissonClient.getBucket(cacheKey(limit));
            String payload = bucket.get();
            if (payload == null || payload.isBlank()) {
                return Optional.empty();
            }

            List<LeaderboardEntryResponse> entries = objectMapper.readValue(
                    payload,
                    new TypeReference<List<LeaderboardEntryResponse>>() {
                    });
            return Optional.of(entries);
        } catch (Exception e) {
            log.warn("Failed to read leaderboard cache: {}", e.getMessage());
            return Optional.empty();
        }
    }

    public void cacheLeaderboard(int limit, List<LeaderboardEntryResponse> entries) {
        try {
            RBucket<String> bucket = redissonClient.getBucket(cacheKey(limit));
            String payload = objectMapper.writeValueAsString(entries);
            bucket.set(payload, CACHE_TTL);
        } catch (Exception e) {
            log.warn("Failed to write leaderboard cache: {}", e.getMessage());
        }
    }

    public void evictLeaderboard() {
        try {
            redissonClient.getKeys().deleteByPattern(LEADERBOARD_KEY_PREFIX + "*");
        } catch (Exception e) {
            log.warn("Failed to evict leaderboard cache: {}", e.getMessage());
        }
    }

    private String cacheKey(int limit) {
        return LEADERBOARD_KEY_PREFIX + limit;
    }
}
