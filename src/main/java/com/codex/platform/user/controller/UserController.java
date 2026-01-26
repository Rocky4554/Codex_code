package com.codex.platform.user.controller;

import com.codex.platform.auth.util.JwtUtil;
import com.codex.platform.submission.entity.Submission;
import com.codex.platform.submission.repository.SubmissionRepository;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.entity.UserProblemStatus;
import com.codex.platform.user.repository.UserProblemStatusRepository;
import com.codex.platform.user.repository.UserRepository;
import jakarta.servlet.http.HttpServletRequest;
import lombok.RequiredArgsConstructor;
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
    private final JwtUtil jwtUtil;

    @GetMapping("/profile")
    public ResponseEntity<User> getProfile(HttpServletRequest request) {
        UUID userId = extractUserIdFromRequest(request);
        return userRepository.findById(userId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping("/submissions")
    public ResponseEntity<List<Submission>> getMySubmissions(HttpServletRequest request) {
        UUID userId = extractUserIdFromRequest(request);
        return ResponseEntity.ok(submissionRepository.findByUserId(userId));
    }

    @GetMapping("/problems")
    public ResponseEntity<List<UserProblemStatus>> getMyProblems(HttpServletRequest request) {
        UUID userId = extractUserIdFromRequest(request);
        return ResponseEntity.ok(userProblemStatusRepository.findByUserId(userId));
    }

    private UUID extractUserIdFromRequest(HttpServletRequest request) {
        String authHeader = request.getHeader("Authorization");
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String token = authHeader.substring(7);
            return jwtUtil.extractUserId(token);
        }
        throw new IllegalArgumentException("Invalid authorization header");
    }
}
