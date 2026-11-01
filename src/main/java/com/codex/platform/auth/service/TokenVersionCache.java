package com.codex.platform.auth.service;

import com.codex.platform.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

/**
 * Short-lived in-memory cache of each user's tokenVersion so the JWT filter
 * doesn't hit the database on every authenticated request.
 * Evicted immediately on password reset; other instances catch up within TTL.
 */
@Component
@RequiredArgsConstructor
public class TokenVersionCache {

    private static final long TTL_MS = 30_000;

    private final UserRepository userRepository;
    private final Map<UUID, Entry> cache = new ConcurrentHashMap<>();

    private record Entry(int version, long expiresAt) {}

    /** Current tokenVersion for the user, or empty if the user doesn't exist. */
    public Optional<Integer> get(UUID userId) {
        Entry entry = cache.get(userId);
        long now = System.currentTimeMillis();
        if (entry != null && entry.expiresAt() > now) {
            return Optional.of(entry.version());
        }
        return userRepository.findById(userId).map(user -> {
            int version = user.getTokenVersion() == null ? 0 : user.getTokenVersion();
            cache.put(userId, new Entry(version, now + TTL_MS));
            return version;
        });
    }

    public void evict(UUID userId) {
        cache.remove(userId);
    }
}
