package com.codex.platform.submission.repository;

import com.codex.platform.submission.entity.SubmissionResult;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.UUID;

@Repository
public interface SubmissionResultRepository extends JpaRepository<SubmissionResult, UUID> {
}
