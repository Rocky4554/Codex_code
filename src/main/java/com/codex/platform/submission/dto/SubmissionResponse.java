package com.codex.platform.submission.dto;

import com.codex.platform.common.enums.SubmissionStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmissionResponse {
    private UUID id;
    private UUID userId;
    private UUID problemId;
    private UUID languageId;
    private SubmissionStatus status;
    private LocalDateTime createdAt;

    // Result details (null if not yet processed)
    private Long executionTimeMs;
    private Long memoryUsedMb;
    private Integer passedTestCases;
    private Integer totalTestCases;
    private String stdout;
    private String stderr;
}
