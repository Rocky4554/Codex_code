package com.codex.platform.problem.controller;

import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.repository.ProblemRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/problems")
@RequiredArgsConstructor
public class ProblemController {

    private final ProblemRepository problemRepository;

    @GetMapping
    public ResponseEntity<List<Problem>> getAllProblems() {
        return ResponseEntity.ok(problemRepository.findAll());
    }

    @GetMapping("/{id}")
    public ResponseEntity<Problem> getProblemById(@PathVariable UUID id) {
        return problemRepository.findById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
