package com.codex.platform.ai.dto;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Data;

/** Body of {@code POST /api/problems/ai/edit}. */
@Data
public class AiEditRequest {

    /** The full draft currently shown in the admin form. */
    @NotNull(message = "Current problem draft is required")
    @Valid
    private ProblemDraft current;

    /** Natural-language change, e.g. "make it Hard and add 3 more test cases". */
    @NotBlank(message = "Instruction is required")
    @Size(max = 2000, message = "Instruction must not exceed 2000 characters")
    private String instruction;
}
