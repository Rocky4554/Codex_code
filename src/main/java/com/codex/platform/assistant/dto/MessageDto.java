package com.codex.platform.assistant.dto;

import com.codex.platform.assistant.entity.AssistantAction;
import com.codex.platform.assistant.entity.MessageRole;
import lombok.Builder;
import lombok.Data;

import java.time.Instant;
import java.util.UUID;

/** A single stored message, returned when re-opening a past conversation. */
@Data
@Builder
public class MessageDto {
    private UUID id;
    private MessageRole role;
    private AssistantAction kind;
    private String content;
    private Instant createdAt;
}
