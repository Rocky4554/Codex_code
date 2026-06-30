package com.codex.platform.assistant.service;

import com.codex.platform.ai.GeminiClient;
import com.codex.platform.assistant.entity.AssistantAction;
import com.codex.platform.assistant.entity.AssistantMessage;
import com.codex.platform.assistant.entity.MessageRole;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.ProblemExample;
import com.codex.platform.problem.repository.ProblemExampleRepository;
import com.codex.platform.problem.repository.ProblemRepository;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.io.UncheckedIOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * CodeBot orchestration: for each action (explain / generate / review / chat) it
 * checks the daily quota, grounds Gemini in the problem, streams the answer to the
 * browser via an {@link SseEmitter}, and persists both the user prompt and the
 * assistant reply to Postgres.
 *
 * <p>Streaming runs on a dedicated thread pool because {@code GeminiClient.streamGenerate}
 * blocks until the SSE stream ends; the controller returns the emitter immediately.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AssistantService {

    private final GeminiClient geminiClient;
    private final AssistantHistoryService history;
    private final AssistantQuotaService quotaService;
    private final ProblemRepository problemRepository;
    private final ProblemExampleRepository exampleRepository;
    private final ObjectMapper objectMapper;

    private final ExecutorService streamExecutor = Executors.newFixedThreadPool(8);

    private static final String PERSONA = """
            You are CodeBot, a helpful coding assistant embedded in an online judge.
            You help the user understand and solve ONE specific problem. Keep answers
            focused and use clear Markdown (headings, lists, fenced code blocks).
            """;

    // ── Public actions ─────────────────────────────────────────────────────────

    public void explain(SseEmitter emitter, UUID userId, UUID problemId, UUID conversationId) {
        ProblemContext ctx = loadContext(problemId);
        String system = PERSONA + "\nPROBLEM:\n" + ctx.text + """

                Task: Explain this problem to a beginner. Cover: what it asks, the input/output
                format, and the core idea to solve it. Be concise and friendly. Do NOT give full
                solution code unless asked.
                """;
        run(emitter, userId, problemId, conversationId, AssistantAction.EXPLAIN,
                "Explain this problem",
                "Explain this problem to me simply.",
                system, false, "Explain: " + ctx.title);
    }

    public void generate(SseEmitter emitter, UUID userId, UUID problemId, String language, UUID conversationId) {
        ProblemContext ctx = loadContext(problemId);
        String system = PERSONA + "\nPROBLEM:\n" + ctx.text + """

                Task: Write a correct, COMPLETE, modern, idiomatic, and OPTIMISED solution program in %s.

                Requirements:
                - Use an efficient algorithm and data structures suitable for the constraints
                  (do not use needless brute force when a better approach fits the limits).
                - Write clean, modern, idiomatic code for the language.
                - The judge runs the program AS-IS: it must read ALL input from standard input
                  and print ONLY the answer to standard output, exactly following the problem's
                  Input/Output format. Do NOT write a class/method template that is never called.
                - C++: begin with `#include <bits/stdc++.h>` and `using namespace std;`, and add
                  `ios_base::sync_with_stdio(false); cin.tie(nullptr);` in main for fast I/O.
                - Python: read input via sys.stdin; avoid slow patterns inside loops.
                - Java: read with a BufferedReader and build output with a StringBuilder.
                - JavaScript: read all of stdin (e.g. require('fs').readFileSync(0,'utf8')) and
                  print with console.log.

                Return the program in a single fenced code block, with a one-line explanation above it.
                """.formatted(language);
        run(emitter, userId, problemId, conversationId, AssistantAction.GENERATE,
                "Generate a solution in " + language,
                "Write a complete " + language + " solution program for this problem.",
                system, false, "Generate (" + language + "): " + ctx.title);
    }

    public void review(SseEmitter emitter, UUID userId, UUID problemId, String language, String code, UUID conversationId) {
        ProblemContext ctx = loadContext(problemId);
        String system = PERSONA + "\nPROBLEM:\n" + ctx.text + """

                Task: Review the user's solution for THIS problem. Give: (1) a one-line verdict,
                (2) a list of concrete issues as "Line N: problem -> fix" (use real line numbers
                from their code), (3) edge cases they may miss, (4) time/space complexity, and
                (5) improvements. Be specific. Markdown.
                """;
        String prompt = "Review my solution. Here is my " + language + " code:\n```" + language + "\n" + code + "\n```";
        run(emitter, userId, problemId, conversationId, AssistantAction.REVIEW,
                "Review my " + language + " code",
                prompt,
                system, false, "Review (" + language + "): " + ctx.title);
    }

    public void chat(SseEmitter emitter, UUID userId, UUID problemId, String message, UUID conversationId) {
        ProblemContext ctx = loadContext(problemId);
        String system = PERSONA + "\nPROBLEM:\n" + ctx.text + """

                Task: Answer the user's questions about understanding or solving THIS problem.
                If the user's message is unrelated to this problem or to programming, reply with
                EXACTLY this sentence and nothing else: "This question is not related to the problem."
                """;
        run(emitter, userId, problemId, conversationId, AssistantAction.CHAT,
                message,
                message,
                system, true, truncate(message, 60));
    }

    // ── Core streaming + persistence ───────────────────────────────────────────

    private void run(SseEmitter emitter, UUID userId, UUID problemId, UUID conversationId,
                     AssistantAction action, String storedUserMessage, String promptText,
                     String systemInstruction, boolean includeHistory, String newTitle) {

        streamExecutor.submit(() -> {
            try {
                quotaService.consume(userId); // throws 429 when out of quota

                UUID convId = history.startOrGet(userId, problemId, conversationId, newTitle);
                emit(emitter, Map.of("type", "meta", "conversationId", convId.toString()));

                List<Map<String, Object>> contents = new ArrayList<>();
                if (includeHistory) {
                    for (AssistantMessage prior : history.rawMessages(convId)) {
                        contents.add(turn(mapRole(prior.getRole()), prior.getContent()));
                    }
                }
                contents.add(turn("user", promptText));

                history.addMessage(convId, MessageRole.USER, action, storedUserMessage);

                StringBuilder full = new StringBuilder();
                geminiClient.streamGenerate(systemInstruction, contents, chunk -> {
                    full.append(chunk);
                    emit(emitter, Map.of("type", "token", "text", chunk));
                });

                history.addMessage(convId, MessageRole.ASSISTANT, action, full.toString());
                emit(emitter, Map.of("type", "done", "conversationId", convId.toString(),
                        "remaining", quotaService.remaining(userId)));
                emitter.complete();

            } catch (ResponseStatusException rse) {
                sendError(emitter, rse.getStatusCode().value(),
                        rse.getReason() != null ? rse.getReason() : "Request failed");
            } catch (UncheckedIOException disconnected) {
                // Client closed the stream — nothing to send, just stop.
                log.debug("Assistant stream client disconnected: {}", disconnected.getMessage());
                safeComplete(emitter);
            } catch (Exception e) {
                log.error("Assistant stream failed", e);
                sendError(emitter, 500, "Assistant failed: " + e.getMessage());
            }
        });
    }

    // ── Helpers ────────────────────────────────────────────────────────────────

    private void emit(SseEmitter emitter, Map<String, Object> payload) {
        try {
            emitter.send(SseEmitter.event().data(objectMapper.writeValueAsString(payload)));
        } catch (IOException io) {
            throw new UncheckedIOException(io); // client gone — unwind the stream
        }
    }

    private void sendError(SseEmitter emitter, int status, String message) {
        try {
            emitter.send(SseEmitter.event().data(objectMapper.writeValueAsString(
                    Map.of("type", "error", "status", status, "message", message))));
        } catch (Exception ignore) {
            // client already gone
        }
        safeComplete(emitter);
    }

    private void safeComplete(SseEmitter emitter) {
        try {
            emitter.complete();
        } catch (Exception ignore) {
            // already completed
        }
    }

    private Map<String, Object> turn(String role, String text) {
        return Map.of("role", role, "parts", List.of(Map.of("text", text == null ? "" : text)));
    }

    private String mapRole(MessageRole role) {
        return role == MessageRole.ASSISTANT ? "model" : "user";
    }

    private record ProblemContext(String title, String text) {}

    private ProblemContext loadContext(UUID problemId) {
        Problem problem = problemRepository.findById(problemId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Problem not found"));

        List<ProblemExample> examples = exampleRepository.findByProblemIdOrderByDisplayOrderAsc(problemId);

        StringBuilder sb = new StringBuilder();
        sb.append("Title: ").append(problem.getTitle()).append('\n');
        sb.append("Difficulty: ").append(problem.getDifficulty()).append('\n');
        List<String> topics = parseList(problem.getTopicsJson());
        if (!topics.isEmpty()) {
            sb.append("Topics: ").append(String.join(", ", topics)).append('\n');
        }
        sb.append("\nDescription:\n").append(problem.getDescription()).append('\n');
        List<String> constraints = parseList(problem.getConstraintsJson());
        if (!constraints.isEmpty()) {
            sb.append("\nConstraints:\n");
            constraints.forEach(c -> sb.append("- ").append(c).append('\n'));
        }
        if (!examples.isEmpty()) {
            sb.append("\nExamples:\n");
            int i = 1;
            for (ProblemExample ex : examples) {
                sb.append(i++).append(") Input: ").append(ex.getInput())
                        .append(" | Output: ").append(ex.getOutput());
                if (ex.getExplanation() != null && !ex.getExplanation().isBlank()) {
                    sb.append(" | Explanation: ").append(ex.getExplanation());
                }
                sb.append('\n');
            }
        }
        return new ProblemContext(problem.getTitle(), sb.toString());
    }

    private List<String> parseList(String json) {
        if (json == null || json.isBlank()) return Collections.emptyList();
        try {
            return objectMapper.readValue(json, new TypeReference<List<String>>() {});
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    private String truncate(String s, int max) {
        if (s == null) return null;
        s = s.strip();
        return s.length() <= max ? s : s.substring(0, max);
    }
}
