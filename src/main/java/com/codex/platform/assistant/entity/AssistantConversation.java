package com.codex.platform.assistant.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

/**
 * One CodeBot chat session: a user's conversation about a specific problem.
 * Messages ({@link AssistantMessage}) hang off this by {@code conversationId}.
 */
@Entity
@Table(name = "assistant_conversations", indexes = {
        @Index(name = "idx_assistant_conv_user_problem", columnList = "userId,problemId")
})
@Data
@NoArgsConstructor
public class AssistantConversation {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private UUID userId;

    @Column(nullable = false)
    private UUID problemId;

    @Column(length = 255)
    private String title;

    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    @PrePersist
    void onCreate() {
        Instant now = Instant.now();
        this.createdAt = now;
        this.updatedAt = now;
    }

    @PreUpdate
    void onUpdate() {
        this.updatedAt = Instant.now();
    }
}
