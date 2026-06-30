package com.codex.platform.assistant.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RAtomicLong;
import org.redisson.api.RedissonClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.Duration;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.util.UUID;

/**
 * Per-user daily quota for CodeBot (the "N left" counter, like NeetBot).
 *
 * <p>Backed by a Redis atomic counter keyed by user + UTC day. The first call of
 * the day creates the key and sets a ~25h TTL so it self-expires. Each AI request
 * increments it; once it passes the configured limit the request is rejected with
 * HTTP 429 and the increment is rolled back so the user is not charged a use for a
 * blocked request.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AssistantQuotaService {

    private static final String KEY_PREFIX = "assistant:quota:";

    private final RedissonClient redissonClient;

    @Value("${assistant.daily-limit:50}")
    private int dailyLimit;

    /** Reserve one use for today, or throw 429 if the user is out of quota. */
    public void consume(UUID userId) {
        String key = KEY_PREFIX + userId + ":" + LocalDate.now(ZoneOffset.UTC);
        RAtomicLong counter = redissonClient.getAtomicLong(key);

        long used = counter.incrementAndGet();
        if (used == 1L) {
            // First use today — set expiry so the key cleans itself up.
            counter.expire(Duration.ofHours(25));
        }

        if (used > dailyLimit) {
            counter.decrementAndGet(); // don't count a rejected request
            throw new ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS,
                    "Daily CodeBot limit reached (" + dailyLimit + "/day). Try again tomorrow.");
        }
    }

    /** Remaining uses for today (for showing the "N left" badge). */
    public int remaining(UUID userId) {
        String key = KEY_PREFIX + userId + ":" + LocalDate.now(ZoneOffset.UTC);
        long used = redissonClient.getAtomicLong(key).get();
        return (int) Math.max(0, dailyLimit - used);
    }

    public int dailyLimit() {
        return dailyLimit;
    }
}
