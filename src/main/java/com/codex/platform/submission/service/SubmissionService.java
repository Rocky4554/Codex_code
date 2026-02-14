package com.codex.platform.submission.service;

import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.execution.repository.LanguageRepository;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.queue.service.QueueService;
import com.codex.platform.submission.dto.SubmitCodeRequest;
import com.codex.platform.submission.dto.SubmitCodeResponse;
import com.codex.platform.submission.dto.SubmissionResponse;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.entity.SubmissionResult;
import com.codex.platform.submission.repository.SubmissionRepository;
import com.codex.platform.submission.repository.SubmissionResultRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class SubmissionService {

    private final SubmissionRepository submissionRepository;
    private final SubmissionResultRepository submissionResultRepository;
    private final ProblemRepository problemRepository;
    private final LanguageRepository languageRepository;
    private final QueueService queueService;

    @Transactional
    public SubmitCodeResponse submitCode(SubmitCodeRequest request, HttpServletRequest httpRequest) {
        // Extract userId from SecurityContext (set by JwtAuthenticationFilter)
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();

        // Validate problem exists
        if (!problemRepository.existsById(request.getProblemId())) {
            throw new IllegalArgumentException("Problem not found");
        }

        // Validate language exists
        if (!languageRepository.existsById(request.getLanguageId())) {
            throw new IllegalArgumentException("Language not found");
        }

        // Create submission
        Submission submission = new Submission();
        submission.setUserId(userId);
        submission.setProblemId(request.getProblemId());
        submission.setLanguageId(request.getLanguageId());
        submission.setSourceCode(request.getSourceCode());
        submission.setStatus(SubmissionStatus.QUEUED);

        Submission savedSubmission = submissionRepository.save(submission);

        // Enqueue for processing ONLY AFTER the transaction commits
        final UUID submissionId = savedSubmission.getId();
        TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
            @Override
            public void afterCommit() {
                queueService.enqueue(submissionId);
                log.info("Submission enqueued after commit: {}", submissionId);
            }
        });

        log.info("Submission created and queued: {}", savedSubmission.getId());

        return new SubmitCodeResponse(
                savedSubmission.getId(),
                SubmissionStatus.QUEUED,
                "Submission queued for execution");
    }

    /**
     * Get submission details by ID
     */
    @Transactional(readOnly = true)
    public SubmissionResponse getSubmission(UUID submissionId) {
        Submission submission = submissionRepository.findById(submissionId)
                .orElseThrow(() -> new IllegalArgumentException("Submission not found"));

        SubmissionResponse.SubmissionResponseBuilder builder = SubmissionResponse.builder()
                .id(submission.getId())
                .problemId(submission.getProblemId())
                .languageId(submission.getLanguageId())
                .status(submission.getStatus())
                .createdAt(submission.getCreatedAt());

        // Add result details if available
        submissionResultRepository.findById(submissionId).ifPresent(result -> {
            builder.executionTimeMs(result.getExecutionTimeMs())
                    .memoryUsedMb(result.getMemoryUsedMb())
                    .passedTestCases(result.getPassedTestCases())
                    .totalTestCases(result.getTotalTestCases())
                    .stdout(result.getStdout())
                    .stderr(result.getStderr());
        });

        return builder.build();
    }
}
