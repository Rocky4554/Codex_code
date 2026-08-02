package com.codex.platform.auth.passwordreset;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RAtomicLong;
import org.redisson.api.RBucket;
import org.redisson.api.RedissonClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.time.Duration;
import java.util.Optional;
import java.util.UUID;

/**
 * Redis-backed OTP / cooldown / rate-limit store for password reset.
 * Namespaces follow {@link PasswordResetRedisKeys}.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class PasswordResetOtpStore {

    private final RedissonClient redissonClient;
    private final ObjectMapper objectMapper;

    @Value("${password-reset.otp-ttl-seconds:600}")
    private long otpTtlSeconds;

    @Value("${password-reset.cooldown-seconds:60}")
    private long cooldownSeconds;

    @Value("${password-reset.forgot-rate-limit:3}")
    private long forgotRateLimit;

    @Value("${password-reset.forgot-rate-window-seconds:3600}")
    private long forgotRateWindowSeconds;

    @Value("${password-reset.reset-rate-limit:5}")
    private long resetRateLimit;

    @Value("${password-reset.reset-rate-window-seconds:3600}")
    private long resetRateWindowSeconds;

    public void saveOtp(UUID userId, OtpRecord record) {
        RBucket<String> bucket = redissonClient.getBucket(PasswordResetRedisKeys.otp(userId));
        try {
            bucket.set(objectMapper.writeValueAsString(record), Duration.ofSeconds(otpTtlSeconds));
        } catch (Exception e) {
            throw new IllegalStateException("Failed to store OTP", e);
        }
    }

    public Optional<OtpRecord> getOtp(UUID userId) {
        RBucket<String> bucket = redissonClient.getBucket(PasswordResetRedisKeys.otp(userId));
        String json = bucket.get();
        if (json == null || json.isBlank()) {
            return Optional.empty();
        }
        try {
            return Optional.of(objectMapper.readValue(json, OtpRecord.class));
        } catch (Exception e) {
            log.warn("Corrupt OTP record for user {}: {}", userId, e.getMessage());
            bucket.delete();
            return Optional.empty();
        }
    }

    public void updateOtp(UUID userId, OtpRecord record) {
        RBucket<String> bucket = redissonClient.getBucket(PasswordResetRedisKeys.otp(userId));
        long ttlMs = bucket.remainTimeToLive();
        try {
            String json = objectMapper.writeValueAsString(record);
            if (ttlMs > 0) {
                bucket.set(json, Duration.ofMillis(ttlMs));
            } else {
                bucket.set(json, Duration.ofSeconds(otpTtlSeconds));
            }
        } catch (Exception e) {
            throw new IllegalStateException("Failed to update OTP", e);
        }
    }

    public void deleteOtp(UUID userId) {
        redissonClient.getBucket(PasswordResetRedisKeys.otp(userId)).delete();
    }

    public boolean isCooldownActive(String email) {
        return redissonClient.getBucket(PasswordResetRedisKeys.cooldown(email)).isExists();
    }

    public void setCooldown(String email) {
        redissonClient.getBucket(PasswordResetRedisKeys.cooldown(email))
                .set("1", Duration.ofSeconds(cooldownSeconds));
    }

    /** @return false if rate limit exceeded */
    public boolean tryConsumeForgotQuota(String email) {
        return incrementWithinWindow(
                PasswordResetRedisKeys.rateLimitForgot(email),
                forgotRateLimit,
                forgotRateWindowSeconds);
    }

    /** @return false if rate limit exceeded */
    public boolean tryConsumeResetQuota(UUID userId) {
        return incrementWithinWindow(
                PasswordResetRedisKeys.rateLimitReset(userId),
                resetRateLimit,
                resetRateWindowSeconds);
    }

    public void markVerified(UUID userId, String jti, long ttlSeconds) {
        redissonClient.getBucket(PasswordResetRedisKeys.verified(userId))
                .set(jti, Duration.ofSeconds(ttlSeconds));
    }

    public Optional<String> getVerifiedJti(UUID userId) {
        Object v = redissonClient.getBucket(PasswordResetRedisKeys.verified(userId)).get();
        return v == null ? Optional.empty() : Optional.of(v.toString());
    }

    public void clearVerified(UUID userId) {
        redissonClient.getBucket(PasswordResetRedisKeys.verified(userId)).delete();
    }

    private boolean incrementWithinWindow(String key, long limit, long windowSeconds) {
        RAtomicLong counter = redissonClient.getAtomicLong(key);
        long value = counter.incrementAndGet();
        if (value == 1L) {
            counter.expire(Duration.ofSeconds(windowSeconds));
        }
        return value <= limit;
    }
}
