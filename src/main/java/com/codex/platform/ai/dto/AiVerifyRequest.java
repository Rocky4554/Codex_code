package com.codex.platform.ai.dto;

import jakarta.validation.constraints.NotEmpty;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

import java.util.List;

/**
 * Body of {@code POST /api/problems/ai/verify} — verify a hand-authored (non-AI)
 * reference solution against hand-authored test cases. Used by the "Add manually"
 * form so SQL problems get the same real-execution verification (and automatic
 * {@code ORDER BY} fix-up) as AI-generated ones, without calling Gemini.
 */
@Data
public class AiVerifyRequest {

    @NotNull(message = "Reference solution is required")
    private ProblemDraft.ReferenceSolution referenceSolution;

    @NotEmpty(message = "At least one test case is required")
    private List<ProblemDraft.TestCaseDraft> testCases;

    private Integer timeLimitMs;
    private Integer memoryLimitMb;
}
