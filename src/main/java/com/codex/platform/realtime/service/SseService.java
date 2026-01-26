package com.codex.platform.realtime.service;

import com.codex.platform.common.enums.SubmissionStatus;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;

@Service
@Slf4j
public class SseService {

    private final Map<UUID, SseEmitter> emitters = new ConcurrentHashMap<>();

    /**
     * Register an emitter for a submission
     */
    public SseEmitter registerEmitter(UUID submissionId) {
        SseEmitter emitter = new SseEmitter(5 * 60 * 1000L); // 5 minute timeout

        emitter.onCompletion(() -> {
            emitters.remove(submissionId);
            log.info("Emitter completed for submission: {}", submissionId);
        });

        emitter.onTimeout(() -> {
            emitters.remove(submissionId);
            log.info("Emitter timeout for submission: {}", submissionId);
        });

        emitter.onError(e -> {
            emitters.remove(submissionId);
            log.error("Emitter error for submission: {}", submissionId, e);
        });

        emitters.put(submissionId, emitter);
        log.info("Registered emitter for submission: {}", submissionId);

        return emitter;
    }

    /**
     * Send an event to a submission's subscribers
     */
    public void sendEvent(UUID submissionId, SubmissionStatus status) {
        SseEmitter emitter = emitters.get(submissionId);

        if (emitter != null) {
            try {
                emitter.send(SseEmitter.event()
                        .name("status")
                        .data(status.toString()));

                log.info("Sent SSE event: {} for submission: {}", status, submissionId);

                // Complete emitter if terminal status
                if (isTerminalStatus(status)) {
                    emitter.complete();
                    emitters.remove(submissionId);
                }

            } catch (IOException e) {
                log.error("Error sending SSE event for submission: {}", submissionId, e);
                emitters.remove(submissionId);
            }
        }
    }

    private boolean isTerminalStatus(SubmissionStatus status) {
        return status == SubmissionStatus.ACCEPTED ||
                status == SubmissionStatus.WRONG_ANSWER ||
                status == SubmissionStatus.TIME_LIMIT_EXCEEDED ||
                status == SubmissionStatus.RUNTIME_ERROR ||
                status == SubmissionStatus.COMPILATION_ERROR;
    }
}
