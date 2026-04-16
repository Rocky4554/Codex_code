package com.codex.platform.execution.service;

import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.common.util.OutputNormalizer;
import com.codex.platform.execution.client.ExecutorAgentClient;
import com.codex.platform.execution.client.dto.ExecuteRequest;
import com.codex.platform.execution.client.dto.ExecuteResponse;
import com.codex.platform.execution.dto.ExecutionResult;
import com.codex.platform.execution.entity.Language;
import com.codex.platform.execution.repository.LanguageRepository;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.TestCase;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.problem.repository.TestCaseRepository;
import com.codex.platform.realtime.service.SseService;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.entity.SubmissionResult;
import com.codex.platform.submission.repository.SubmissionRepository;
import com.codex.platform.submission.service.AsyncResultPersister;
import com.codex.platform.submission.service.SubmissionCacheService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.file.Path;
import java.util.List;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicLong;

@Service
@RequiredArgsConstructor
@Slf4j
public class ExecutionService {

    private final SubmissionRepository submissionRepository;
    private final ProblemRepository problemRepository;
    private final TestCaseRepository testCaseRepository;
    private final LanguageRepository languageRepository;
    private final DockerExecutor dockerExecutor;
    private final ExecutorAgentClient executorAgentClient;
    private final SseService sseService;
    private final SubmissionCacheService cacheService;
    private final AsyncResultPersister asyncResultPersister;

    /**
     * "local"  → drive DockerExecutor on the same machine (legacy path).
     * "remote" → POST to the executor agent on EC2 over HTTPS.
     * Default is "local" so deployments without the new env var keep working.
     */
    @Value("${execution.mode:local}")
    private String executionMode;

    // Metrics
    private final AtomicLong totalSubmissions = new AtomicLong(0);
    private final AtomicLong successfulExecutions = new AtomicLong(0);
    private final AtomicLong failedExecutions = new AtomicLong(0);
    private final AtomicLong cumulativeExecutionTimeMs = new AtomicLong(0);

    /**
     * Main entry point for executing a submission.
     *
     * <p>Both execution branches (local / remote) follow the Redis-first pattern:
     * <ol>
     *   <li>Cache result in Redis  (< 1 ms)</li>
     *   <li>Fire SSE event          (client sees verdict immediately)</li>
     *   <li>Persist to DB async    (background thread)</li>
     * </ol>
     *
     * <p>Marked {@code @Transactional} so the RUNNING status save and subsequent
     * reads happen within a single session — avoids detached-entity errors when
     * the worker thread calls JPA repositories directly.
     */
    @Transactional
    public void executeSubmission(UUID submissionId) {
        log.info("Starting execution for submission: {} (mode={})", submissionId, executionMode);
        totalSubmissions.incrementAndGet();

        try {
            // Load submission
            Submission submission = submissionRepository
                    .findById(Objects.requireNonNull(submissionId, "Submission ID is required"))
                    .orElseThrow(() -> new IllegalArgumentException("Submission not found: " + submissionId));

            // Immediately broadcast RUNNING so the UI shows a spinner
            submission.setStatus(SubmissionStatus.RUNNING);
            submissionRepository.save(submission);
            sseService.sendEvent(submissionId, SubmissionStatus.RUNNING);
            log.info("Submission {} marked RUNNING and SSE event fired", submissionId);

            // Load problem, language, and test cases
            Problem problem = problemRepository
                    .findById(Objects.requireNonNull(submission.getProblemId(), "Problem ID is required"))
                    .orElseThrow(() -> new IllegalArgumentException("Problem not found"));

            Language language = languageRepository
                    .findById(Objects.requireNonNull(submission.getLanguageId(), "Language ID is required"))
                    .orElseThrow(() -> new IllegalArgumentException("Language not found"));

            List<TestCase> testCases = testCaseRepository.findByProblemId(problem.getId());
            if (testCases.isEmpty()) {
                throw new IllegalArgumentException("No test cases found for problem: " + problem.getId());
            }

            log.info("Executing submission {} against {} test case(s) via {} mode",
                    submissionId, testCases.size(), executionMode);

            if ("remote".equalsIgnoreCase(executionMode)) {
                executeRemote(submission, problem, language, testCases);
            } else {
                executeLocal(submission, problem, language, testCases);
            }

        } catch (Exception e) {
            log.error("Error executing submission {}: {}", submissionId, e.getMessage(), e);

            // Cache error status first so SSE / REST both see it immediately
            cacheService.cacheStatus(submissionId, SubmissionStatus.RUNTIME_ERROR);
            sseService.sendEvent(submissionId, SubmissionStatus.RUNTIME_ERROR);

            // Update DB status directly (we are still in the @Transactional context here)
            submissionRepository.findById(Objects.requireNonNull(submissionId))
                    .ifPresent(s -> {
                        s.setStatus(SubmissionStatus.RUNTIME_ERROR);
                        submissionRepository.save(s);
                    });

            failedExecutions.incrementAndGet();
        }
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Local (Docker on same host)
    // ──────────────────────────────────────────────────────────────────────────

    private void executeLocal(Submission submission, Problem problem, Language language, List<TestCase> testCases) {
        UUID submissionId = submission.getId();
        String containerId = null;
        Path tempDir = null;

        try {
            tempDir = dockerExecutor.prepareTempDirectory(
                    submission.getSourceCode(),
                    "solution" + language.getFileExtension());

            containerId = dockerExecutor.createAndStartContainer(
                    language.getDockerImage(),
                    tempDir,
                    problem.getMemoryLimitMb());

            ExecutionResult compileError = dockerExecutor.compileInContainer(
                    containerId,
                    language.getCompileCommand());

            SubmissionStatus finalStatus;
            int passedCount = 0;
            long totalExecutionTime = 0;
            StringBuilder stdoutBuilder = new StringBuilder();
            StringBuilder stderrBuilder = new StringBuilder();

            if (compileError != null) {
                finalStatus = SubmissionStatus.COMPILATION_ERROR;
                stdoutBuilder.append(compileError.getStdout());
                stderrBuilder.append(compileError.getStderr());
                totalExecutionTime = compileError.getExecutionTimeMs();
                log.warn("Compilation failed ({}ms): {}", totalExecutionTime,
                        compileError.getStderr().length() > 200
                                ? compileError.getStderr().substring(0, 200) + "..."
                                : compileError.getStderr());
            } else {
                finalStatus = SubmissionStatus.ACCEPTED;

                int testIndex = 0;
                for (TestCase testCase : testCases) {
                    testIndex++;
                    log.info("Running test case {}/{}: {}", testIndex, testCases.size(), testCase.getId());

                    ExecutionResult result = dockerExecutor.runTestCase(
                            containerId,
                            language.getExecuteCommand(),
                            testCase.getInput(),
                            problem.getTimeLimitMs(),
                            tempDir);

                    totalExecutionTime += result.getExecutionTimeMs();
                    stdoutBuilder.append(result.getStdout()).append("\n");
                    stderrBuilder.append(result.getStderr()).append("\n");

                    if (result.getExitCode() != 0) {
                        if (result.getExitCode() == 137) {
                            log.warn("  -> Test {}/{} MEMORY_LIMIT_EXCEEDED (exit code {}, {}ms)",
                                    testIndex, testCases.size(), result.getExitCode(), result.getExecutionTimeMs());
                            finalStatus = SubmissionStatus.MEMORY_LIMIT_EXCEEDED;
                        } else {
                            log.warn("  -> Test {}/{} RUNTIME_ERROR (exit code {}, {}ms)",
                                    testIndex, testCases.size(), result.getExitCode(), result.getExecutionTimeMs());
                            finalStatus = SubmissionStatus.RUNTIME_ERROR;
                        }
                        break;
                    }

                    if (result.getExecutionTimeMs() > problem.getTimeLimitMs()) {
                        log.warn("  -> Test {}/{} TIME_LIMIT_EXCEEDED ({}ms / limit {}ms)",
                                testIndex, testCases.size(), result.getExecutionTimeMs(), problem.getTimeLimitMs());
                        finalStatus = SubmissionStatus.TIME_LIMIT_EXCEEDED;
                        break;
                    }

                    if (OutputNormalizer.areEqual(testCase.getExpectedOutput(), result.getStdout())) {
                        passedCount++;
                        log.info("  -> Test {}/{} PASSED ({}ms)", testIndex, testCases.size(),
                                result.getExecutionTimeMs());
                    } else {
                        finalStatus = SubmissionStatus.WRONG_ANSWER;
                        log.warn("  -> Test {}/{} WRONG_ANSWER ({}ms)", testIndex, testCases.size(),
                                result.getExecutionTimeMs());
                        break;
                    }
                }
            }

            SubmissionResult submissionResult = new SubmissionResult();
            submissionResult.setSubmissionId(submissionId);
            submissionResult.setExecutionTimeMs(totalExecutionTime);
            submissionResult.setMemoryUsedMb(0L);
            submissionResult.setPassedTestCases(passedCount);
            submissionResult.setTotalTestCases(testCases.size());
            submissionResult.setStdout(stdoutBuilder.toString());
            submissionResult.setStderr(stderrBuilder.toString());

            // ── Redis-first delivery ────────────────────────────────────────
            // 1. Cache to Redis (< 1 ms)
            cacheService.cacheResult(submissionId, finalStatus, submissionResult);
            // 2. Fire SSE — user sees verdict immediately
            sseService.sendEvent(submissionId, finalStatus, submissionResult);
            // 3. Persist to DB asynchronously
            asyncResultPersister.saveAsync(submission, submissionResult, finalStatus);
            // ────────────────────────────────────────────────────────────────

            successfulExecutions.incrementAndGet();
            cumulativeExecutionTimeMs.addAndGet(totalExecutionTime);

            log.info("╔══════════════════════════════════════════════════");
            log.info("║ Submission  : {}", submissionId);
            log.info("║ Verdict     : {} (local)", finalStatus);
            log.info("║ Test Cases  : {}/{} passed", passedCount, testCases.size());
            log.info("║ Time        : {}ms (limit: {}ms)", totalExecutionTime, problem.getTimeLimitMs());
            log.info("╚══════════════════════════════════════════════════");

        } catch (RuntimeException re) {
            throw re;
        } catch (Exception e) {
            throw new RuntimeException("Local execution failed", e);
        } finally {
            dockerExecutor.cleanup(containerId, tempDir);
        }
    }

    // ──────────────────────────────────────────────────────────────────────────
    // Remote (EC2 executor agent)
    // ──────────────────────────────────────────────────────────────────────────

    private void executeRemote(Submission submission, Problem problem, Language language, List<TestCase> testCases) {
        UUID submissionId = submission.getId();

        List<ExecuteRequest.TestCase> wireTestCases = testCases.stream()
                .map(tc -> ExecuteRequest.TestCase.builder()
                        .id(tc.getId().toString())
                        .stdin(tc.getInput())
                        .expectedStdout(tc.getExpectedOutput())
                        .build())
                .toList();

        ExecuteRequest request = ExecuteRequest.builder()
                .submissionId(submissionId)
                .language(language.getName())
                .dockerImage(language.getDockerImage())
                .compileCommand(language.getCompileCommand())
                .executeCommand(language.getExecuteCommand())
                .fileExtension(language.getFileExtension())
                .sourceCode(submission.getSourceCode())
                .compileTimeoutMs(180_000)
                .runTimeoutMs(problem.getTimeLimitMs())
                .memoryLimitMb(problem.getMemoryLimitMb())
                .testCases(wireTestCases)
                .build();

        log.info("Dispatching submission {} to remote executor at {}", submissionId,
                request.getSubmissionId());

        ExecuteResponse response;
        try {
            response = executorAgentClient.execute(request);
        } catch (ExecutorAgentClient.ExecutorAgentException agentError) {
            log.error("Submission {}: executor agent unreachable: {}", submissionId, agentError.getMessage());

            SubmissionResult errorResult = new SubmissionResult();
            errorResult.setSubmissionId(submissionId);
            errorResult.setExecutionTimeMs(0L);
            errorResult.setMemoryUsedMb(0L);
            errorResult.setPassedTestCases(0);
            errorResult.setTotalTestCases(testCases.size());
            errorResult.setStdout("");
            errorResult.setStderr("Executor unavailable: " + agentError.getMessage());

            // Redis-first even on agent error
            cacheService.cacheResult(submissionId, SubmissionStatus.RUNTIME_ERROR, errorResult);
            sseService.sendEvent(submissionId, SubmissionStatus.RUNTIME_ERROR);
            asyncResultPersister.saveAsync(submission, errorResult, SubmissionStatus.RUNTIME_ERROR);

            failedExecutions.incrementAndGet();
            return;
        }

        // Map agent string status to our enum, defaulting safely
        SubmissionStatus finalStatus;
        try {
            finalStatus = SubmissionStatus.valueOf(response.getStatus());
        } catch (IllegalArgumentException unknown) {
            log.warn("Submission {}: agent returned unknown status '{}', mapping to RUNTIME_ERROR",
                    submissionId, response.getStatus());
            finalStatus = SubmissionStatus.RUNTIME_ERROR;
        }

        SubmissionResult submissionResult = new SubmissionResult();
        submissionResult.setSubmissionId(submissionId);
        submissionResult.setExecutionTimeMs(response.getCompileTimeMs() + response.getTotalExecTimeMs());
        submissionResult.setMemoryUsedMb(0L);
        submissionResult.setPassedTestCases(response.getPassedTestCases());
        submissionResult.setTotalTestCases(response.getTotalTestCases());
        submissionResult.setStdout(response.getStdout());
        submissionResult.setStderr(response.getStderr());

        // ── Redis-first delivery ────────────────────────────────────────────
        // 1. Cache to Redis (< 1 ms)
        cacheService.cacheResult(submissionId, finalStatus, submissionResult);
        // 2. Fire SSE — user sees verdict immediately
        sseService.sendEvent(submissionId, finalStatus, submissionResult);
        // 3. Persist to DB asynchronously
        asyncResultPersister.saveAsync(submission, submissionResult, finalStatus);
        // ────────────────────────────────────────────────────────────────────

        successfulExecutions.incrementAndGet();
        cumulativeExecutionTimeMs.addAndGet(submissionResult.getExecutionTimeMs());

        log.info("╔══════════════════════════════════════════════════");
        log.info("║ Submission  : {}", submissionId);
        log.info("║ Verdict     : {} (remote)", finalStatus);
        log.info("║ Test Cases  : {}/{} passed", response.getPassedTestCases(), response.getTotalTestCases());
        log.info("║ Compile     : {}ms", response.getCompileTimeMs());
        log.info("║ Run total   : {}ms (limit: {}ms)", response.getTotalExecTimeMs(), problem.getTimeLimitMs());
        log.info("╚══════════════════════════════════════════════════");
    }

    // Metric Getters
    public long getTotalSubmissions() { return totalSubmissions.get(); }
    public long getSuccessfulExecutions() { return successfulExecutions.get(); }
    public long getFailedExecutions() { return failedExecutions.get(); }
    public long getCumulativeExecutionTimeMs() { return cumulativeExecutionTimeMs.get(); }
}
