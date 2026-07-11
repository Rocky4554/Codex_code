package com.codex.platform.playlist.dto;

import jakarta.validation.constraints.NotEmpty;
import lombok.Data;

import java.util.List;
import java.util.UUID;

@Data
public class ReorderPlaylistProblemsRequest {
    /** Full ordered list of problem IDs currently in the playlist. */
    @NotEmpty(message = "problemIds is required")
    private List<UUID> problemIds;
}
