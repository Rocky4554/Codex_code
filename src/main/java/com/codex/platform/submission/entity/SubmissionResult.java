package com.codex.platform.submission.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Entity
@Table(name = "submission_results")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class SubmissionResult {

    @Id
    private UUID submissionId;

    @Column
    private Long executionTimeMs;

    @Column
    private Long memoryUsedMb;

    @Column
    private Integer passedTestCases;

    @Column
    private Integer totalTestCases;

    @Column(columnDefinition = "TEXT")
    private String stdout;

    @Column(columnDefinition = "TEXT")
    private String stderr;
}
