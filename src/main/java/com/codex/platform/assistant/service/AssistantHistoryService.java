package com.codex.platform.assistant.service;

import com.codex.platform.assistant.dto.ConversationDto;
import com.codex.platform.assistant.dto.MessageDto;
import com.codex.platform.assistant.entity.AssistantAction;
import com.codex.platform.assistant.entity.AssistantConversation;
import com.codex.platform.assistant.entity.AssistantMessage;
import com.codex.platform.assistant.entity.MessageRole;
import com.codex.platform.assistant.repository.AssistantConversationRepository;
import com.codex.platform.assistant.repository.AssistantMessageRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
import java.util.UUID;

/**
 * All Postgres persistence for CodeBot conversations and messages.
 *
 * <p>Kept separate from {@link AssistantService} on purpose: the streaming flow
 * runs on a background thread, and Spring's {@code @Transactional} only applies
 * when these methods are called through the proxy (i.e. from another bean). So
 * the streaming service calls into this bean for every DB touch.
 */
@Service
@RequiredArgsConstructor
public class AssistantHistoryService {

    private final AssistantConversationRepository conversationRepository;
    private final AssistantMessageRepository messageRepository;

    /** Reuse the given conversation (verifying ownership) or start a new one. */
    @Transactional
    public UUID startOrGet(UUID userId, UUID problemId, UUID conversationId, String newTitle) {
        if (conversationId != null) {
            AssistantConversation existing = conversationRepository.findById(conversationId)
                    .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Conversation not found"));
            if (!existing.getUserId().equals(userId)) {
                throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Not your conversation");
            }
            existing.setUpdatedAt(java.time.Instant.now());
            conversationRepository.save(existing);
            return existing.getId();
        }

        AssistantConversation conversation = new AssistantConversation();
        conversation.setUserId(userId);
        conversation.setProblemId(problemId);
        conversation.setTitle(truncate(newTitle, 255));
        return conversationRepository.save(conversation).getId();
    }

    @Transactional
    public void addMessage(UUID conversationId, MessageRole role, AssistantAction kind, String content) {
        AssistantMessage message = new AssistantMessage();
        message.setConversationId(conversationId);
        message.setRole(role);
        message.setKind(kind);
        message.setContent(content == null ? "" : content);
        messageRepository.save(message);
    }

    /** Prior messages of a conversation, oldest first (used to rebuild chat context). */
    @Transactional(readOnly = true)
    public List<AssistantMessage> rawMessages(UUID conversationId) {
        return messageRepository.findByConversationIdOrderByCreatedAtAsc(conversationId);
    }

    @Transactional(readOnly = true)
    public List<ConversationDto> conversations(UUID userId, UUID problemId) {
        return conversationRepository.findByUserIdAndProblemIdOrderByUpdatedAtDesc(userId, problemId).stream()
                .map(c -> ConversationDto.builder()
                        .id(c.getId())
                        .title(c.getTitle())
                        .updatedAt(c.getUpdatedAt())
                        .build())
                .toList();
    }

    @Transactional(readOnly = true)
    public List<MessageDto> messages(UUID userId, UUID conversationId) {
        AssistantConversation conversation = conversationRepository.findById(conversationId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Conversation not found"));
        if (!conversation.getUserId().equals(userId)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Not your conversation");
        }
        return messageRepository.findByConversationIdOrderByCreatedAtAsc(conversationId).stream()
                .map(m -> MessageDto.builder()
                        .id(m.getId())
                        .role(m.getRole())
                        .kind(m.getKind())
                        .content(m.getContent())
                        .createdAt(m.getCreatedAt())
                        .build())
                .toList();
    }

    private String truncate(String s, int max) {
        if (s == null) return null;
        s = s.strip();
        return s.length() <= max ? s : s.substring(0, max);
    }
}
