package com.codex.platform.realtime.service;

import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.submission.entity.SubmissionResult;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
@RequiredArgsConstructor
@Slf4j
public class SseService {

    private final Map<UUID, List<SseEmitter>> emitters = new ConcurrentHashMap<>();

    /**
     * Injected Spring-managed ObjectMapper (respects all registered modules/serializers).
     * Previously was a raw {@code new ObjectMapper()} which skipped custom configuration.
     */
    private final ObjectMapper objectMapper;

    /**
     * Register an emitter for a submission
     */
    public SseEmitter registerEmitter(UUID submissionId) {
        SseEmitter emitter = new SseEmitter(5 * 60 * 1000L); // 5 minute timeout

        emitter.onCompletion(() -> {
            removeEmitter(submissionId, emitter);
            log.info("Emitter completed for submission: {}", submissionId);
        });

        emitter.onTimeout(() -> {
            removeEmitter(submissionId, emitter);
            log.info("Emitter timeout for submission: {}", submissionId);
        });

        emitter.onError(e -> {
            removeEmitter(submissionId, emitter);
            log.error("Emitter error for submission: {}", submissionId, e);
        });

        emitters.computeIfAbsent(submissionId, id -> new CopyOnWriteArrayList<>()).add(emitter);
        log.info("Registered emitter for submission: {}", submissionId);

        return emitter;
    }

    /**
     * Send a status-only event (used for intermediate statuses like RUNNING)
     */
    public void sendEvent(UUID submissionId, SubmissionStatus status) {
        sendEvent(submissionId, status, null);
    }

    /**
     * Send an event with full result payload as JSON.
     * The frontend receives: { status, stdout, stderr, testsPassed, totalTests, executionTimeMs }
     */
    public void sendEvent(UUID submissionId, SubmissionStatus status, SubmissionResult result) {
        List<SseEmitter> emitterList = emitters.get(submissionId);

        if (emitterList == null || emitterList.isEmpty()) {
            log.debug("No SSE subscribers for submission {}, skipping event dispatch", submissionId);
            return;
        }

        // Build JSON payload
        Map<String, Object> payload = new HashMap<>();
        payload.put("status", Objects.requireNonNull(status, "Submission status is required").toString());

        if (result != null) {
            payload.put("stdout", result.getStdout());
            payload.put("stderr", result.getStderr());
            payload.put("testsPassed", result.getPassedTestCases());
            payload.put("totalTests", result.getTotalTestCases());
            payload.put("executionTimeMs", result.getExecutionTimeMs());
        }

        String json;
        try {
            json = objectMapper.writeValueAsString(payload);
        } catch (Exception e) {
            log.error("Error serializing SSE payload for submission: {}", submissionId, e);
            json = "{\"status\":\"" + status + "\"}";
        }

        for (SseEmitter emitter : emitterList) {
            try {
                emitter.send(SseEmitter.event()
                        .name("status")
                        .data(json));
            } catch (IOException e) {
                log.error("Error sending SSE event for submission: {}", submissionId, e);
                removeEmitter(submissionId, emitter);
            }
        }

        log.info("Sent SSE event: {} for submission: {} to {} client(s)",
                status, submissionId, emitterList.size());

        // Complete emitters if terminal status
        if (isTerminalStatus(status)) {
            for (SseEmitter emitter : emitterList) {
                emitter.complete();
            }
            emitters.remove(submissionId);
        }
    }

    private boolean isTerminalStatus(SubmissionStatus status) {
        return status == SubmissionStatus.ACCEPTED ||
                status == SubmissionStatus.WRONG_ANSWER ||
                status == SubmissionStatus.TIME_LIMIT_EXCEEDED ||
                status == SubmissionStatus.MEMORY_LIMIT_EXCEEDED ||
                status == SubmissionStatus.RUNTIME_ERROR ||
                status == SubmissionStatus.COMPILATION_ERROR;
    }

    private void removeEmitter(UUID submissionId, SseEmitter emitter) {
        List<SseEmitter> emitterList = emitters.get(submissionId);
        if (emitterList == null) {
            return;
        }
        emitterList.remove(emitter);
        if (emitterList.isEmpty()) {
            emitters.remove(submissionId);
        }
    }
}
