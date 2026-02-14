package com.codex.platform.user.controller;

import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.repository.SubmissionRepository;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.entity.UserProblemStatus;
import com.codex.platform.user.repository.UserProblemStatusRepository;
import com.codex.platform.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.web.PageableDefault;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/user")
@RequiredArgsConstructor
public class UserController {

    private final UserRepository userRepository;
    private final SubmissionRepository submissionRepository;
    private final UserProblemStatusRepository userProblemStatusRepository;

    @GetMapping("/profile")
    public ResponseEntity<User> getProfile() {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        return userRepository.findById(userId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/submissions")
    public ResponseEntity<Page<Submission>> getMySubmissions(
            @PageableDefault(size = 20) Pageable pageable) {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        return ResponseEntity.ok(submissionRepository.findByUserId(userId, pageable));
    }

    @GetMapping("/problems")
    public ResponseEntity<List<UserProblemStatus>> getMyProblems() {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        return ResponseEntity.ok(userProblemStatusRepository.findByUserId(userId));
    }
}
