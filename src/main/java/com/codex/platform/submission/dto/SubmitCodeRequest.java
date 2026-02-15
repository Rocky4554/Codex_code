package com.codex.platform.submission.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

import java.util.UUID;

@Data
public class SubmitCodeRequest {
    @NotNull(message = "Problem ID is required")
    private UUID problemId;

    @NotNull(message = "Language ID is required")
    private UUID languageId;

    @NotBlank(message = "Source code is required")
    @Size(max = 100000, message = "Source code must not exceed 100000 characters")
    private String sourceCode;
}
