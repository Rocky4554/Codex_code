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
import com.codex.platform.submission.service.ResultProcessor;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

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
    private final ResultProcessor resultProcessor;
    private final SseService sseService;

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
     * <p>Branches on {@code execution.mode}:
     * <ul>
     *   <li>{@code local} — drive {@link DockerExecutor} on the same machine</li>
     *   <li>{@code remote} — POST to the executor agent on EC2</li>
     * </ul>
     *
     * <p>Both branches share the same persistence and SSE plumbing — only the
     * "where does the container actually run" decision differs.
     */
    public void executeSubmission(UUID submissionId) {
        log.info("Starting execution for submission: {} (mode={})", submissionId, executionMode);
        totalSubmissions.incrementAndGet();

        try {
            // Load submission
            Submission submission = submissionRepository
                    .findById(Objects.requireNonNull(submissionId, "Submission ID is required"))
                    .orElseThrow(() -> new IllegalArgumentException("Submission not found"));

            // Send RUNNING event
            sseService.sendEvent(submissionId, SubmissionStatus.RUNNING);
            submission.setStatus(SubmissionStatus.RUNNING);
            submissionRepository.save(submission);

            // Load problem, language, and test cases
            Problem problem = problemRepository
                    .findById(Objects.requireNonNull(submission.getProblemId(), "Problem ID is required"))
                    .orElseThrow(() -> new IllegalArgumentException("Problem not found"));

            Language language = languageRepository
                    .findById(Objects.requireNonNull(submission.getLanguageId(), "Language ID is required"))
                    .orElseThrow(() -> new IllegalArgumentException("Language not found"));

            List<TestCase> testCases = testCaseRepository.findByProblemId(problem.getId());
            if (testCases.isEmpty()) {
                throw new IllegalArgumentException("No test cases found for problem");
            }

            if ("remote".equalsIgnoreCase(executionMode)) {
                executeRemote(submission, problem, language, testCases);
            } else {
                executeLocal(submission, problem, language, testCases);
            }

        } catch (Exception e) {
            log.error("Error executing submission: {}", submissionId, e);

            submissionRepository.findById(Objects.requireNonNull(submissionId, "Submission ID is required"))
                    .ifPresent(submission -> {
                        submission.setStatus(SubmissionStatus.RUNTIME_ERROR);
                        submissionRepository.save(submission);
                        sseService.sendEvent(submissionId, SubmissionStatus.RUNTIME_ERROR);
                    });
            failedExecutions.incrementAndGet();
        }
    }

    /**
     * Legacy in-process path — runs containers on the local Docker daemon.
     */
    private void executeLocal(Submission submission, Problem problem, Language language, List<TestCase> testCases) {
        UUID submissionId = submission.getId();
        String containerId = null;
        Path tempDir = null;

        try {
            // ── Single Container Lifecycle ──────────────────────────────
            // 1. Prepare workspace (write source file to temp dir)
            tempDir = dockerExecutor.prepareTempDirectory(
                    submission.getSourceCode(),
                    "solution" + language.getFileExtension());

            // 2. Create and start ONE container
            containerId = dockerExecutor.createAndStartContainer(
                    language.getDockerImage(),
                    tempDir,
                    problem.getMemoryLimitMb());

            // 3. Compile once (returns null on success, error result on failure)
            ExecutionResult compileError = dockerExecutor.compileInContainer(
                    containerId,
                    language.getCompileCommand());

            SubmissionStatus finalStatus;
            int passedCount = 0;
            long totalExecutionTime = 0;
            StringBuilder stdoutBuilder = new StringBuilder();
            StringBuilder stderrBuilder = new StringBuilder();

            if (compileError != null) {
                // Compilation failed
                finalStatus = SubmissionStatus.COMPILATION_ERROR;
                stdoutBuilder.append(compileError.getStdout());
                stderrBuilder.append(compileError.getStderr());
                totalExecutionTime = compileError.getExecutionTimeMs();
                log.warn("Compilation failed ({}ms): {}", totalExecutionTime,
                        compileError.getStderr().length() > 200
                                ? compileError.getStderr().substring(0, 200) + "..."
                                : compileError.getStderr());
            } else {
                // 4. Run each test case in the SAME container
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

                    // Check for runtime error (exit 137 usually means OOM kill in container)
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

                    // Check for time limit exceeded
                    if (result.getExecutionTimeMs() > problem.getTimeLimitMs()) {
                        log.warn("  -> Test {}/{} TIME_LIMIT_EXCEEDED ({}ms / limit {}ms)",
                                testIndex, testCases.size(), result.getExecutionTimeMs(), problem.getTimeLimitMs());
                        finalStatus = SubmissionStatus.TIME_LIMIT_EXCEEDED;
                        break;
                    }

                    // Compare output
                    if (OutputNormalizer.areEqual(testCase.getExpectedOutput(), result.getStdout())) {
                        passedCount++;
                        log.info("  -> Test {}/{} PASSED ({}ms)", testIndex, testCases.size(),
                                result.getExecutionTimeMs());
                    } else {
                        finalStatus = SubmissionStatus.WRONG_ANSWER;
                        log.warn("  -> Test {}/{} WRONG_ANSWER ({}ms)", testIndex, testCases.size(),
                                result.getExecutionTimeMs());
                        log.debug("     Expected: [{}]", testCase.getExpectedOutput());
                        log.debug("     Got:      [{}]", result.getStdout());
                        break;
                    }
                }
            }

            // Save result
            SubmissionResult submissionResult = new SubmissionResult();
            submissionResult.setSubmissionId(submissionId);
            submissionResult.setExecutionTimeMs(totalExecutionTime);
            submissionResult.setMemoryUsedMb(0L); // TODO: Implement memory tracking
            submissionResult.setPassedTestCases(passedCount);
            submissionResult.setTotalTestCases(testCases.size());
            submissionResult.setStdout(stdoutBuilder.toString());
            submissionResult.setStderr(stderrBuilder.toString());

            resultProcessor.saveResult(submission, submissionResult, finalStatus);
            sseService.sendEvent(submissionId, finalStatus);

            successfulExecutions.incrementAndGet();
            cumulativeExecutionTimeMs.addAndGet(totalExecutionTime);

            log.info("╔══════════════════════════════════════════════════");
            log.info("║ Submission  : {}", submissionId);
            log.info("║ Verdict     : {} (local)", finalStatus);
            log.info("║ Test Cases  : {}/{} passed", passedCount, testCases.size());
            log.info("║ Time        : {}ms (limit: {}ms)", totalExecutionTime, problem.getTimeLimitMs());
            log.info("║ Memory      : {}MB (limit: {}MB)", submissionResult.getMemoryUsedMb(),
                    problem.getMemoryLimitMb());
            log.info("╚══════════════════════════════════════════════════");

        } catch (RuntimeException re) {
            throw re;
        } catch (Exception e) {
            // Wrap checked exceptions so the outer handler in executeSubmission picks them up
            throw new RuntimeException("Local execution failed", e);
        } finally {
            // Cleanup — always runs, even on error
            dockerExecutor.cleanup(containerId, tempDir);
        }
    }

    /**
     * Remote path — POST the submission to the executor agent on EC2 over HTTPS.
     * The agent runs the container, returns the verdict + per-test results, and
     * we map them back into the existing {@link SubmissionResult} entity.
     */
    private void executeRemote(Submission submission, Problem problem, Language language, List<TestCase> testCases) {
        UUID submissionId = submission.getId();

        // Build the request from the loaded entities
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
                .compileTimeoutMs(60_000)
                .runTimeoutMs(problem.getTimeLimitMs())
                .memoryLimitMb(problem.getMemoryLimitMb())
                .testCases(wireTestCases)
                .build();

        ExecuteResponse response;
        try {
            response = executorAgentClient.execute(request);
        } catch (ExecutorAgentClient.ExecutorAgentException agentError) {
            log.error("Submission {}: executor agent unreachable: {}", submissionId, agentError.getMessage());
            // Persist a clear error so the user sees a useful message instead of a hang.
            SubmissionResult errorResult = new SubmissionResult();
            errorResult.setSubmissionId(submissionId);
            errorResult.setExecutionTimeMs(0L);
            errorResult.setMemoryUsedMb(0L);
            errorResult.setPassedTestCases(0);
            errorResult.setTotalTestCases(testCases.size());
            errorResult.setStdout("");
            errorResult.setStderr("Executor unavailable: " + agentError.getMessage());
            resultProcessor.saveResult(submission, errorResult, SubmissionStatus.RUNTIME_ERROR);
            sseService.sendEvent(submissionId, SubmissionStatus.RUNTIME_ERROR);
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
        submissionResult.setMemoryUsedMb(0L); // TODO: Implement memory tracking
        submissionResult.setPassedTestCases(response.getPassedTestCases());
        submissionResult.setTotalTestCases(response.getTotalTestCases());
        submissionResult.setStdout(response.getStdout());
        submissionResult.setStderr(response.getStderr());

        resultProcessor.saveResult(submission, submissionResult, finalStatus);
        sseService.sendEvent(submissionId, finalStatus, submissionResult);

        successfulExecutions.incrementAndGet();
        cumulativeExecutionTimeMs.addAndGet(submissionResult.getExecutionTimeMs());

        log.info("╔══════════════════════════════════════════════════");
        log.info("║ Submission  : {}", submissionId);
        log.info("║ Verdict     : {} (remote)", finalStatus);
        log.info("║ Test Cases  : {}/{} passed", response.getPassedTestCases(), response.getTotalTestCases());
        log.info("║ Compile     : {}ms", response.getCompileTimeMs());
        log.info("║ Run total   : {}ms (limit: {}ms)", response.getTotalExecTimeMs(), problem.getTimeLimitMs());
        log.info("║ Memory      : limit {}MB", problem.getMemoryLimitMb());
        log.info("╚══════════════════════════════════════════════════");
    }

    // Metric Getters
    public long getTotalSubmissions() {
        return totalSubmissions.get();
    }

    public long getSuccessfulExecutions() {
        return successfulExecutions.get();
    }

    public long getFailedExecutions() {
        return failedExecutions.get();
    }

    public long getCumulativeExecutionTimeMs() {
        return cumulativeExecutionTimeMs.get();
    }
}
