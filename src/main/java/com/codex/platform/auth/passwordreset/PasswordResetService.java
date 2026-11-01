package com.codex.platform.auth.passwordreset;

import com.codex.platform.auth.dto.MessageResponse;
import com.codex.platform.auth.dto.VerifyOtpResponse;
import com.codex.platform.auth.service.TokenVersionCache;
import com.codex.platform.auth.util.JwtUtil;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.security.SecureRandom;
import java.time.Instant;
import java.util.Locale;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class PasswordResetService {

    private static final String GENERIC_FORGOT_MESSAGE =
            "If the email exists, an OTP has been sent.";
    private static final int MAX_OTP_ATTEMPTS = 5;

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;
    private final PasswordResetOtpStore otpStore;
    private final MailService mailService;
    private final TokenVersionCache tokenVersionCache;
    private final SecureRandom secureRandom = new SecureRandom();

    @Value("${password-reset.jwt-ttl-ms:600000}")
    private long passwordResetTtlMs;

    @Value("${password-reset.max-otp-attempts:5}")
    private int maxOtpAttempts;

    /**
     * Always returns a generic success message (no email enumeration).
     * Cooldown / rate-limit failures are still surfaced so legitimate users know to wait.
     */
    public MessageResponse forgotPassword(String rawEmail) {
        String email = normalizeEmail(rawEmail);

        if (!otpStore.tryConsumeForgotQuota(email)) {
            throw new ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS,
                    "Too many reset requests. Please try again later.");
        }

        if (otpStore.isCooldownActive(email)) {
            throw new ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS,
                    "Please wait before requesting another OTP.");
        }

        Optional<User> userOpt = userRepository.findByEmail(email);
        if (userOpt.isEmpty()) {
            // Same timing surface as success path — still set a short cooldown to reduce probing noise.
            otpStore.setCooldown(email);
            log.info("Password-reset requested for unknown email");
            return new MessageResponse(GENERIC_FORGOT_MESSAGE);
        }

        User user = userOpt.get();
        String otp = generateOtp();
        OtpRecord record = new OtpRecord(passwordEncoder.encode(otp), 0, Instant.now());
        otpStore.saveOtp(user.getId(), record); // overwrites any previous OTP
        otpStore.setCooldown(email);
        otpStore.clearVerified(user.getId());

        mailService.sendPasswordResetOtp(user.getEmail(), user.getUsername(), otp);
        log.info("Password-reset OTP issued for userId={}", user.getId());

        return new MessageResponse(GENERIC_FORGOT_MESSAGE);
    }

    public VerifyOtpResponse verifyOtp(String rawEmail, String otp) {
        String email = normalizeEmail(rawEmail);
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid OTP."));

        OtpRecord record = otpStore.getOtp(user.getId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.BAD_REQUEST,
                        "OTP expired. Request a new OTP."));

        int attemptLimit = maxOtpAttempts > 0 ? maxOtpAttempts : MAX_OTP_ATTEMPTS;
        if (record.getAttempts() >= attemptLimit) {
            otpStore.deleteOtp(user.getId());
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "OTP expired. Request a new OTP.");
        }

        if (!passwordEncoder.matches(otp, record.getOtpHash())) {
            record.setAttempts(record.getAttempts() + 1);
            if (record.getAttempts() >= attemptLimit) {
                otpStore.deleteOtp(user.getId());
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                        "OTP expired. Request a new OTP.");
            }
            otpStore.updateOtp(user.getId(), record);
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Invalid OTP.");
        }

        // Success — one-time OTP
        otpStore.deleteOtp(user.getId());
        String jti = UUID.randomUUID().toString();
        long ttlSeconds = Math.max(60, passwordResetTtlMs / 1000);
        otpStore.markVerified(user.getId(), jti, ttlSeconds);
        String resetToken = jwtUtil.generatePasswordResetToken(user.getId(), jti);

        log.info("Password-reset OTP verified for userId={}", user.getId());
        return new VerifyOtpResponse(resetToken, "OTP verified. You may now set a new password.");
    }

    @Transactional
    public MessageResponse resetPassword(String resetJwt, String newPassword) {
        if (resetJwt == null || resetJwt.isBlank()) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Reset token required");
        }
        if (!jwtUtil.isPasswordResetToken(resetJwt)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid or expired reset token");
        }

        UUID userId = jwtUtil.extractUserId(resetJwt);
        String jti = jwtUtil.extractJti(resetJwt);

        String storedJti = otpStore.getVerifiedJti(userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.UNAUTHORIZED,
                        "Reset token already used or expired"));
        if (!storedJti.equals(jti)) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid reset token");
        }

        if (!otpStore.tryConsumeResetQuota(userId)) {
            throw new ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS,
                    "Too many password resets. Please try again later.");
        }

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "User not found"));

        user.setPasswordHash(passwordEncoder.encode(newPassword));
        int nextVersion = (user.getTokenVersion() == null ? 0 : user.getTokenVersion()) + 1;
        user.setTokenVersion(nextVersion);
        userRepository.save(user);
        tokenVersionCache.evict(userId);

        // Invalidate the one-time reset JWT and any leftover OTP state
        otpStore.clearVerified(userId);
        otpStore.deleteOtp(userId);

        log.info("Password reset completed for userId={} (tokenVersion={})", userId, nextVersion);
        return new MessageResponse("Password updated successfully. Please log in with your new password.");
    }

    private String generateOtp() {
        int n = secureRandom.nextInt(1_000_000);
        return String.format("%06d", n);
    }

    private static String normalizeEmail(String email) {
        return email == null ? "" : email.trim().toLowerCase(Locale.ROOT);
    }
}
