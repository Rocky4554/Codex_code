package com.codex.platform.playlist.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.UUID;

@Data
public class AddProblemToPlaylistRequest {
    @NotNull(message = "problemId is required")
    private UUID problemId;
}
