package com.codex.platform.execution.client;

import com.codex.platform.execution.client.dto.ExecuteRequest;
import com.codex.platform.execution.client.dto.ExecuteResponse;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientResponseException;

import java.time.Duration;

/**
 * HTTP client for the EC2-hosted executor agent.
 *
 * <p>Used only when {@code execution.mode=remote}. The {@link ExecutionService}
 * branches on the mode flag and calls {@link #execute(ExecuteRequest)} instead
 * of driving {@code DockerExecutor} locally.
 *
 * <p><b>Failure modes</b> — if the agent is unreachable, slow, or returns 5xx,
 * this method throws {@link ExecutorAgentException}. {@code ExecutionService}
 * catches it and marks the submission as {@code RUNTIME_ERROR} with a clear
 * "executor unavailable" stderr so the user gets a useful error rather than
 * a silent hang.
 *
 * <p><b>Retry policy</b> — single retry on connection failure / read timeout.
 * The agent's idempotency cache (keyed on {@code submissionId}) makes the
 * retry safe: if the first call actually executed but we never saw the
 * response, the second call returns the cached result instead of re-running.
 */
@Component
@Slf4j
public class ExecutorAgentClient {

    private final String baseUrl;
    private final String token;
    private final int timeoutMs;

    private RestClient restClient;

    public ExecutorAgentClient(
            @Value("${executor.agent.base-url:}") String baseUrl,
            @Value("${executor.agent.token:}") String token,
            @Value("${executor.agent.timeout-ms:90000}") int timeoutMs) {
        this.baseUrl = baseUrl;
        this.token = token;
        this.timeoutMs = timeoutMs;
    }

    @PostConstruct
    void init() {
        if (baseUrl == null || baseUrl.isBlank()) {
            log.info("ExecutorAgentClient: executor.agent.base-url not set; remote-mode calls will fail until configured");
            return;
        }

        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout((int) Duration.ofSeconds(5).toMillis());
        factory.setReadTimeout(timeoutMs);

        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(factory)
                .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, "application/json")
                .build();

        log.info("ExecutorAgentClient initialized: baseUrl={}, timeoutMs={}", baseUrl, timeoutMs);
    }

    /** Submit a job to the agent. Retries once on transient failure. */
    public ExecuteResponse execute(ExecuteRequest request) {
        if (restClient == null) {
            throw new ExecutorAgentException("ExecutorAgentClient not configured (executor.agent.base-url empty)");
        }

        try {
            return doExecute(request);
        } catch (ResourceAccessException firstAttemptIo) {
            // Connection refused / read timeout / DNS failure — retry once.
            log.warn("Executor agent call failed ({}), retrying once", firstAttemptIo.getMessage());
            try {
                return doExecute(request);
            } catch (Exception retryError) {
                throw new ExecutorAgentException(
                        "Executor agent unreachable after retry: " + retryError.getMessage(), retryError);
            }
        } catch (RestClientResponseException httpError) {
            int status = httpError.getStatusCode().value();
            if (status == 503 || status == 502 || status == 504) {
                // Server-side transient — single retry
                log.warn("Executor agent returned {} ({}), retrying once", status, httpError.getMessage());
                try {
                    return doExecute(request);
                } catch (Exception retryError) {
                    throw new ExecutorAgentException(
                            "Executor agent transient error after retry: " + retryError.getMessage(), retryError);
                }
            }
            throw new ExecutorAgentException(
                    "Executor agent returned " + status + ": " + httpError.getResponseBodyAsString(), httpError);
        } catch (Exception other) {
            throw new ExecutorAgentException("Executor agent call failed: " + other.getMessage(), other);
        }
    }

    private ExecuteResponse doExecute(ExecuteRequest request) {
        return restClient.post()
                .uri("/v1/execute")
                .body(request)
                .retrieve()
                .body(ExecuteResponse.class);
    }

    public static class ExecutorAgentException extends RuntimeException {
        public ExecutorAgentException(String message) {
            super(message);
        }

        public ExecutorAgentException(String message, Throwable cause) {
            super(message, cause);
        }
    }
}
