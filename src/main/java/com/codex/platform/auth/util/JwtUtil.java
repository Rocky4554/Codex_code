package com.codex.platform.auth.util;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.UUID;

@Component
public class JwtUtil {

    public static final String PURPOSE_PASSWORD_RESET = "password_reset";

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration}")
    private Long expiration;

    @Value("${password-reset.jwt-ttl-ms:600000}")
    private Long passwordResetTtlMs;

    @PostConstruct
    public void validateSecret() {
        if (secret == null || secret.getBytes(StandardCharsets.UTF_8).length < 32) {
            throw new IllegalStateException("JWT secret must be at least 32 bytes (256 bits)");
        }
    }

    private SecretKey getSigningKey() {
        return Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    /** Access token used for normal API auth. Embeds {@code tokenVersion} for global logout. */
    public String generateToken(UUID userId, String username, String role, int tokenVersion) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);

        return Jwts.builder()
                .subject(username)
                .claim("userId", userId.toString())
                .claim("role", role)
                .claim("tokenVersion", tokenVersion)
                .id(UUID.randomUUID().toString())
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }

    /** Short-lived token issued only after OTP verification. */
    public String generatePasswordResetToken(UUID userId, String jti) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + passwordResetTtlMs);

        return Jwts.builder()
                .subject(userId.toString())
                .claim("userId", userId.toString())
                .claim("purpose", PURPOSE_PASSWORD_RESET)
                .id(jti)
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(getSigningKey())
                .compact();
    }

    public String extractRole(String token) {
        String role = extractClaims(token).get("role", String.class);
        return role != null ? role : "USER";
    }

    public String extractUsername(String token) {
        return extractClaims(token).getSubject();
    }

    public UUID extractUserId(String token) {
        String userIdStr = extractClaims(token).get("userId", String.class);
        return UUID.fromString(userIdStr);
    }

    public int extractTokenVersion(String token) {
        Integer version = extractClaims(token).get("tokenVersion", Integer.class);
        return version != null ? version : 0;
    }

    public String extractPurpose(String token) {
        return extractClaims(token).get("purpose", String.class);
    }

    public String extractJti(String token) {
        return extractClaims(token).getId();
    }

    public boolean validateToken(String token) {
        try {
            Claims claims = extractClaims(token);
            return !claims.getExpiration().before(new Date());
        } catch (Exception e) {
            return false;
        }
    }

    public boolean isPasswordResetToken(String token) {
        try {
            return PURPOSE_PASSWORD_RESET.equals(extractPurpose(token)) && validateToken(token);
        } catch (Exception e) {
            return false;
        }
    }

    public Claims extractClaims(String token) {
        return Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }
}
