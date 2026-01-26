package com.codex.platform.user.repository;

import com.codex.platform.user.entity.UserProblemStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface UserProblemStatusRepository
        extends JpaRepository<UserProblemStatus, UserProblemStatus.UserProblemStatusId> {
    Optional<UserProblemStatus> findByUserIdAndProblemId(UUID userId, UUID problemId);

    List<UserProblemStatus> findByUserId(UUID userId);
}
