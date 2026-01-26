package com.codex.platform;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class CodexPlatformApplication {

    public static void main(String[] args) {
        SpringApplication.run(CodexPlatformApplication.class, args);
    }
}
