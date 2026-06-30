package com.codex.platform.assistant.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

import java.util.UUID;

/** Request bodies for the CodeBot streaming endpoints. */
public class AssistantRequests {

    /** Explain — only needs the (optional) conversation to append to. */
    @Data
    public static class ExplainRequest {
        private UUID conversationId;
    }

    /** Generate a starter/solution in the chosen language. */
    @Data
    public static class GenerateRequest {
        @NotBlank(message = "language is required")
        private String language;
        private UUID conversationId;
    }

    /** Review the user's current editor code. */
    @Data
    public static class ReviewRequest {
        @NotBlank(message = "language is required")
        private String language;
        @NotBlank(message = "code is required")
        private String code;
        private UUID conversationId;
    }

    /** Free-form chat question. */
    @Data
    public static class ChatRequest {
        @NotBlank(message = "message is required")
        private String message;
        private UUID conversationId;
    }
}
