package com.codex.platform.user.controller;

import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import com.codex.platform.user.dto.CurrentUserLeaderboardResponse;
import com.codex.platform.user.dto.LeaderboardEntryResponse;
import com.codex.platform.user.service.LeaderboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/leaderboard")
@RequiredArgsConstructor
public class LeaderboardController {

    private final LeaderboardService leaderboardService;

    @GetMapping
    public ResponseEntity<List<LeaderboardEntryResponse>> getLeaderboard(
            @RequestParam(defaultValue = "100") int limit) {
        return ResponseEntity.ok(leaderboardService.getLeaderboard(limit));
    }

    @GetMapping("/me")
    public ResponseEntity<CurrentUserLeaderboardResponse> getCurrentUserLeaderboardStats() {
        return ResponseEntity.ok(
                leaderboardService.getCurrentUserLeaderboardStats(JwtAuthenticationFilter.getCurrentUserId())
        );
    }
}
