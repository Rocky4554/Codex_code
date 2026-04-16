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

    // BLPOP timeout — blocks server-side, wakes up every 5s to check thread interruption
    private static final long BLPOP_TIMEOUT_SEC = 5;

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
     * BLPOP — blocks server-side until item arrives or timeout expires.
     * No busy-loop, no missed items on latency spikes.
     * Returns UUID or null if timeout elapsed with no item.
     */
    public UUID dequeue() throws InterruptedException {
        RBlockingQueue<String> q = queue();
        try {
            String raw = q.poll(BLPOP_TIMEOUT_SEC, TimeUnit.SECONDS);
            if (raw != null && !raw.isBlank()) {
                UUID result = UUID.fromString(raw.trim());
                log.info("Queue hit: {} dequeued", result);
                return result;
            }
            return null;
        } catch (IllegalArgumentException badUuid) {
            log.error("Queue contained invalid UUID '{}' — discarding", badUuid.getMessage());
            return null;
        } catch (InterruptedException ie) {
            throw ie;
        } catch (Exception e) {
            log.warn("Queue BLPOP failed: {} — backing off 5s", e.getMessage());
            Thread.sleep(5_000);
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
