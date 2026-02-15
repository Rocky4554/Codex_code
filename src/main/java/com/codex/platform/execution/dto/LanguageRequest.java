package com.codex.platform.execution.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class LanguageRequest {
    @NotBlank(message = "Name is required")
    @Size(max = 50, message = "Name must not exceed 50 characters")
    private String name;

    @NotBlank(message = "Version is required")
    @Size(max = 50, message = "Version must not exceed 50 characters")
    private String version;

    @NotBlank(message = "Docker image is required")
    @Size(max = 255, message = "Docker image must not exceed 255 characters")
    private String dockerImage;

    @NotBlank(message = "File extension is required")
    @Size(max = 20, message = "File extension must not exceed 20 characters")
    private String fileExtension;

    @Size(max = 500, message = "Compile command must not exceed 500 characters")
    private String compileCommand;

    @NotBlank(message = "Execute command is required")
    @Size(max = 500, message = "Execute command must not exceed 500 characters")
    private String executeCommand;
}
