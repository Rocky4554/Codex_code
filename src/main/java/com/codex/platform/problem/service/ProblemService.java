package com.codex.platform.problem.service;

import com.codex.platform.problem.dto.ProblemDetailResponse;
import com.codex.platform.problem.dto.ProblemRequest;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.ProblemExample;
import com.codex.platform.problem.repository.ProblemExampleRepository;
import com.codex.platform.problem.repository.ProblemRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Collections;
import java.util.List;
import java.util.Objects;
import java.util.Optional;
import java.util.UUID;

@Service
@RequiredArgsConstructor
@Slf4j
public class ProblemService {

    private final ProblemRepository problemRepository;
    private final ProblemExampleRepository exampleRepository;
    private final ObjectMapper objectMapper;

    public Page<Problem> getAllProblems(Pageable pageable) {
        return problemRepository.findAll(Objects.requireNonNull(pageable, "Pageable is required"));
    }

    public Optional<ProblemDetailResponse> getProblemDetailById(UUID id) {
        return problemRepository.findById(Objects.requireNonNull(id, "Problem ID is required"))
                .map(this::toDetail);
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
        return problemRepository.save(problem);
    }

    @Transactional
    public void deleteProblem(UUID id) {
        UUID problemId = Objects.requireNonNull(id, "Problem ID is required");
        if (!problemRepository.existsById(problemId)) {
            throw new IllegalArgumentException("Problem not found");
        }
        problemRepository.deleteById(problemId);
    }

    public ProblemDetailResponse toDetail(Problem problem) {
        List<ProblemExample> examples = exampleRepository
                .findByProblemIdOrderByDisplayOrderAsc(problem.getId());

        return ProblemDetailResponse.builder()
                .id(problem.getId())
                .title(problem.getTitle())
                .description(problem.getDescription())
                .difficulty(problem.getDifficulty())
                .timeLimitMs(problem.getTimeLimitMs())
                .memoryLimitMb(problem.getMemoryLimitMb())
                .orderNum(problem.getOrderNum())
                .constraints(deserializeList(problem.getConstraintsJson()))
                .topics(deserializeList(problem.getTopicsJson()))
                .examples(examples.stream()
                        .map(e -> ProblemDetailResponse.ExampleDto.builder()
                                .id(e.getId())
                                .input(e.getInput())
                                .output(e.getOutput())
                                .explanation(e.getExplanation())
                                .build())
                        .toList())
                .build();
    }

    private void applyRequest(Problem problem, ProblemRequest request) {
        problem.setTitle(request.getTitle().trim());
        problem.setDescription(request.getDescription().trim());
        problem.setDifficulty(request.getDifficulty());
        problem.setTimeLimitMs(request.getTimeLimitMs());
        problem.setMemoryLimitMb(request.getMemoryLimitMb());
        problem.setOrderNum(request.getOrderNum());
        problem.setConstraintsJson(serializeList(request.getConstraints()));
        problem.setTopicsJson(serializeList(request.getTopics()));
    }

    private String serializeList(List<String> list) {
        if (list == null || list.isEmpty()) return null;
        try {
            return objectMapper.writeValueAsString(list);
        } catch (Exception e) {
            log.warn("Failed to serialize list: {}", e.getMessage());
            return null;
        }
    }

    private List<String> deserializeList(String json) {
        if (json == null || json.isBlank()) return Collections.emptyList();
        try {
            return objectMapper.readValue(json, new TypeReference<List<String>>() {});
        } catch (Exception e) {
            log.warn("Failed to deserialize list: {}", e.getMessage());
            return Collections.emptyList();
        }
    }
}
