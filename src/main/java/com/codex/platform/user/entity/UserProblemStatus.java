package com.codex.platform.user.entity;

import com.codex.platform.common.enums.UserProblemStatusEnum;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "user_problem_status")
@Data
@NoArgsConstructor
@AllArgsConstructor
@IdClass(UserProblemStatus.UserProblemStatusId.class)
public class UserProblemStatus {

    @Id
    private UUID userId;

    @Id
    private UUID problemId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private UserProblemStatusEnum status;

    @Column
    private LocalDateTime solvedAt;

    // Composite Key Class
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class UserProblemStatusId implements Serializable {
        private UUID userId;
        private UUID problemId;
    }
}
