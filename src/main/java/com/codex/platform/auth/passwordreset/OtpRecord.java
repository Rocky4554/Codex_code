package com.codex.platform.auth.passwordreset;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class OtpRecord {
    private String otpHash;
    private int attempts;
    private Instant createdAt;
}
