package com.codex.platform.playlist.dto;

import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class PlaylistUpdateRequest {
    @Size(max = 120, message = "Title must not exceed 120 characters")
    private String title;

    @Size(max = 2000, message = "Description must not exceed 2000 characters")
    private String description;
}
