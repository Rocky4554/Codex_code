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

    @Value("${execution.worker-count:1}")
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

                while (!Thread.currentThread().isInterrupted()) {
                    RLock lock = null;
                    UUID submissionId = null;

                    try {
                        // BLPOP — blocks up to 5s server-side, returns null on timeout
                        submissionId = queueService.dequeue();
                        if (submissionId == null) continue;

                        log.info("Worker-{} dequeued: {}", workerId, submissionId);

                        // Acquire distributed lock to prevent duplicate processing
                        lock = queueService.acquireLock(submissionId);
                        if (lock != null) {
                            log.info("Worker-{} starting execution for {}", workerId, submissionId);
                            executionService.executeSubmission(submissionId);
                            log.info("Worker-{} finished execution for {}", workerId, submissionId);
                        } else {
                            log.warn("Worker-{} could not acquire lock for {}, re-queuing", workerId, submissionId);
                            queueService.enqueue(submissionId);
                        }

                    } catch (InterruptedException e) {
                        log.info("Worker-{} interrupted, shutting down", workerId);
                        Thread.currentThread().interrupt();
                        break;
                    } catch (Throwable t) {
                        log.error("CRITICAL: Worker-{} unhandled error for {}: {}",
                                workerId, submissionId, t.getMessage(), t);
                        try { Thread.sleep(5_000); } catch (InterruptedException ie) {
                            Thread.currentThread().interrupt();
                            break;
                        }
                    } finally {
                        if (lock != null) {
                            try { queueService.releaseLock(lock); }
                            catch (Exception e) { log.debug("Lock release failed: {}", e.getMessage()); }
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
