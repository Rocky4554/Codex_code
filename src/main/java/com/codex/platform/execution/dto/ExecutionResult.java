package com.codex.platform.execution.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ExecutionResult {
    private String stdout;
    private String stderr;
    private Integer exitCode;
    private Long executionTimeMs;
    private boolean success;
}
