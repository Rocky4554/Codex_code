package com.codex.platform.problem.controller;

import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import com.codex.platform.problem.dto.TestCaseRequest;
import com.codex.platform.problem.entity.TestCase;
import com.codex.platform.problem.service.TestCaseService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/test-cases")
@RequiredArgsConstructor
@Validated
public class TestCaseController {

    private final TestCaseService testCaseService;

    @GetMapping("/problem/{problemId}")
    public ResponseEntity<List<TestCase>> getTestCasesByProblemId(@PathVariable UUID problemId) {
        requireAdmin();
        return ResponseEntity.ok(testCaseService.getTestCasesByProblemId(problemId));
    }

    @GetMapping("/problem/{problemId}/samples")
    public ResponseEntity<List<TestCase>> getSampleTestCasesByProblemId(@PathVariable UUID problemId) {
        return ResponseEntity.ok(testCaseService.getSampleTestCasesByProblemId(problemId));
    }

    @GetMapping("/{id}")
    public ResponseEntity<TestCase> getTestCaseById(@PathVariable UUID id) {
        requireAdmin();
        return testCaseService.getTestCaseById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<TestCase> createTestCase(@Valid @RequestBody TestCaseRequest request) {
        requireAdmin();
        return ResponseEntity.status(HttpStatus.CREATED).body(testCaseService.createTestCase(request));
    }

    @PostMapping("/batch")
    public ResponseEntity<List<TestCase>> createTestCases(@Valid @RequestBody List<TestCaseRequest> requests) {
        requireAdmin();
        List<TestCase> created = requests.stream()
                .map(testCaseService::createTestCase)
                .toList();
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<TestCase> updateTestCase(@PathVariable UUID id, @Valid @RequestBody TestCaseRequest request) {
        requireAdmin();
        return ResponseEntity.ok(testCaseService.updateTestCase(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteTestCase(@PathVariable UUID id) {
        requireAdmin();
        testCaseService.deleteTestCase(id);
        return ResponseEntity.noContent().build();
    }

    @DeleteMapping("/problem/{problemId}")
    public ResponseEntity<Void> deleteTestCasesByProblemId(@PathVariable UUID problemId) {
        requireAdmin();
        testCaseService.deleteTestCasesByProblemId(problemId);
        return ResponseEntity.noContent().build();
    }

    private void requireAdmin() {
        String role = JwtAuthenticationFilter.getCurrentUserRole();
        if (!"ADMIN".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Admin access required");
        }
    }
}
