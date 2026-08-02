package com.codex.platform.auth.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class VerifyOtpResponse {
    private String resetToken;
    private String message;
}
