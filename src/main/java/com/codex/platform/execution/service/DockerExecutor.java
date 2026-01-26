package com.codex.platform.execution.service;

import com.codex.platform.execution.dto.ExecutionResult;
import com.github.dockerjava.api.DockerClient;
import com.github.dockerjava.api.command.CreateContainerResponse;
import com.github.dockerjava.api.command.WaitContainerResultCallback;
import com.github.dockerjava.api.model.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
@Slf4j
public class DockerExecutor {

    private final DockerClient dockerClient;

    @Value("${execution.temp-dir:/tmp/codex}")
    private String tempBaseDir;

    @Value("${execution.default-time-limit-ms:5000}")
    private int defaultTimeLimit;

    @Value("${execution.default-memory-limit-mb:256}")
    private int defaultMemoryLimit;

    /**
     * Execute code in a Docker container
     */
    public ExecutionResult executeCode(String dockerImage,
            String sourceCode,
            String fileName,
            String executeCommand,
            String compileCommand,
            String input,
            int timeLimitMs,
            int memoryLimitMb) {
        String containerId = null;
        Path tempDir = null;

        try {
            // Create temp directory
            tempDir = createTempDirectory();
            Path sourceFile = tempDir.resolve(fileName);
            Files.writeString(sourceFile, sourceCode);

            // Create input file if needed
            if (input != null && !input.isEmpty()) {
                Path inputFile = tempDir.resolve("input.txt");
                Files.writeString(inputFile, input);
            }

            // Create container
            containerId = createContainer(dockerImage, tempDir, timeLimitMs, memoryLimitMb);

            log.info("Created container: {}", containerId);

            // Start container
            dockerClient.startContainerCmd(containerId).exec();

            long startTime = System.currentTimeMillis();

            // Compile if needed
            if (compileCommand != null && !compileCommand.isEmpty()) {
                ExecutionResult compileResult = executeCommandInContainer(
                        containerId,
                        compileCommand,
                        null,
                        timeLimitMs);

                if (!compileResult.isSuccess() || compileResult.getExitCode() != 0) {
                    return new ExecutionResult(
                            compileResult.getStdout(),
                            compileResult.getStderr(),
                            compileResult.getExitCode(),
                            compileResult.getExecutionTimeMs(),
                            false);
                }
            }

            // Execute code
            String inputRedirect = (input != null && !input.isEmpty()) ? " < /workspace/input.txt" : "";
            String fullCommand = executeCommand + inputRedirect;

            ExecutionResult result = executeCommandInContainer(
                    containerId,
                    fullCommand,
                    null,
                    timeLimitMs);

            long executionTime = System.currentTimeMillis() - startTime;
            result.setExecutionTimeMs(executionTime);
            result.setSuccess(result.getExitCode() == 0);

            return result;

        } catch (Exception e) {
            log.error("Execution error: ", e);
            return new ExecutionResult(
                    "",
                    "Execution error: " + e.getMessage(),
                    -1,
                    0L,
                    false);
        } finally {
            // Cleanup
            cleanup(containerId, tempDir);
        }
    }

    private String createContainer(String image, Path workDir, int timeLimitMs, int memoryLimitMb) {
        HostConfig hostConfig = HostConfig.newHostConfig()
                .withBinds(new Bind(workDir.toString(), new Volume("/workspace")))
                .withNetworkMode("none") // No network access
                .withMemory((long) memoryLimitMb * 1024 * 1024) // Memory limit
                .withMemorySwap((long) memoryLimitMb * 1024 * 1024) // No swap
                .withCpuQuota(50000L) // 50% CPU
                .withPidsLimit(50L) // Process limit
                .withAutoRemove(false);

        CreateContainerResponse container = dockerClient.createContainerCmd(image)
                .withHostConfig(hostConfig)
                .withWorkingDir("/workspace")
                .withCmd("sleep", String.valueOf(timeLimitMs / 1000 + 10))
                .exec();

        return container.getId();
    }

    private ExecutionResult executeCommandInContainer(String containerId,
            String command,
            String input,
            int timeLimitMs) throws Exception {
        ByteArrayOutputStream stdout = new ByteArrayOutputStream();
        ByteArrayOutputStream stderr = new ByteArrayOutputStream();

        long startTime = System.currentTimeMillis();

        // Execute command using docker exec
        String execId = dockerClient.execCreateCmd(containerId)
                .withCmd("/bin/sh", "-c", command)
                .withAttachStdout(true)
                .withAttachStderr(true)
                .exec()
                .getId();

        dockerClient.execStartCmd(execId)
                .exec(new com.github.dockerjava.api.async.ResultCallback.Adapter<>() {
                })
                .awaitCompletion(timeLimitMs, TimeUnit.MILLISECONDS);

        // Get logs
        dockerClient.logContainerCmd(containerId)
                .withStdOut(true)
                .withStdErr(true)
                .exec(new com.github.dockerjava.core.command.LogContainerResultCallback() {
                    @Override
                    public void onNext(Frame item) {
                        try {
                            if (item.getStreamType() == StreamType.STDOUT) {
                                stdout.write(item.getPayload());
                            } else if (item.getStreamType() == StreamType.STDERR) {
                                stderr.write(item.getPayload());
                            }
                        } catch (IOException e) {
                            log.error("Error reading logs", e);
                        }
                    }
                })
                .awaitCompletion(2, TimeUnit.SECONDS);

        long executionTime = System.currentTimeMillis() - startTime;

        // Get exit code
        Integer exitCode = dockerClient.inspectExecCmd(execId).exec().getExitCodeLong().intValue();

        return new ExecutionResult(
                stdout.toString(),
                stderr.toString(),
                exitCode != null ? exitCode : -1,
                executionTime,
                exitCode != null && exitCode == 0);
    }

    private Path createTempDirectory() throws IOException {
        Path baseDir = Paths.get(tempBaseDir);
        Files.createDirectories(baseDir);
        return Files.createTempDirectory(baseDir, "exec-");
    }

    private void cleanup(String containerId, Path tempDir) {
        // Remove container
        if (containerId != null) {
            try {
                dockerClient.removeContainerCmd(containerId)
                        .withForce(true)
                        .exec();
                log.info("Removed container: {}", containerId);
            } catch (Exception e) {
                log.error("Error removing container: {}", containerId, e);
            }
        }

        // Delete temp directory
        if (tempDir != null) {
            try {
                deleteDirectory(tempDir.toFile());
                log.info("Deleted temp directory: {}", tempDir);
            } catch (Exception e) {
                log.error("Error deleting temp directory: {}", tempDir, e);
            }
        }
    }

    private void deleteDirectory(File directory) {
        if (directory.isDirectory()) {
            File[] files = directory.listFiles();
            if (files != null) {
                for (File file : files) {
                    deleteDirectory(file);
                }
            }
        }
        directory.delete();
    }
}
