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

import java.util.List;
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
     * Main entry point for executing a submission
     */
    public void executeSubmission(UUID submissionId) {
        log.info("Starting execution for submission: {}", submissionId);

        try {
            // Load submission
            Submission submission = submissionRepository.findById(submissionId)
                    .orElseThrow(() -> new IllegalArgumentException("Submission not found"));

            // Send RUNNING event
            sseService.sendEvent(submissionId, SubmissionStatus.RUNNING);

            // Update status to RUNNING
            submission.setStatus(SubmissionStatus.RUNNING);
            submissionRepository.save(submission);

            // Load problem, language, and test cases
            Problem problem = problemRepository.findById(submission.getProblemId())
                    .orElseThrow(() -> new IllegalArgumentException("Problem not found"));

            Language language = languageRepository.findById(submission.getLanguageId())
                    .orElseThrow(() -> new IllegalArgumentException("Language not found"));

            List<TestCase> testCases = testCaseRepository.findByProblemId(problem.getId());

            if (testCases.isEmpty()) {
                throw new IllegalArgumentException("No test cases found for problem");
            }

            // Execute test cases
            SubmissionStatus finalStatus = SubmissionStatus.ACCEPTED;
            int passedCount = 0;
            long totalExecutionTime = 0;
            StringBuilder stdoutBuilder = new StringBuilder();
            StringBuilder stderrBuilder = new StringBuilder();

            for (TestCase testCase : testCases) {
                log.info("Running test case: {}", testCase.getId());

                ExecutionResult result = dockerExecutor.executeCode(
                        language.getDockerImage(),
                        submission.getSourceCode(),
                        "solution" + language.getFileExtension(),
                        language.getExecuteCommand(),
                        language.getCompileCommand(),
                        testCase.getInput(),
                        problem.getTimeLimitMs(),
                        problem.getMemoryLimitMb());

                totalExecutionTime += result.getExecutionTimeMs();
                stdoutBuilder.append(result.getStdout()).append("\n");
                stderrBuilder.append(result.getStderr()).append("\n");

                // Check for compilation error
                if (!result.isSuccess() && language.getCompileCommand() != null) {
                    finalStatus = SubmissionStatus.COMPILATION_ERROR;
                    break;
                }

                // Check for runtime error
                if (result.getExitCode() != 0) {
                    finalStatus = SubmissionStatus.RUNTIME_ERROR;
                    break;
                }

                // Check for time limit exceeded
                if (result.getExecutionTimeMs() > problem.getTimeLimitMs()) {
                    finalStatus = SubmissionStatus.TIME_LIMIT_EXCEEDED;
                    break;
                }

                // Compare output
                if (OutputNormalizer.areEqual(testCase.getExpectedOutput(), result.getStdout())) {
                    passedCount++;
                } else {
                    finalStatus = SubmissionStatus.WRONG_ANSWER;
                    log.info("Wrong answer on test case: {}", testCase.getId());
                    log.debug("Expected: {}", testCase.getExpectedOutput());
                    log.debug("Got: {}", result.getStdout());
                    break;
                }
            }

            // Create result
            SubmissionResult submissionResult = new SubmissionResult();
            submissionResult.setSubmissionId(submissionId);
            submissionResult.setExecutionTimeMs(totalExecutionTime);
            submissionResult.setMemoryUsedMb(0L); // TODO: Implement memory tracking
            submissionResult.setPassedTestCases(passedCount);
            submissionResult.setTotalTestCases(testCases.size());
            submissionResult.setStdout(stdoutBuilder.toString());
            submissionResult.setStderr(stderrBuilder.toString());

            // Save result
            resultProcessor.saveResult(submission, submissionResult, finalStatus);

            // Send final event
            sseService.sendEvent(submissionId, finalStatus);

            log.info("Execution completed for submission: {} with status: {}", submissionId, finalStatus);

        } catch (Exception e) {
            log.error("Error executing submission: {}", submissionId, e);

            // Update submission status to error
            submissionRepository.findById(submissionId).ifPresent(submission -> {
                submission.setStatus(SubmissionStatus.RUNTIME_ERROR);
                submissionRepository.save(submission);
                sseService.sendEvent(submissionId, SubmissionStatus.RUNTIME_ERROR);
            });
        }
    }
}
