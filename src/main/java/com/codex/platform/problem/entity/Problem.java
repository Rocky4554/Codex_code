package com.codex.platform.problem.entity;

import com.codex.platform.common.enums.ProblemDifficulty;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Entity
@Table(name = "problems")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Problem {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ProblemDifficulty difficulty;

    @Column(nullable = false)
    private Integer timeLimitMs;

    @Column(nullable = false)
    private Integer memoryLimitMb;

    @Column
    private Integer orderNum;

    // JSON arrays stored as TEXT: ["constraint1", "constraint2"]
    @Column(columnDefinition = "TEXT")
    private String constraintsJson;

    // JSON arrays stored as TEXT: ["Array", "Hash Table"]
    @Column(columnDefinition = "TEXT")
    private String topicsJson;
}
