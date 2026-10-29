package com.codex.platform.playlist.dto;

import com.codex.platform.common.enums.ProblemDifficulty;
import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Data
@Builder
public class PlaylistResponse {
    private UUID id;
    private String title;
    private String description;
    private String accentColor;
    private int problemCount;
    /** True for system playlists, which users cannot edit. */
    private boolean featured;
    private Instant createdAt;
    private Instant updatedAt;
    private List<PlaylistProblemSummary> problems;

    @Data
    @Builder
    public static class PlaylistProblemSummary {
        private UUID id;
        private String title;
        private ProblemDifficulty difficulty;
        private Integer position;
        private boolean userCreated;
    }
}
