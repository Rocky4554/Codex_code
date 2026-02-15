package com.codex.platform.queue.worker;

import com.codex.platform.execution.service.ExecutionService;
import com.codex.platform.queue.service.QueueService;
import jakarta.annotation.PostConstruct;
import jakarta.annotation.PreDestroy;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RLock;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

@Component
@RequiredArgsConstructor
@Slf4j
public class SubmissionWorker {

    private final QueueService queueService;
    private final ExecutionService executionService;
    private final List<Thread> workerThreads = new ArrayList<>();

    @Value("${execution.worker-count:2}")
    private int workerCount;

    /**
     * Start workers on application startup
     */
    @PostConstruct
    public void start() {
        for (int w = 0; w < workerCount; w++) {
            final int workerId = w + 1;
            Thread workerThread = new Thread(() -> {
                log.info("Submission worker-{} started", workerId);

                int consecutiveErrors = 0;

                while (!Thread.currentThread().isInterrupted()) {
                    RLock lock = null;
                    UUID submissionId = null;

                    try {
                        // Dequeue submission (blocking operation)
                        submissionId = queueService.dequeue();
                        consecutiveErrors = 0; // reset on successful dequeue
                        log.info("Worker-{} dequeued submission: {}", workerId, submissionId);

                        // Acquire Redis lock
                        lock = queueService.acquireLock(submissionId);

                        if (lock != null) {
                            // Process submission
                            executionService.executeSubmission(submissionId);
                        } else {
                            log.warn("Worker-{} could not acquire lock for submission: {}, skipping", workerId,
                                    submissionId);
                            queueService.enqueue(submissionId);
                            log.info("Worker-{} re-enqueued submission after lock miss: {}", workerId, submissionId);
                        }

                    } catch (InterruptedException e) {
                        log.info("Worker-{} interrupted, shutting down", workerId);
                        Thread.currentThread().interrupt();
                        break;
                    } catch (Exception e) {
                        log.error("Worker-{} error processing submission: {}", workerId, submissionId, e);

                        // Backoff on Redis / infrastructure errors to avoid tight error loops
                        try {
                            consecutiveErrors++;
                            long backoffMs = Math.min(5_000L * consecutiveErrors, 30_000L);
                            log.warn("Worker-{} backing off for {}ms after {} consecutive error(s)",
                                    workerId, backoffMs, consecutiveErrors);
                            Thread.sleep(backoffMs);
                        } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                            break;
                        }
                        continue;
                    } finally {
                        // Always release lock
                        if (lock != null) {
                            try {
                                queueService.releaseLock(lock);
                            } catch (Exception e) {
                                log.debug("Could not release lock (may already be released): {}", e.getMessage());
                            }
                        }
                    }
                }

                log.info("Submission worker-{} stopped", workerId);
            });

            workerThread.setName("submission-worker-" + workerId);
            workerThread.setDaemon(true);
            workerThread.start();
            workerThreads.add(workerThread);
        }

        log.info("Started {} submission workers", workerCount);
    }

    /**
     * Gracefully stop all workers on application shutdown
     */
    @PreDestroy
    public void stop() {
        log.info("Shutting down {} submission workers...", workerThreads.size());

        // Interrupt all worker threads
        for (Thread thread : workerThreads) {
            thread.interrupt();
        }

        // Wait for all threads to finish (max 10 seconds)
        for (Thread thread : workerThreads) {
            try {
                thread.join(10_000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }

        log.info("All submission workers stopped");
    }
}
