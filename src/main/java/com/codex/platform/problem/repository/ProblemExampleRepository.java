package com.codex.platform.problem.repository;

import com.codex.platform.problem.entity.ProblemExample;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ProblemExampleRepository extends JpaRepository<ProblemExample, UUID> {
    List<ProblemExample> findByProblemIdOrderByDisplayOrderAsc(UUID problemId);
    void deleteByProblemId(UUID problemId);
}
