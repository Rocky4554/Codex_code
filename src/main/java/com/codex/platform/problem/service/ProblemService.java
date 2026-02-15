package com.codex.platform.problem.service;

import com.codex.platform.problem.dto.ProblemRequest;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.repository.ProblemRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class ProblemService {

    private final ProblemRepository problemRepository;

    public Page<Problem> getAllProblems(Pageable pageable) {
        return problemRepository.findAll(Objects.requireNonNull(pageable, "Pageable is required"));
    }

    public Optional<Problem> getProblemById(UUID id) {
        return problemRepository.findById(Objects.requireNonNull(id, "Problem ID is required"));
    }

    @Transactional
    public Problem createProblem(ProblemRequest request) {
        Problem problem = new Problem();
        applyRequest(problem, request);
        return problemRepository.save(problem);
    }

    @Transactional
    public Problem updateProblem(UUID id, ProblemRequest request) {
        Problem problem = problemRepository.findById(Objects.requireNonNull(id, "Problem ID is required"))
                .orElseThrow(() -> new IllegalArgumentException("Problem not found"));

        applyRequest(problem, request);
        return problemRepository.save(Objects.requireNonNull(problem, "Problem is required"));
    }

    @Transactional
    public void deleteProblem(UUID id) {
        UUID problemId = Objects.requireNonNull(id, "Problem ID is required");
        if (!problemRepository.existsById(problemId)) {
            throw new IllegalArgumentException("Problem not found");
        }
        problemRepository.deleteById(problemId);
    }

    private void applyRequest(Problem problem, ProblemRequest request) {
        problem.setTitle(request.getTitle().trim());
        problem.setDescription(request.getDescription().trim());
        problem.setDifficulty(request.getDifficulty());
        problem.setTimeLimitMs(request.getTimeLimitMs());
        problem.setMemoryLimitMb(request.getMemoryLimitMb());
    }
}
