package com.codex.platform.assistant.repository;

import com.codex.platform.assistant.entity.AssistantConversation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface AssistantConversationRepository extends JpaRepository<AssistantConversation, UUID> {
    List<AssistantConversation> findByUserIdAndProblemIdOrderByUpdatedAtDesc(UUID userId, UUID problemId);
}
