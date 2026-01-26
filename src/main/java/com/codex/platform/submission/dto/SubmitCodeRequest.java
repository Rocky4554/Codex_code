package com.codex.platform.submission.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.UUID;

@Data
public class SubmitCodeRequest {
    @NotNull(message = "Problem ID is required")
    private UUID problemId;

    @NotNull(message = "Language ID is required")
    private UUID languageId;

    @NotBlank(message = "Source code is required")
    private String sourceCode;
}
