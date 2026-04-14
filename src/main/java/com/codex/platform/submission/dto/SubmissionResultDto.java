package com.codex.platform.submission.dto;

import com.codex.platform.common.enums.SubmissionStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.util.UUID;

/**
 * Lightweight DTO stored in Redis as JSON after execution completes.
 * Contains everything the frontend needs to render the verdict panel.
 * TTL is controlled by submission.cache.result-ttl-seconds (default 3600).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SubmissionResultDto implements Serializable {

    private UUID submissionId;
    private SubmissionStatus status;

    private Long executionTimeMs;
    private Long memoryUsedMb;
    private Integer passedTestCases;
    private Integer totalTestCases;
    private String stdout;
    private String stderr;
}
