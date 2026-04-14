package com.codex.platform.realtime.controller;

import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.realtime.service.SseService;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.repository.SubmissionRepository;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.transaction.annotation.Transactional;
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
@Slf4j
public class SseController {

    private final SseService sseService;
    private final SubmissionRepository submissionRepository;

    @GetMapping(value = "/{id}/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    @Transactional(readOnly = true)
    public SseEmitter streamEvents(@PathVariable UUID id, HttpServletResponse response) {
        // Disable proxy/nginx buffering so each SSE event is flushed immediately
        response.setHeader("X-Accel-Buffering", "no");
        response.setHeader("Cache-Control", "no-cache");
        response.setHeader("Connection", "keep-alive");

        UUID currentUserId = JwtAuthenticationFilter.getCurrentUserId();

        // ---- All DB work happens here and finishes before the SSE stream opens ----
        Submission submission = submissionRepository
                .findById(Objects.requireNonNull(id, "Submission ID is required"))
                .orElseThrow(() -> new IllegalArgumentException("Submission not found"));
        if (!submission.getUserId().equals(currentUserId)) {
            throw new AccessDeniedException("You are not authorized to view this submission events");
        }

        // Capture the current status before releasing the DB connection
        SubmissionStatus currentStatus = submission.getStatus();
        // ---- End of DB work ----

        // Register emitter FIRST — before checking status — so the worker can never
        // complete and call sendEvent() into an empty map between these two operations.
        SseEmitter emitter = sseService.registerEmitter(id);

        if (currentStatus != null && isTerminalStatus(currentStatus)) {
            log.info("Submission {} already terminal ({}); scheduling immediate SSE push", id, currentStatus);

            // Send on a separate thread so Spring MVC has time to initialize
            // the emitter with the actual response writer before we write to it.
            Thread t = new Thread(() -> {
                try {
                    Thread.sleep(50);
                    sseService.sendEvent(id, currentStatus);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } catch (Exception e) {
                    log.error("Failed to push terminal status {} for submission {}", currentStatus, id, e);
                }
            });
            t.setDaemon(true);
            t.setName("sse-push-" + id);
            t.start();
        }

        return emitter;
    }

    private boolean isTerminalStatus(SubmissionStatus status) {
        return status == SubmissionStatus.ACCEPTED ||
                status == SubmissionStatus.WRONG_ANSWER ||
                status == SubmissionStatus.TIME_LIMIT_EXCEEDED ||
                status == SubmissionStatus.MEMORY_LIMIT_EXCEEDED ||
                status == SubmissionStatus.RUNTIME_ERROR ||
                status == SubmissionStatus.COMPILATION_ERROR;
    }
}
