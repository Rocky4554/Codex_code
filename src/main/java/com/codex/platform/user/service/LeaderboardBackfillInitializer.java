package com.codex.platform.user.service;

import lombok.RequiredArgsConstructor;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class LeaderboardBackfillInitializer implements ApplicationRunner {

    private final LeaderboardStatsBackfillService leaderboardStatsBackfillService;

    @Override
    public void run(ApplicationArguments args) {
        leaderboardStatsBackfillService.backfillStats();
    }
}
