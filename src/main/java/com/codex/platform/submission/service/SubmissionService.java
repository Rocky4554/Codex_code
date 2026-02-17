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
import com.codex.platform.submission.repository.SubmissionRepository;
import com.codex.platform.submission.repository.SubmissionResultRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RRateLimiter;
import org.redisson.api.RateIntervalUnit;
import org.redisson.api.RateType;
import org.redisson.api.RedissonClient;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronization;
import org.springframework.transaction.support.TransactionSynchronizationManager;

import java.util.Objects;
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
    private final RedissonClient redissonClient;

    @Transactional
    public SubmitCodeResponse submitCode(SubmitCodeRequest request, HttpServletRequest httpRequest) {
        // Extract userId from SecurityContext (set by JwtAuthenticationFilter)
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();

        // Rate Limiting: 5 submissions per minute per user
        String rateLimitKey = "rate_limit:submission:" + userId;
        RRateLimiter rateLimiter = redissonClient.getRateLimiter(rateLimitKey);
        // Initialize rate limiter if not exists: 5 permits per 1 minute
        rateLimiter.trySetRate(RateType.OVERALL, 5, 1, RateIntervalUnit.MINUTES);

        if (!rateLimiter.tryAcquire()) {
            log.warn("Rate limit exceeded for user: {}", userId);
            throw new ResponseStatusException(HttpStatus.TOO_MANY_REQUESTS,
                    "Submission rate limit exceeded. Please try again later.");
        }

        UUID problemId = Objects.requireNonNull(request.getProblemId(), "Problem ID is required");
        UUID languageId = Objects.requireNonNull(request.getLanguageId(), "Language ID is required");

        // Validate problem exists
        if (!problemRepository.existsById(problemId)) {
            throw new IllegalArgumentException("Problem not found");
        }

        // Validate language exists
        if (!languageRepository.existsById(languageId)) {
            throw new IllegalArgumentException("Language not found");
        }

        // Create submission
        Submission submission = new Submission();
        submission.setUserId(userId);
        submission.setProblemId(problemId);
        submission.setLanguageId(languageId);
        submission.setSourceCode(request.getSourceCode());
        submission.setStatus(SubmissionStatus.QUEUED);

        Submission savedSubmission = submissionRepository.save(submission);

        // Enqueue for processing ONLY AFTER the transaction commits
        final UUID submissionId = savedSubmission.getId();
        TransactionSynchronizationManager.registerSynchronization(new TransactionSynchronization() {
            @Override
            public void afterCommit() {
                int maxRetries = 3;
                for (int attempt = 1; attempt <= maxRetries; attempt++) {
                    try {
                        queueService.enqueue(submissionId);
                        log.info("Submission enqueued after commit: {}", submissionId);
                        return;
                    } catch (Exception e) {
                        log.error("Failed to enqueue submission {} (attempt {}/{}): {}",
                                submissionId, attempt, maxRetries, e.getMessage());
                        if (attempt < maxRetries) {
                            try {
                                Thread.sleep(1000L * attempt);
                            } catch (InterruptedException ie) {
                                Thread.currentThread().interrupt();
                                break;
                            }
                        }
                    }
                }
                log.error("Submission {} could not be enqueued after retries. Manual intervention may be required.",
                        submissionId);
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
        UUID currentUserId = JwtAuthenticationFilter.getCurrentUserId();
        Submission submission = submissionRepository
                .findById(Objects.requireNonNull(submissionId, "Submission ID is required"))
                .orElseThrow(() -> new IllegalArgumentException("Submission not found"));

        if (!submission.getUserId().equals(currentUserId)) {
            throw new org.springframework.security.access.AccessDeniedException(
                    "You are not authorized to view this submission");
        }

        SubmissionResponse.SubmissionResponseBuilder builder = SubmissionResponse.builder()
                .id(submission.getId())
                .userId(submission.getUserId())
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

    @Transactional(readOnly = true)
    public void validateSubmissionOwnership(UUID submissionId) {
        UUID currentUserId = JwtAuthenticationFilter.getCurrentUserId();
        Submission submission = submissionRepository
                .findById(Objects.requireNonNull(submissionId, "Submission ID is required"))
                .orElseThrow(() -> new IllegalArgumentException("Submission not found"));

        if (!submission.getUserId().equals(currentUserId)) {
            throw new org.springframework.security.access.AccessDeniedException(
                    "You are not authorized to access this submission");
        }
    }
}
