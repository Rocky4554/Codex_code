package com.codex.platform.auth.controller;

import com.codex.platform.auth.dto.AuthResponse;
import com.codex.platform.auth.dto.ForgotPasswordRequest;
import com.codex.platform.auth.dto.LoginRequest;
import com.codex.platform.auth.dto.MessageResponse;
import com.codex.platform.auth.dto.RegisterRequest;
import com.codex.platform.auth.dto.ResetPasswordRequest;
import com.codex.platform.auth.dto.VerifyOtpRequest;
import com.codex.platform.auth.dto.VerifyOtpResponse;
import com.codex.platform.auth.passwordreset.PasswordResetService;
import com.codex.platform.auth.service.AuthService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {

    private final AuthService authService;
    private final PasswordResetService passwordResetService;

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(@Valid @RequestBody RegisterRequest request) {
        return ResponseEntity.ok(authService.register(request));
    }

    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.login(request));
    }

    @PostMapping("/forgot-password")
    public ResponseEntity<MessageResponse> forgotPassword(@Valid @RequestBody ForgotPasswordRequest request) {
        return ResponseEntity.ok(passwordResetService.forgotPassword(request.getEmail()));
    }

    @PostMapping("/verify-otp")
    public ResponseEntity<VerifyOtpResponse> verifyOtp(@Valid @RequestBody VerifyOtpRequest request) {
        return ResponseEntity.ok(passwordResetService.verifyOtp(request.getEmail(), request.getOtp()));
    }

    @PostMapping("/reset-password")
    public ResponseEntity<MessageResponse> resetPassword(
            @RequestHeader(value = "Authorization", required = false) String authorization,
            @Valid @RequestBody ResetPasswordRequest request) {
        String token = extractBearer(authorization);
        return ResponseEntity.ok(passwordResetService.resetPassword(token, request.getPassword()));
    }

    private static String extractBearer(String authorization) {
        if (authorization == null || !authorization.startsWith("Bearer ")) {
            return null;
        }
        return authorization.substring(7).trim();
    }
}
