package com.codex.platform.submission.dto;

import com.codex.platform.common.enums.SubmissionStatus;
import lombok.AllArgsConstructor;
import lombok.Data;

import java.util.UUID;

@Data
@AllArgsConstructor
public class SubmitCodeResponse {
    private UUID submissionId;
    private SubmissionStatus status;
    private String message;
}
