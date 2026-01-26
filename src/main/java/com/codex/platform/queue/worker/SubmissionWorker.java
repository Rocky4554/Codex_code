package com.codex.platform.queue.worker;

import com.codex.platform.execution.service.ExecutionService;
import com.codex.platform.queue.service.QueueService;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RLock;
import org.springframework.stereotype.Component;

import java.util.UUID;

@Component
@RequiredArgsConstructor
@Slf4j
public class SubmissionWorker {

    private final QueueService queueService;
    private final ExecutionService executionService;

    /**
     * Start worker on application startup
     * This runs in a separate thread and continuously processes submissions
     */
    @PostConstruct
    public void start() {
        Thread workerThread = new Thread(() -> {
            log.info("Submission worker started");

            while (!Thread.currentThread().isInterrupted()) {
                RLock lock = null;
                UUID submissionId = null;

                try {
                    // Dequeue submission (blocking operation)
                    submissionId = queueService.dequeue();
                    log.info("Dequeued submission: {}", submissionId);

                    // Acquire Redis lock
                    lock = queueService.acquireLock(submissionId);

                    if (lock != null) {
                        // Process submission
                        executionService.executeSubmission(submissionId);
                    } else {
                        log.warn("Could not acquire lock for submission: {}, skipping", submissionId);
                    }

                } catch (InterruptedException e) {
                    log.info("Worker interrupted, shutting down");
                    Thread.currentThread().interrupt();
                    break;
                } catch (Exception e) {
                    log.error("Error processing submission: {}", submissionId, e);
                } finally {
                    // Always release lock
                    if (lock != null) {
                        queueService.releaseLock(lock);
                    }
                }
            }

            log.info("Submission worker stopped");
        });

        workerThread.setName("submission-worker");
        workerThread.setDaemon(false); // Keep JVM alive
        workerThread.start();
    }
}
