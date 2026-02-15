package com.codex.platform.execution.service;

import com.codex.platform.common.enums.SubmissionStatus;
import com.codex.platform.common.util.OutputNormalizer;
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
import org.springframework.stereotype.Service;

import java.nio.file.Path;
import java.util.List;
import java.util.Objects;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class ExecutionService {

    private final SubmissionRepository submissionRepository;
    private final ProblemRepository problemRepository;
    private final TestCaseRepository testCaseRepository;
    private final LanguageRepository languageRepository;
    private final DockerExecutor dockerExecutor;
    private final ResultProcessor resultProcessor;
    private final SseService sseService;

    /**
     * Main entry point for executing a submission.
     * Uses a SINGLE container for the entire submission — compile once, run all
     * test cases.
     */
    public void executeSubmission(UUID submissionId) {
        log.info("Starting execution for submission: {}", submissionId);

        String containerId = null;
        Path tempDir = null;

        try {
            // Load submission
            Submission submission = submissionRepository.findById(Objects.requireNonNull(submissionId, "Submission ID is required"))
                    .orElseThrow(() -> new IllegalArgumentException("Submission not found"));

            // Send RUNNING event
            sseService.sendEvent(submissionId, SubmissionStatus.RUNNING);
            submission.setStatus(SubmissionStatus.RUNNING);
            submissionRepository.save(submission);

            // Load problem, language, and test cases
            Problem problem = problemRepository.findById(Objects.requireNonNull(submission.getProblemId(), "Problem ID is required"))
                    .orElseThrow(() -> new IllegalArgumentException("Problem not found"));

            Language language = languageRepository.findById(Objects.requireNonNull(submission.getLanguageId(), "Language ID is required"))
                    .orElseThrow(() -> new IllegalArgumentException("Language not found"));

            List<TestCase> testCases = testCaseRepository.findByProblemId(problem.getId());
            if (testCases.isEmpty()) {
                throw new IllegalArgumentException("No test cases found for problem");
            }

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
                        log.info("  -> Test {}/{} PASSED ({}ms)", testIndex, testCases.size(), result.getExecutionTimeMs());
                    } else {
                        finalStatus = SubmissionStatus.WRONG_ANSWER;
                        log.warn("  -> Test {}/{} WRONG_ANSWER ({}ms)", testIndex, testCases.size(), result.getExecutionTimeMs());
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

            log.info("╔══════════════════════════════════════════════════");
            log.info("║ Submission  : {}", submissionId);
            log.info("║ Verdict     : {}", finalStatus);
            log.info("║ Test Cases  : {}/{} passed", passedCount, testCases.size());
            log.info("║ Time        : {}ms (limit: {}ms)", totalExecutionTime, problem.getTimeLimitMs());
            log.info("║ Memory      : {}MB (limit: {}MB)", submissionResult.getMemoryUsedMb(), problem.getMemoryLimitMb());
            log.info("╚══════════════════════════════════════════════════");

        } catch (Exception e) {
            log.error("Error executing submission: {}", submissionId, e);

            submissionRepository.findById(Objects.requireNonNull(submissionId, "Submission ID is required")).ifPresent(submission -> {
                submission.setStatus(SubmissionStatus.RUNTIME_ERROR);
                submissionRepository.save(submission);
                sseService.sendEvent(submissionId, SubmissionStatus.RUNTIME_ERROR);
            });
        } finally {
            // 5. Cleanup — always runs, even on error
            dockerExecutor.cleanup(containerId, tempDir);
        }
    }
}
