package com.codex.platform.execution.client.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.UUID;

/**
 * Backend-side mirror of {@code com.codex.agent.dto.ExecuteRequest}.
 * Sent over HTTP to the executor agent on EC2 when {@code execution.mode=remote}.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ExecuteRequest {
    private UUID submissionId;
    private String language;
    private String dockerImage;
    private String compileCommand;
    private String executeCommand;
    private String fileExtension;
    private String sourceCode;
    private int compileTimeoutMs;
    private int runTimeoutMs;
    private int memoryLimitMb;
    private List<TestCase> testCases;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestCase {
        private String id;
        private String stdin;
        private String expectedStdout;
    }
}
