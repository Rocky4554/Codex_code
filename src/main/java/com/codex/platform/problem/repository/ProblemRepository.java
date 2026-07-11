package com.codex.platform.problem.repository;

import com.codex.platform.problem.entity.Problem;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

@Repository
public interface ProblemRepository extends JpaRepository<Problem, UUID> {
    Optional<Problem> findByTitleIgnoreCase(String title);

    /** Catalog problems: inCatalog true, or null for rows created before the column existed. */
    @Query("SELECT p FROM Problem p WHERE p.inCatalog = true OR p.inCatalog IS NULL")
    Page<Problem> findCatalogProblems(Pageable pageable);
}
