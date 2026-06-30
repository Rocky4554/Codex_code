package com.codex.platform.ai;

import com.codex.platform.common.util.OutputNormalizer;
import com.codex.platform.execution.client.ExecutorAgentClient;
import com.codex.platform.execution.client.dto.ExecuteRequest;
import com.codex.platform.execution.client.dto.ExecuteResponse;
import com.codex.platform.execution.entity.Language;
import com.codex.platform.execution.repository.LanguageRepository;
import com.codex.platform.execution.service.DockerExecutor;
import com.codex.platform.execution.dto.ExecutionResult;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Runs an AI-authored reference solution against a list of stdin inputs and
 * returns the program's real stdout for each — so the AI-guessed expected
 * outputs can be replaced with ground truth before the problem is saved.
 *
 * <p>Why one execution call per input (remote mode): the executor agent
 * short-circuits — the first non-passing test marks every later test as
 * {@code SKIPPED} with empty stdout (see {@code ExecutionRunner} in the engine).
 * Since we leave {@code expectedStdout} blank (we are harvesting, not grading),
 * the very first case "fails", so a single multi-test call would only ever give
 * us one real output. Running each input in its own call (fresh
 * {@code submissionId} to bypass the idempotency cache) sidesteps that.
 *
 * <p>Branches on {@code execution.mode} exactly like {@code ExecutionService}:
 * {@code remote} → executor agent on EC2; {@code local} → local Docker.
 */
@Service
@Slf4j
public class SolutionVerifier {

    private final ExecutorAgentClient executorAgentClient;
    private final DockerExecutor dockerExecutor;
    private final LanguageRepository languageRepository;

    @Value("${execution.mode:local}")
    private String executionMode;

    public SolutionVerifier(ExecutorAgentClient executorAgentClient,
                            DockerExecutor dockerExecutor,
                            LanguageRepository languageRepository) {
        this.executorAgentClient = executorAgentClient;
        this.dockerExecutor = dockerExecutor;
        this.languageRepository = languageRepository;
    }

    /** Outcome of a verification run. */
    @Data
    public static class VerificationResult {
        /** True if the reference solution actually ran (no missing language / executor down). */
        private boolean executed;
        /** Non-null when the reference solution failed to compile. */
        private String compileError;
        /** A human-readable warning when verification could not run at all. */
        private String warning;
        /**
         * Normalized stdout per input, aligned by index with the input list.
         * An entry is {@code null} when that specific input could not be verified
         * (runtime error, timeout, etc.) — caller keeps the AI's guess for it.
         */
        private List<String> outputs = new ArrayList<>();
    }

    public VerificationResult verify(String languageName, String sourceCode,
                                     List<String> inputs, int runTimeoutMs, int memoryLimitMb) {
        VerificationResult vr = new VerificationResult();

        if (sourceCode == null || sourceCode.isBlank()) {
            vr.setWarning("No reference solution was provided, so test outputs are AI-generated and unverified.");
            return vr;
        }

        Language language = resolveLanguage(languageName);
        if (language == null) {
            vr.setWarning("Reference language '" + languageName + "' is not configured on this server; "
                    + "test outputs are AI-generated and unverified.");
            return vr;
        }

        try {
            if ("remote".equalsIgnoreCase(executionMode)) {
                return verifyRemote(language, sourceCode, inputs, runTimeoutMs, memoryLimitMb);
            }
            return verifyLocal(language, sourceCode, inputs, runTimeoutMs, memoryLimitMb);
        } catch (ExecutorAgentClient.ExecutorAgentException agentDown) {
            log.warn("Verification skipped — executor unavailable: {}", agentDown.getMessage());
            vr.setWarning("Code execution engine is unavailable, so test outputs could not be verified.");
            return vr;
        } catch (Exception e) {
            log.warn("Verification failed unexpectedly: {}", e.getMessage(), e);
            vr.setWarning("Verification failed: " + e.getMessage());
            return vr;
        }
    }

    // ── Remote: one executor call per input ────────────────────────────────────

    private VerificationResult verifyRemote(Language language, String sourceCode,
                                            List<String> inputs, int runTimeoutMs, int memoryLimitMb) {
        VerificationResult vr = new VerificationResult();
        vr.setExecuted(true);

        for (int i = 0; i < inputs.size(); i++) {
            String input = inputs.get(i);
            ExecuteRequest req = ExecuteRequest.builder()
                    .submissionId(UUID.randomUUID()) // fresh id → bypass agent idempotency cache
                    .language(language.getName())
                    .dockerImage(language.getDockerImage())
                    .compileCommand(language.getCompileCommand())
                    .executeCommand(language.getExecuteCommand())
                    .fileExtension(language.getFileExtension())
                    .sourceCode(sourceCode)
                    .compileTimeoutMs(120_000)
                    .runTimeoutMs(runTimeoutMs)
                    .memoryLimitMb(memoryLimitMb)
                    .testCases(List.of(ExecuteRequest.TestCase.builder()
                            .id("verify-" + i)
                            .stdin(input)
                            .expectedStdout("") // harvesting output, not grading
                            .build()))
                    .build();

            ExecuteResponse resp = executorAgentClient.execute(req);

            if ("COMPILATION_ERROR".equalsIgnoreCase(resp.getStatus())) {
                vr.setCompileError(resp.getCompileOutput());
                vr.getOutputs().clear(); // nothing is trustworthy if it didn't compile
                return vr;
            }

            vr.getOutputs().add(harvestOutput(resp));
        }
        return vr;
    }

    /** Extract the real stdout from a single-test response, or null if it didn't run cleanly. */
    private String harvestOutput(ExecuteResponse resp) {
        if (resp.getResults() == null || resp.getResults().isEmpty()) {
            return null;
        }
        ExecuteResponse.TestResult tr = resp.getResults().get(0);
        if (tr.getExitCode() != 0) {
            return null; // runtime error / TLE / MLE — cannot trust output
        }
        return OutputNormalizer.normalize(tr.getStdout());
    }

    // ── Local: one container, run every input ──────────────────────────────────

    private VerificationResult verifyLocal(Language language, String sourceCode,
                                           List<String> inputs, int runTimeoutMs, int memoryLimitMb) throws Exception {
        VerificationResult vr = new VerificationResult();
        vr.setExecuted(true);

        String containerId = null;
        Path tempDir = null;
        try {
            tempDir = dockerExecutor.prepareTempDirectory(
                    sourceCode, "solution" + language.getFileExtension());
            containerId = dockerExecutor.createAndStartContainer(
                    language.getDockerImage(), tempDir, memoryLimitMb);

            ExecutionResult compileError = dockerExecutor.compileInContainer(
                    containerId, language.getCompileCommand());
            if (compileError != null) {
                vr.setCompileError(compileError.getStderr());
                return vr;
            }

            for (String input : inputs) {
                ExecutionResult result = dockerExecutor.runTestCase(
                        containerId, language.getExecuteCommand(), input, runTimeoutMs, tempDir);
                if (result.getExitCode() != null && result.getExitCode() == 0) {
                    vr.getOutputs().add(OutputNormalizer.normalize(result.getStdout()));
                } else {
                    vr.getOutputs().add(null);
                }
            }
            return vr;
        } finally {
            dockerExecutor.cleanup(containerId, tempDir);
        }
    }

    // ── Language resolution ────────────────────────────────────────────────────

    private Language resolveLanguage(String languageName) {
        if (languageName != null && !languageName.isBlank()) {
            Optional<Language> exact = languageRepository.findByName(languageName.trim());
            if (exact.isPresent()) {
                return exact.get();
            }
            // Tolerate common aliases the model might emit.
            String normalized = switch (languageName.trim().toLowerCase()) {
                case "py", "python3", "python 3" -> "Python";
                case "c++", "cpp", "cplusplus" -> "C++";
                case "js", "node", "nodejs" -> "JavaScript";
                case "java" -> "Java";
                default -> languageName.trim();
            };
            Optional<Language> aliased = languageRepository.findByName(normalized);
            if (aliased.isPresent()) {
                return aliased.get();
            }
        }
        // Last resort: Python is the most forgiving for AI-written reference code.
        return languageRepository.findByName("Python").orElse(null);
    }
}
