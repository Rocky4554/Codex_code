package com.codex.platform.problem.dto;

import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.UUID;

@Data
public class TestCaseRequest {
    @NotNull(message = "Problem ID is required")
    private UUID problemId;

    @NotNull(message = "Input is required")
    private String input;

    @NotNull(message = "Expected output is required")
    private String expectedOutput;

    private Boolean isSample = false;
}
