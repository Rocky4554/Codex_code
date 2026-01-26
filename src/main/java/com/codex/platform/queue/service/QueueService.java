package com.codex.platform.queue.service;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.redisson.api.RBlockingQueue;
import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
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
     * Enqueue a submission for processing
     */
    public void enqueue(UUID submissionId) {
        RBlockingQueue<UUID> queue = redissonClient.getBlockingQueue(QUEUE_NAME);
        queue.offer(submissionId);
        log.info("Enqueued submission: {}", submissionId);
    }

    /**
     * Dequeue a submission (blocking operation)
     */
    public UUID dequeue() throws InterruptedException {
        RBlockingQueue<UUID> queue = redissonClient.getBlockingQueue(QUEUE_NAME);
        return queue.take(); // Blocks until an item is available
    }

    /**
     * Acquire a lock for a submission
     * Returns null if lock cannot be acquired
     */
    public RLock acquireLock(UUID submissionId) {
        String lockKey = LOCK_PREFIX + submissionId;
        RLock lock = redissonClient.getLock(lockKey);

        try {
            // Try to acquire lock with 10 second wait time and 5 minute lease time
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
            log.error("Interrupted while acquiring lock for submission: {}", submissionId);
            return null;
        }
    }

    /**
     * Release a lock
     */
    public void releaseLock(RLock lock) {
        if (lock != null && lock.isHeldByCurrentThread()) {
            lock.unlock();
            log.info("Released lock");
        }
    }
}
