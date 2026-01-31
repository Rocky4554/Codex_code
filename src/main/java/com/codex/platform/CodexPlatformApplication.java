package com.codex.platform;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

import java.util.TimeZone;

@SpringBootApplication
@EnableAsync
public class CodexPlatformApplication {

    public static void main(String[] args) {
        // Avoid PostgreSQL JDBC sending an unsupported JVM default timezone (e.g. "Asia/Calcutta")
        // during connection startup.
        System.setProperty("user.timezone", "UTC");
        TimeZone.setDefault(TimeZone.getTimeZone("UTC"));
        SpringApplication.run(CodexPlatformApplication.class, args);
    }
}
