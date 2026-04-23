package com.codex.platform.problem.controller;

import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import com.codex.platform.problem.dto.ProblemDetailResponse;
import com.codex.platform.problem.dto.ProblemRequest;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.ProblemExample;
import com.codex.platform.problem.repository.ProblemExampleRepository;
import com.codex.platform.problem.service.ProblemService;
import jakarta.validation.Valid;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.UUID;

@RestController
@RequestMapping("/api/problems")
@RequiredArgsConstructor
public class ProblemController {

    private final ProblemService problemService;
    private final ProblemExampleRepository exampleRepository;

    @GetMapping
    public ResponseEntity<Page<Problem>> getAllProblems(
            @PageableDefault(size = 100) Pageable pageable) {
        return ResponseEntity.ok(problemService.getAllProblems(pageable));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ProblemDetailResponse> getProblemById(@PathVariable UUID id) {
        return problemService.getProblemDetailById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/{id}/admin")
    public ResponseEntity<ProblemDetailResponse> getAdminProblemById(@PathVariable UUID id) {
        requireAdmin();
        return problemService.getAdminProblemDetailById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<Problem> createProblem(@Valid @RequestBody ProblemRequest request) {
        requireAdmin();
        return ResponseEntity.status(HttpStatus.CREATED).body(problemService.createProblem(request));
    }

    @PutMapping("/{id}")
    public ResponseEntity<Problem> updateProblem(@PathVariable UUID id, @Valid @RequestBody ProblemRequest request) {
        requireAdmin();
        return ResponseEntity.ok(problemService.updateProblem(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProblem(@PathVariable UUID id) {
        requireAdmin();
        problemService.deleteProblem(id);
        return ResponseEntity.noContent().build();
    }

    // ── Example management ──────────────────────────────────────────────────

    @PostMapping("/{problemId}/examples")
    public ResponseEntity<ProblemExample> addExample(
            @PathVariable UUID problemId,
            @RequestBody ExampleRequest req) {
        requireAdmin();
        ProblemExample example = new ProblemExample();
        example.setProblemId(problemId);
        example.setInput(req.getInput());
        example.setOutput(req.getOutput());
        example.setExplanation(req.getExplanation());
        example.setDisplayOrder(req.getDisplayOrder() != null ? req.getDisplayOrder() : 0);
        return ResponseEntity.status(HttpStatus.CREATED).body(exampleRepository.save(example));
    }

    @DeleteMapping("/{problemId}/examples/{exampleId}")
    public ResponseEntity<Void> deleteExample(
            @PathVariable UUID problemId,
            @PathVariable UUID exampleId) {
        requireAdmin();
        exampleRepository.deleteById(exampleId);
        return ResponseEntity.noContent().build();
    }

    @Data
    static class ExampleRequest {
        private String input;
        private String output;
        private String explanation;
        private Integer displayOrder;
    }

    private void requireAdmin() {
        String role = JwtAuthenticationFilter.getCurrentUserRole();
        if (!"ADMIN".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Admin access required");
        }
    }
}
