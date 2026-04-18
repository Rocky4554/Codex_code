package com.codex.platform.run.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RunCodeResponse {

    private String status;
    private String stdout;
    private String stderr;
    private int testsPassed;
    private int totalTests;
    private List<TestResult> testResults;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TestResult {
        private String input;
        private String expectedOutput;
        private String actualOutput;
        private boolean passed;
    }
}
