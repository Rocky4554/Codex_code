package com.codex.platform.realtime.controller;

import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import com.codex.platform.realtime.service.SseService;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.repository.SubmissionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.Objects;
import java.util.UUID;

@RestController
@RequestMapping("/api/submissions")
@RequiredArgsConstructor
public class SseController {

    private final SseService sseService;
    private final SubmissionRepository submissionRepository;

    @GetMapping(value = "/{id}/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamEvents(@PathVariable UUID id) {
        UUID currentUserId = JwtAuthenticationFilter.getCurrentUserId();
        Submission submission = submissionRepository.findById(Objects.requireNonNull(id, "Submission ID is required"))
                .orElseThrow(() -> new IllegalArgumentException("Submission not found"));
        if (!submission.getUserId().equals(currentUserId)) {
            throw new AccessDeniedException("You are not authorized to view this submission events");
        }
        
        // Register emitter and immediately send current status if submission is already complete
        SseEmitter emitter = sseService.registerEmitter(id);
        
        // If submission already has a terminal status, send it immediately
        if (submission.getStatus() != null && isTerminalStatus(submission.getStatus())) {
            sseService.sendEvent(id, submission.getStatus());
        }
        
        return emitter;
    }
    
    private boolean isTerminalStatus(com.codex.platform.common.enums.SubmissionStatus status) {
        return status == com.codex.platform.common.enums.SubmissionStatus.ACCEPTED ||
                status == com.codex.platform.common.enums.SubmissionStatus.WRONG_ANSWER ||
                status == com.codex.platform.common.enums.SubmissionStatus.TIME_LIMIT_EXCEEDED ||
                status == com.codex.platform.common.enums.SubmissionStatus.MEMORY_LIMIT_EXCEEDED ||
                status == com.codex.platform.common.enums.SubmissionStatus.RUNTIME_ERROR ||
                status == com.codex.platform.common.enums.SubmissionStatus.COMPILATION_ERROR;
    }
}
