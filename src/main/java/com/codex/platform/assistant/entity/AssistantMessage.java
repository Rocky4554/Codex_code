package com.codex.platform.assistant.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

/** A single message inside an {@link AssistantConversation}. */
@Entity
@Table(name = "assistant_messages", indexes = {
        @Index(name = "idx_assistant_msg_conversation", columnList = "conversationId,createdAt")
})
@Data
@NoArgsConstructor
public class AssistantMessage {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private UUID conversationId;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 16)
    private MessageRole role;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 16)
    private AssistantAction kind;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String content;

    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    @PrePersist
    void onCreate() {
        this.createdAt = Instant.now();
    }
}
