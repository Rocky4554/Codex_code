package com.codex.platform.submission.repository;

import com.codex.platform.submission.entity.Submission;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface SubmissionRepository extends JpaRepository<Submission, UUID> {
    List<Submission> findByUserId(UUID userId);

    Page<Submission> findByUserId(UUID userId, Pageable pageable);

    List<Submission> findByProblemId(UUID problemId);

    List<Submission> findByUserIdAndProblemId(UUID userId, UUID problemId);
}
