package com.codex.platform.monitoring.service;

import com.codex.platform.execution.service.ExecutionService;
import com.codex.platform.queue.service.QueueService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class MonitoringService {

    private final QueueService queueService;
    private final ExecutionService executionService;

    public Map<String, Object> getPlatformStats() {
        Map<String, Object> stats = new HashMap<>();

        long total = executionService.getTotalSubmissions();
        long success = executionService.getSuccessfulExecutions();
        long failed = executionService.getFailedExecutions();
        long cumulativeTime = executionService.getCumulativeExecutionTimeMs();

        stats.put("queueDepth", queueService.getQueueDepth());
        stats.put("totalSubmissions", total);
        stats.put("successfulExecutions", success);
        stats.put("failedExecutions", failed);
        stats.put("averageExecutionTimeMs", total > 0 ? (double) cumulativeTime / total : 0.0);

        return stats;
    }
}
