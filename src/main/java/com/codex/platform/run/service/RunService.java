package com.codex.platform.run.service;

import com.codex.platform.execution.client.ExecutorAgentClient;
import com.codex.platform.execution.client.dto.ExecuteRequest;
import com.codex.platform.execution.client.dto.ExecuteResponse;
import com.codex.platform.execution.entity.Language;
import com.codex.platform.execution.repository.LanguageRepository;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.TestCase;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.problem.repository.TestCaseRepository;
import com.codex.platform.run.dto.RunCodeRequest;
import com.codex.platform.run.dto.RunCodeResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class RunService {

    private final ProblemRepository problemRepository;
    private final LanguageRepository languageRepository;
    private final TestCaseRepository testCaseRepository;
    private final ExecutorAgentClient executorAgentClient;

    @Value("${execution.mode:local}")
    private String executionMode;

    public RunCodeResponse run(RunCodeRequest request) {
        Problem problem = problemRepository.findById(request.getProblemId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Problem not found"));

        Language language = languageRepository.findById(request.getLanguageId())
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Language not found"));

        List<TestCase> sampleCases = testCaseRepository
                .findByProblemIdAndIsSample(request.getProblemId(), true);

        if (sampleCases.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.UNPROCESSABLE_ENTITY,
                    "No sample test cases found for this problem");
        }

        if ("remote".equals(executionMode)) {
            return runRemote(request.getSourceCode(), problem, language, sampleCases);
        }

        throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,
                "Run is only supported in remote execution mode");
    }

    private RunCodeResponse runRemote(String sourceCode, Problem problem, Language language,
                                      List<TestCase> sampleCases) {
        UUID ephemeralId = UUID.randomUUID();

        List<ExecuteRequest.TestCase> wireTestCases = sampleCases.stream()
                .map(tc -> ExecuteRequest.TestCase.builder()
                        .id(tc.getId().toString())
                        .stdin(tc.getInput())
                        .expectedStdout(tc.getExpectedOutput())
                        .build())
                .toList();

        ExecuteRequest request = ExecuteRequest.builder()
                .submissionId(ephemeralId)
                .language(language.getName())
                .dockerImage(language.getDockerImage())
                .compileCommand(language.getCompileCommand())
                .executeCommand(language.getExecuteCommand())
                .fileExtension(language.getFileExtension())
                .sourceCode(sourceCode)
                .compileTimeoutMs(180_000)
                .runTimeoutMs(problem.getTimeLimitMs())
                .memoryLimitMb(problem.getMemoryLimitMb())
                .testCases(wireTestCases)
                .build();

        log.info("Run request: problemId={}, language={}, sampleCases={}",
                problem.getId(), language.getName(), sampleCases.size());

        ExecuteResponse response;
        try {
            response = executorAgentClient.execute(request);
        } catch (ExecutorAgentClient.ExecutorAgentException e) {
            log.error("Executor agent unreachable during run: {}", e.getMessage());
            return RunCodeResponse.builder()
                    .status("RUNTIME_ERROR")
                    .stderr("Executor unavailable: " + e.getMessage())
                    .testsPassed(0)
                    .totalTests(sampleCases.size())
                    .testResults(List.of())
                    .build();
        }

        List<RunCodeResponse.TestResult> testResults = buildTestResults(response, sampleCases);

        return RunCodeResponse.builder()
                .status(response.getStatus())
                .stdout(response.getStdout())
                .stderr(response.getStderr())
                .testsPassed(response.getPassedTestCases())
                .totalTests(response.getTotalTestCases())
                .testResults(testResults)
                .build();
    }

    private List<RunCodeResponse.TestResult> buildTestResults(ExecuteResponse response,
                                                               List<TestCase> sampleCases) {
        if (response.getResults() == null) return List.of();

        return response.getResults().stream()
                .map(r -> {
                    TestCase tc = sampleCases.stream()
                            .filter(s -> s.getId().toString().equals(r.getTestCaseId()))
                            .findFirst()
                            .orElse(null);
                    return RunCodeResponse.TestResult.builder()
                            .input(tc != null ? tc.getInput() : "")
                            .expectedOutput(tc != null ? tc.getExpectedOutput() : "")
                            .actualOutput(r.getStdout())
                            .passed("ACCEPTED".equals(r.getStatus()))
                            .build();
                })
                .toList();
    }
}
