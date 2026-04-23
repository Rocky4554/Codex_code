package com.codex.platform.user.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

/**
 * Runs after the application (including the web server) is fully up.
 * Using {@code ApplicationRunner} here caused failures on slow hosts (e.g. Render) when the
 * platform sent SIGTERM during long startup: {@code callRunners} then raced with context shutdown
 * and could throw {@code BeanCreationNotAllowedException}.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class LeaderboardBackfillInitializer {

    private final LeaderboardStatsBackfillService leaderboardStatsBackfillService;

    @Order(20)
    @EventListener(ApplicationReadyEvent.class)
    public void onApplicationReady() {
        try {
            leaderboardStatsBackfillService.backfillStats();
        } catch (Exception e) {
            log.error("Leaderboard stats backfill failed: {}", e.getMessage(), e);
        }
    }
}
