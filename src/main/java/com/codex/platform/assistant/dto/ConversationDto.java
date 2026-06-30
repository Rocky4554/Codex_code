package com.codex.platform.assistant.dto;

import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.UUID;

/** Summary of a conversation for the history list. */
@Data
@Builder
public class ConversationDto {
    private UUID id;
    private String title;
    private Instant updatedAt;
}
