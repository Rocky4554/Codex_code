package com.codex.platform.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.concurrent.ThreadPoolTaskExecutor;

import java.util.concurrent.Executor;

/**
 * Enables Spring @Async and configures a dedicated thread pool for
 * background submission result persistence.
 *
 * <p>The {@code submissionPersistExecutor} is intentionally small — DB writes
 * are sequential and infrequent. Using a dedicated pool avoids starving the
 * default async executor used by other parts of the application.
 */
@Configuration
@EnableAsync
public class AsyncConfig {

    @Value("${submission.persist.executor.core-size:2}")
    private int corePoolSize;

    @Value("${submission.persist.executor.max-size:4}")
    private int maxPoolSize;

    @Value("${submission.persist.executor.queue-capacity:100}")
    private int queueCapacity;

    @Bean(name = "submissionPersistExecutor")
    public Executor submissionPersistExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(corePoolSize);
        executor.setMaxPoolSize(maxPoolSize);
        executor.setQueueCapacity(queueCapacity);
        executor.setThreadNamePrefix("sub-persist-");
        executor.setWaitForTasksToCompleteOnShutdown(true);
        executor.setAwaitTerminationSeconds(30);
        executor.initialize();
        return executor;
    }
}
