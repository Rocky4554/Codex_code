package com.codex.platform.problem.dto;

import com.codex.platform.common.enums.ProblemDifficulty;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class ProblemRequest {
    @NotBlank(message = "Title is required")
    @Size(max = 255, message = "Title must not exceed 255 characters")
    private String title;

    @NotBlank(message = "Description is required")
    @Size(max = 10000, message = "Description must not exceed 10000 characters")
    private String description;

    @NotNull(message = "Difficulty is required")
    private ProblemDifficulty difficulty;

    @NotNull(message = "Time limit is required")
    @Min(value = 100, message = "Time limit must be at least 100ms")
    @Max(value = 120000, message = "Time limit must not exceed 120000ms")
    private Integer timeLimitMs;

    @NotNull(message = "Memory limit is required")
    @Min(value = 16, message = "Memory limit must be at least 16MB")
    @Max(value = 2048, message = "Memory limit must not exceed 2048MB")
    private Integer memoryLimitMb;
}
