package com.codex.platform.auth.service;

import com.codex.platform.auth.dto.AuthResponse;
import com.codex.platform.auth.dto.LoginRequest;
import com.codex.platform.auth.dto.RegisterRequest;
import com.codex.platform.auth.util.JwtUtil;
import com.codex.platform.user.entity.User;
import com.codex.platform.user.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByUsername(request.getUsername())) {
            throw new IllegalArgumentException("Username already exists");
        }
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new IllegalArgumentException("Email already exists");
        }

        User user = new User();
        user.setUsername(request.getUsername());
        user.setEmail(request.getEmail());
        user.setPasswordHash(passwordEncoder.encode(request.getPassword()));
        user.setTokenVersion(0);

        User savedUser = userRepository.save(user);

        String token = jwtUtil.generateToken(
                savedUser.getId(),
                savedUser.getUsername(),
                savedUser.getRole(),
                savedUser.getTokenVersion() == null ? 0 : savedUser.getTokenVersion());

        return new AuthResponse(token, savedUser.getId(), savedUser.getUsername(), savedUser.getEmail(), savedUser.getRole());
    }

    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new IllegalArgumentException("Invalid username or password"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new IllegalArgumentException("Invalid username or password");
        }

        String token = jwtUtil.generateToken(
                user.getId(),
                user.getUsername(),
                user.getRole(),
                user.getTokenVersion() == null ? 0 : user.getTokenVersion());

        return new AuthResponse(token, user.getId(), user.getUsername(), user.getEmail(), user.getRole());
    }
}
