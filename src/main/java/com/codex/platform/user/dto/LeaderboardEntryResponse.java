package com.codex.platform.user.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LeaderboardEntryResponse {
    private int rank;
    private UUID userId;
    private String username;
    private int solvedEasy;
    private int solvedMedium;
    private int solvedHard;
    private int totalScore;
}
