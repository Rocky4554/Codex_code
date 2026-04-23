package com.codex.platform.user.repository;

import com.codex.platform.user.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import org.springframework.data.domain.Pageable;
import java.time.LocalDateTime;
import java.util.Optional;
import java.util.List;
import java.util.UUID;

@Repository
public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByUsername(String username);

    Optional<User> findByEmail(String email);

    boolean existsByUsername(String username);

    boolean existsByEmail(String email);

    List<User> findAllByOrderByTotalScoreDescSolvedHardDescCreatedAtAsc(Pageable pageable);

    long countByTotalScoreGreaterThan(int totalScore);

    long countByTotalScoreAndSolvedHardGreaterThan(int totalScore, int solvedHard);

    long countByTotalScoreAndSolvedHardAndCreatedAtBefore(int totalScore, int solvedHard, LocalDateTime createdAt);
}
