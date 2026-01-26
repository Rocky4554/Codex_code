package com.codex.platform.config;

import com.codex.platform.common.enums.ProblemDifficulty;
import com.codex.platform.execution.entity.Language;
import com.codex.platform.execution.repository.LanguageRepository;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.TestCase;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.problem.repository.TestCaseRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final LanguageRepository languageRepository;
    private final ProblemRepository problemRepository;
    private final TestCaseRepository testCaseRepository;

    @Override
    public void run(String... args) {
        if (languageRepository.count() == 0) {
            initializeLanguages();
        }

        if (problemRepository.count() == 0) {
            initializeSampleProblems();
        }
    }

    private void initializeLanguages() {
        log.info("Initializing languages...");

        // Python
        Language python = new Language();
        python.setName("Python");
        python.setVersion("3.11");
        python.setDockerImage("python:3.11-slim");
        python.setFileExtension(".py");
        python.setCompileCommand(null);
        python.setExecuteCommand("python solution.py");
        languageRepository.save(python);

        // Java
        Language java = new Language();
        java.setName("Java");
        java.setVersion("17");
        java.setDockerImage("openjdk:17-slim");
        java.setFileExtension(".java");
        java.setCompileCommand("javac solution.java");
        java.setExecuteCommand("java solution");
        languageRepository.save(java);

        // C++
        Language cpp = new Language();
        cpp.setName("C++");
        cpp.setVersion("11");
        cpp.setDockerImage("gcc:latest");
        cpp.setFileExtension(".cpp");
        cpp.setCompileCommand("g++ -std=c++11 -o solution solution.cpp");
        cpp.setExecuteCommand("./solution");
        languageRepository.save(cpp);

        // JavaScript (Node.js)
        Language javascript = new Language();
        javascript.setName("JavaScript");
        javascript.setVersion("20");
        javascript.setDockerImage("node:20-slim");
        javascript.setFileExtension(".js");
        javascript.setCompileCommand(null);
        javascript.setExecuteCommand("node solution.js");
        languageRepository.save(javascript);

        log.info("Languages initialized successfully");
    }

    private void initializeSampleProblems() {
        log.info("Initializing sample problems...");

        // Problem 1: Two Sum
        Problem twoSum = new Problem();
        twoSum.setTitle("Two Sum");
        twoSum.setDescription(
                "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nInput: First line contains space-separated integers (nums), second line contains target.\nOutput: Two space-separated indices.");
        twoSum.setDifficulty(ProblemDifficulty.EASY);
        twoSum.setTimeLimitMs(5000);
        twoSum.setMemoryLimitMb(256);
        Problem savedTwoSum = problemRepository.save(twoSum);

        // Test cases for Two Sum
        TestCase tc1 = new TestCase();
        tc1.setProblemId(savedTwoSum.getId());
        tc1.setInput("2 7 11 15\n9");
        tc1.setExpectedOutput("0 1");
        tc1.setIsSample(true);
        testCaseRepository.save(tc1);

        TestCase tc2 = new TestCase();
        tc2.setProblemId(savedTwoSum.getId());
        tc2.setInput("3 2 4\n6");
        tc2.setExpectedOutput("1 2");
        tc2.setIsSample(false);
        testCaseRepository.save(tc2);

        // Problem 2: Hello World
        Problem helloWorld = new Problem();
        helloWorld.setTitle("Hello World");
        helloWorld.setDescription("Print 'Hello, World!' to the console.");
        helloWorld.setDifficulty(ProblemDifficulty.EASY);
        helloWorld.setTimeLimitMs(2000);
        helloWorld.setMemoryLimitMb(128);
        Problem savedHelloWorld = problemRepository.save(helloWorld);

        // Test case for Hello World
        TestCase tcHello = new TestCase();
        tcHello.setProblemId(savedHelloWorld.getId());
        tcHello.setInput("");
        tcHello.setExpectedOutput("Hello, World!");
        tcHello.setIsSample(true);
        testCaseRepository.save(tcHello);

        log.info("Sample problems initialized successfully");
    }
}
