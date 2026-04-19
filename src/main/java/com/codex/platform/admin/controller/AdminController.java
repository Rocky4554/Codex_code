package com.codex.platform.admin.controller;

import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import com.codex.platform.submission.dto.SubmissionResponse;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.entity.SubmissionResult;
import com.codex.platform.submission.repository.SubmissionRepository;
import com.codex.platform.submission.repository.SubmissionResultRepository;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.entity.UserProblemStatus;
import com.codex.platform.user.repository.UserProblemStatusRepository;
import com.codex.platform.user.repository.UserRepository;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.http.HttpStatus;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {

    private final UserRepository userRepository;
    private final SubmissionRepository submissionRepository;
    private final SubmissionResultRepository submissionResultRepository;
    private final UserProblemStatusRepository userProblemStatusRepository;

    @GetMapping("/users")
    public ResponseEntity<List<UserSummary>> listUsers() {
        requireAdmin();
        List<User> users = userRepository.findAll();
        List<UserSummary> summaries = users.stream().map(u -> {
            long solvedCount = userProblemStatusRepository.countByUserIdAndStatus(
                    u.getId(), com.codex.platform.common.enums.UserProblemStatusEnum.SOLVED);
            long submissionCount = submissionRepository.countByUserId(u.getId());
            return UserSummary.builder()
                    .id(u.getId())
                    .username(u.getUsername())
                    .email(u.getEmail())
                    .role(u.getRole())
                    .createdAt(u.getCreatedAt())
                    .solvedCount(solvedCount)
                    .submissionCount(submissionCount)
                    .build();
        }).toList();
        return ResponseEntity.ok(summaries);
    }

    @GetMapping("/users/{userId}/submissions")
    public ResponseEntity<List<SubmissionResponse>> getUserSubmissions(@PathVariable UUID userId) {
        requireAdmin();
        List<Submission> submissions = submissionRepository.findByUserIdOrderByCreatedAtDesc(userId);
        List<SubmissionResponse> responses = submissions.stream().map(sub -> {
            SubmissionResponse.SubmissionResponseBuilder builder = SubmissionResponse.builder()
                    .id(sub.getId())
                    .userId(sub.getUserId())
                    .problemId(sub.getProblemId())
                    .languageId(sub.getLanguageId())
                    .status(sub.getStatus())
                    .createdAt(sub.getCreatedAt())
                    .sourceCode(sub.getSourceCode());
            submissionResultRepository.findById(sub.getId()).ifPresent(r -> builder
                    .passedTestCases(r.getPassedTestCases())
                    .totalTestCases(r.getTotalTestCases())
                    .executionTimeMs(r.getExecutionTimeMs())
                    .stdout(r.getStdout())
                    .stderr(r.getStderr()));
            return builder.build();
        }).toList();
        return ResponseEntity.ok(responses);
    }

    @GetMapping("/users/{userId}/problems")
    public ResponseEntity<List<UserProblemStatus>> getUserProblems(@PathVariable UUID userId) {
        requireAdmin();
        return ResponseEntity.ok(userProblemStatusRepository.findByUserId(userId));
    }

    @PutMapping("/users/{userId}/role")
    public ResponseEntity<Void> setUserRole(@PathVariable UUID userId, @RequestBody RoleRequest req) {
        requireAdmin();
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "User not found"));
        user.setRole(req.getRole());
        userRepository.save(user);
        return ResponseEntity.ok().build();
    }

    private void requireAdmin() {
        String role = JwtAuthenticationFilter.getCurrentUserRole();
        if (!"ADMIN".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Admin access required");
        }
    }

    @Data
    static class RoleRequest {
        private String role;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    static class UserSummary {
        private UUID id;
        private String username;
        private String email;
        private String role;
        private LocalDateTime createdAt;
        private long solvedCount;
        private long submissionCount;
    }
}
