package com.codex.platform.auth.passwordreset;

import java.util.Locale;
import java.util.UUID;

public final class PasswordResetRedisKeys {

    private PasswordResetRedisKeys() {}

    public static String otp(UUID userId) {
        return "password-reset:otp:" + userId;
    }

    public static String cooldown(String email) {
        return "password-reset:cooldown:" + email.trim().toLowerCase(Locale.ROOT);
    }

    public static String rateLimitForgot(String email) {
        return "password-reset:ratelimit:forgot:" + email.trim().toLowerCase(Locale.ROOT);
    }

    public static String rateLimitReset(UUID userId) {
        return "password-reset:ratelimit:reset:" + userId;
    }

    public static String verified(UUID userId) {
        return "password-reset:verified:" + userId;
    }
}
