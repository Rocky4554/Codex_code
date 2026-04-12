package com.codex.platform.problem.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.UUID;

@Data
public class TestCaseRequest {
    @NotNull(message = "Problem ID is required")
    private UUID problemId;

    @NotBlank(message = "Input is required")
    private String input;

    @NotBlank(message = "Expected output is required")
    private String expectedOutput;

    private Boolean isSample = false;
}
