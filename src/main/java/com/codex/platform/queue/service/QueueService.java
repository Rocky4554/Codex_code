package com.codex.platform.queue.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RBlockingQueue;
import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
import org.redisson.client.codec.StringCodec;
import org.springframework.stereotype.Service;

import java.util.UUID;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
@Slf4j
public class QueueService {

    private final RedissonClient redissonClient;
    private static final String QUEUE_NAME = "submission-queue";
    private static final String LOCK_PREFIX = "submission:";

    /**
     * Adaptive backoff: poll quickly when recently active, slow down when idle.
     * - Active  : 300 ms  (fast pickup after submission)
     * - Idle    : 3000 ms (after 5 consecutive empty polls, save Redis quota)
     */
    private static final long POLL_FAST_MS = 300;
    private static final long POLL_IDLE_MS = 3_000;
    private static final int  IDLE_THRESHOLD = 5;   // empty polls before switching to slow mode

    /**
     * Get a String-typed queue reference backed by raw bytes (no JSON wrapping).
     *
     * <p>Using {@link StringCodec#INSTANCE} instead of the global
     * {@code JsonJacksonCodec} avoids a subtle type-erasure bug: JsonJacksonCodec
     * stores a Java String as {@code "value"} (JSON-quoted), but when Redisson
     * deserialises it from a generic {@code RBlockingQueue<String>} at runtime the
     * type token is lost and Jackson returns {@code null}.  StringCodec stores the
     * UUID string as raw UTF-8 bytes and round-trips it perfectly.
     */
    private RBlockingQueue<String> queue() {
        return redissonClient.getBlockingQueue(QUEUE_NAME, StringCodec.INSTANCE);
    }

    /**
     * Enqueue a submission for processing.
     */
    public void enqueue(UUID submissionId) {
        RBlockingQueue<String> q = queue();
        boolean offered = q.offer(submissionId.toString());
        log.info("Enqueued submission: {} (offered={}, queue depth={})",
                submissionId, offered, q.size());
        if (!offered) {
            log.error("Queue rejected submission {} — possible capacity issue!", submissionId);
            throw new IllegalStateException("Queue rejected submission " + submissionId + " — enqueue failed");
        }
    }

    /**
     * Non-blocking poll with adaptive back-off to protect Upstash quota.
     *
     * <p>Returns the next submission UUID immediately if one is available,
     * otherwise sleeps and returns {@code null} — the worker loop will call
     * this again on its next iteration.
     *
     * <p><b>Back-off strategy:</b>
     * <ul>
     *   <li>Hit: reset empty-count, no sleep (process immediately)</li>
     *   <li>Miss × 1–{@value #IDLE_THRESHOLD}: sleep {@value #POLL_FAST_MS} ms</li>
     *   <li>Miss > {@value #IDLE_THRESHOLD}: sleep {@value #POLL_IDLE_MS} ms (idle mode)</li>
     * </ul>
     *
     * @param emptyPollCount consecutive empty polls so far (passed in by the worker)
     * @return the next UUID, or {@code null} if the queue was empty
     */
    public UUID dequeue(int emptyPollCount) throws InterruptedException {
        RBlockingQueue<String> q = queue();
        log.trace("Queue poll: depth={}", q.size());

        try {
            String raw = q.poll(); // non-blocking LPOP
            if (raw != null && !raw.isBlank()) {
                UUID result = UUID.fromString(raw.trim());
                log.info("Queue hit: {} dequeued", result);
                return result;
            }

            // Queue empty — back off proportionally to avoid hammering Redis
            long sleepMs = (emptyPollCount >= IDLE_THRESHOLD) ? POLL_IDLE_MS : POLL_FAST_MS;
            log.trace("Queue empty (emptyPolls={}), sleeping {}ms", emptyPollCount, sleepMs);
            Thread.sleep(sleepMs);
            return null;

        } catch (IllegalArgumentException badUuid) {
            log.error("Queue contained invalid UUID '{}' — discarding", badUuid.getMessage());
            return null;
        } catch (InterruptedException ie) {
            throw ie;
        } catch (Exception e) {
            log.warn("Queue poll failed: {} — backing off {}ms", e.getMessage(), POLL_IDLE_MS);
            Thread.sleep(POLL_IDLE_MS);
            return null;
        }
    }

    /**
     * Acquire a distributed lock for a submission.
     * Returns null if lock cannot be acquired.
     */
    public RLock acquireLock(UUID submissionId) {
        String lockKey = LOCK_PREFIX + submissionId;
        RLock lock = redissonClient.getLock(lockKey);
        try {
            boolean acquired = lock.tryLock(10, 300, TimeUnit.SECONDS);
            if (acquired) {
                log.info("Acquired lock for submission: {}", submissionId);
                return lock;
            } else {
                log.warn("Could not acquire lock for submission: {}", submissionId);
                return null;
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            log.error("Interrupted while acquiring lock for: {}", submissionId);
            return null;
        }
    }

    /**
     * Release a distributed lock.
     */
    public void releaseLock(RLock lock) {
        if (lock != null && lock.isHeldByCurrentThread()) {
            lock.unlock();
            log.debug("Released lock");
        }
    }

    /**
     * Current queue depth — useful for health checks.
     */
    public int getQueueDepth() {
        return queue().size();
    }
}
