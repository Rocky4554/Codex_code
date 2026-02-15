package com.codex.platform.realtime.service;

import com.codex.platform.common.enums.SubmissionStatus;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
@Slf4j
public class SseService {

    private final Map<UUID, List<SseEmitter>> emitters = new ConcurrentHashMap<>();

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
     * Send an event to a submission's subscribers
     */
    public void sendEvent(UUID submissionId, SubmissionStatus status) {
        List<SseEmitter> emitterList = emitters.get(submissionId);

        if (emitterList == null || emitterList.isEmpty()) {
            return;
        }

        for (SseEmitter emitter : emitterList) {
            try {
                String payload = Objects.requireNonNull(status, "Submission status is required").toString();
                emitter.send(SseEmitter.event()
                        .name("status")
                        .data(Objects.requireNonNull((Object) payload)));
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
