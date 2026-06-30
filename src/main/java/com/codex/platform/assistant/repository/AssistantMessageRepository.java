package com.codex.platform.assistant.repository;

import com.codex.platform.assistant.entity.AssistantMessage;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface AssistantMessageRepository extends JpaRepository<AssistantMessage, UUID> {
    List<AssistantMessage> findByConversationIdOrderByCreatedAtAsc(UUID conversationId);
}
