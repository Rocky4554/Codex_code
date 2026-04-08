package com.codex.platform.execution.client.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.UUID;

/**
 * Backend-side mirror of {@code com.codex.agent.dto.ExecuteResponse}.
 * Received over HTTP from the executor agent on EC2 when {@code execution.mode=remote}.
 *
 * <p>{@code status} is a string here (not the {@code SubmissionStatus} enum) so
 * deserialization is forgiving — {@code ExecutionService} maps it to the enum
 * with a safe fallback to {@code RUNTIME_ERROR}.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ExecuteResponse {
    private UUID submissionId;
    private String status;
    private String compileOutput;
    private long compileTimeMs;
    private long totalExecTimeMs;
    private int passedTestCases;
    private int totalTestCases;
    private String stdout;
    private String stderr;
    private List<TestResult> results;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestResult {
        private String testCaseId;
        private String status;
        private String stdout;
        private String stderr;
        private long execTimeMs;
        private int exitCode;
    }
}
