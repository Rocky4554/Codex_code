package com.codex.platform.problem.service;

import com.codex.platform.problem.dto.TestCaseRequest;
import com.codex.platform.problem.entity.TestCase;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.problem.repository.TestCaseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class TestCaseService {

    private final TestCaseRepository testCaseRepository;
    private final ProblemRepository problemRepository;

    public List<TestCase> getTestCasesByProblemId(UUID problemId) {
        return testCaseRepository.findByProblemId(Objects.requireNonNull(problemId, "Problem ID is required"));
    }

    public List<TestCase> getSampleTestCasesByProblemId(UUID problemId) {
        return testCaseRepository.findByProblemIdAndIsSample(
                Objects.requireNonNull(problemId, "Problem ID is required"), 
                true
        );
    }

    public Optional<TestCase> getTestCaseById(UUID id) {
        return testCaseRepository.findById(Objects.requireNonNull(id, "Test case ID is required"));
    }

    @Transactional
    public TestCase createTestCase(TestCaseRequest request) {
        // Verify problem exists
        UUID problemId = Objects.requireNonNull(request.getProblemId(), "Problem ID is required");
        if (!problemRepository.existsById(problemId)) {
            throw new IllegalArgumentException("Problem not found with ID: " + problemId);
        }

        TestCase testCase = new TestCase();
        testCase.setProblemId(problemId);
        testCase.setInput(request.getInput());
        testCase.setExpectedOutput(request.getExpectedOutput());
        testCase.setIsSample(request.getIsSample() != null ? request.getIsSample() : false);
        
        return testCaseRepository.save(testCase);
    }

    @Transactional
    public TestCase updateTestCase(UUID id, TestCaseRequest request) {
        TestCase testCase = testCaseRepository.findById(Objects.requireNonNull(id, "Test case ID is required"))
                .orElseThrow(() -> new IllegalArgumentException("Test case not found"));

        // Verify problem exists if changed
        UUID problemId = Objects.requireNonNull(request.getProblemId(), "Problem ID is required");
        if (!problemId.equals(testCase.getProblemId()) && !problemRepository.existsById(problemId)) {
            throw new IllegalArgumentException("Problem not found with ID: " + problemId);
        }

        testCase.setProblemId(problemId);
        testCase.setInput(request.getInput());
        testCase.setExpectedOutput(request.getExpectedOutput());
        testCase.setIsSample(request.getIsSample() != null ? request.getIsSample() : false);
        
        return testCaseRepository.save(testCase);
    }

    @Transactional
    public void deleteTestCase(UUID id) {
        UUID testCaseId = Objects.requireNonNull(id, "Test case ID is required");
        if (!testCaseRepository.existsById(testCaseId)) {
            throw new IllegalArgumentException("Test case not found");
        }
        testCaseRepository.deleteById(testCaseId);
    }

    @Transactional
    public void deleteTestCasesByProblemId(UUID problemId) {
        UUID pid = Objects.requireNonNull(problemId, "Problem ID is required");
        List<TestCase> testCases = testCaseRepository.findByProblemId(pid);
        testCaseRepository.deleteAll(testCases);
    }
}
