package com.codex.platform.assistant.controller;

import com.codex.platform.assistant.dto.AssistantRequests.*;
import com.codex.platform.assistant.dto.ConversationDto;
import com.codex.platform.assistant.dto.MessageDto;
import com.codex.platform.assistant.service.AssistantHistoryService;
import com.codex.platform.assistant.service.AssistantQuotaService;
import com.codex.platform.assistant.service.AssistantService;
import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * CodeBot endpoints. All require an authenticated user (enforced by Spring
 * Security's {@code anyRequest().authenticated()}); the streaming actions also
 * consume the per-user daily quota.
 *
 * <p>The four action endpoints return an {@link SseEmitter} (text/event-stream).
 * Each SSE frame is a JSON line:
 * <pre>
 *   {"type":"meta","conversationId":"..."}
 *   {"type":"token","text":"partial answer"}
 *   {"type":"done","conversationId":"...","remaining":42}
 *   {"type":"error","status":429,"message":"..."}
 * </pre>
 */
@RestController
@RequiredArgsConstructor
public class AssistantController {

    private static final long SSE_TIMEOUT_MS = 120_000L;

    private final AssistantService assistantService;
    private final AssistantHistoryService historyService;
    private final AssistantQuotaService quotaService;

    // ── Streaming actions ──────────────────────────────────────────────────────

    @PostMapping(value = "/api/problems/{problemId}/assistant/explain", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter explain(@PathVariable UUID problemId, @RequestBody(required = false) ExplainRequest req) {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        SseEmitter emitter = new SseEmitter(SSE_TIMEOUT_MS);
        assistantService.explain(emitter, userId, problemId, req != null ? req.getConversationId() : null);
        return emitter;
    }

    @PostMapping(value = "/api/problems/{problemId}/assistant/generate", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter generate(@PathVariable UUID problemId, @Valid @RequestBody GenerateRequest req) {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        SseEmitter emitter = new SseEmitter(SSE_TIMEOUT_MS);
        assistantService.generate(emitter, userId, problemId, req.getLanguage(), req.getConversationId());
        return emitter;
    }

    @PostMapping(value = "/api/problems/{problemId}/assistant/review", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter review(@PathVariable UUID problemId, @Valid @RequestBody ReviewRequest req) {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        SseEmitter emitter = new SseEmitter(SSE_TIMEOUT_MS);
        assistantService.review(emitter, userId, problemId, req.getLanguage(), req.getCode(), req.getConversationId());
        return emitter;
    }

    @PostMapping(value = "/api/problems/{problemId}/assistant/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chat(@PathVariable UUID problemId, @Valid @RequestBody ChatRequest req) {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        SseEmitter emitter = new SseEmitter(SSE_TIMEOUT_MS);
        assistantService.chat(emitter, userId, problemId, req.getMessage(), req.getConversationId());
        return emitter;
    }

    // ── History (durable, from Postgres) ───────────────────────────────────────

    @GetMapping("/api/problems/{problemId}/assistant/conversations")
    public List<ConversationDto> conversations(@PathVariable UUID problemId) {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        return historyService.conversations(userId, problemId);
    }

    @GetMapping("/api/assistant/conversations/{conversationId}/messages")
    public List<MessageDto> messages(@PathVariable UUID conversationId) {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        return historyService.messages(userId, conversationId);
    }

    @GetMapping("/api/assistant/quota")
    public Map<String, Integer> quota() {
        UUID userId = JwtAuthenticationFilter.getCurrentUserId();
        return Map.of("remaining", quotaService.remaining(userId), "dailyLimit", quotaService.dailyLimit());
    }
}
