package com.codex.platform.auth.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class ResetPasswordRequest {
    @NotBlank(message = "Password is required")
    @Size(min = 8, max = 72, message = "Password must be 8-72 characters")
    @Pattern(
            regexp = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).+$",
            message = "Password must include upper, lower, and a digit")
    private String password;
}
