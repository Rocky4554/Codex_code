package com.codex.platform.submission.service;

import com.codex.platform.auth.util.JwtUtil;
import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.execution.repository.LanguageRepository;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.queue.service.QueueService;
import com.codex.platform.submission.dto.SubmitCodeRequest;
import com.codex.platform.submission.dto.SubmitCodeResponse;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.repository.SubmissionRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class SubmissionService {

    private final SubmissionRepository submissionRepository;
    private final ProblemRepository problemRepository;
    private final LanguageRepository languageRepository;
    private final QueueService queueService;
    private final JwtUtil jwtUtil;

    @Transactional
    public SubmitCodeResponse submitCode(SubmitCodeRequest request, HttpServletRequest httpRequest) {
        // Extract userId from JWT
        UUID userId = extractUserIdFromRequest(httpRequest);

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

        // Enqueue for processing
        queueService.enqueue(savedSubmission.getId());

        log.info("Submission created and queued: {}", savedSubmission.getId());

        return new SubmitCodeResponse(
                savedSubmission.getId(),
                SubmissionStatus.QUEUED,
                "Submission queued for execution");
    }

    private UUID extractUserIdFromRequest(HttpServletRequest request) {
        String authHeader = request.getHeader("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            return jwtUtil.extractUserId(token);
        }
        throw new IllegalArgumentException("Invalid authorization header");
    }
}
