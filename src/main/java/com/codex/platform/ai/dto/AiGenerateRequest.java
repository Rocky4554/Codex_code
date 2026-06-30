package com.codex.platform.ai.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

/** Body of {@code POST /api/problems/ai/generate}. */
@Data
public class AiGenerateRequest {

    /** The problem to look up, e.g. "Two Sum" or "Kadane's maximum subarray". */
    @NotBlank(message = "Problem name is required")
    @Size(max = 300, message = "Problem name must not exceed 300 characters")
    private String name;

    /** Optional extra guidance, e.g. "make it Hard, stdin is one line of integers". */
    @Size(max = 2000, message = "Notes must not exceed 2000 characters")
    private String notes;
}
