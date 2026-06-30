package com.codex.platform.ai;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.server.ResponseStatusException;

import java.time.Duration;
import java.util.List;
import java.util.Map;

/**
 * Thin HTTP client for Google's Gemini {@code generateContent} REST API.
 *
 * <p>Two modes:
 * <ul>
 *   <li>{@code useSearch=true} — attaches the built-in {@code google_search}
 *       grounding tool so Gemini can look the problem up on the web. Gemini does
 *       not allow combining grounding with a forced JSON response schema, so we
 *       ask for JSON in the prompt and extract it from the text ourselves
 *       (see {@link #extractJson}).</li>
 *   <li>{@code useSearch=false} — plain generation (used for edits, which need
 *       no web lookup).</li>
 * </ul>
 *
 * <p>Deliberately dependency-free: uses Spring's {@link RestClient} (already on
 * the classpath via {@code spring-boot-starter-web}) and Jackson, so no new
 * Maven dependency is required.
 */
@Component
@Slf4j
public class GeminiClient {

    private final String apiKey;
    private final String model;
    private final String baseUrl;
    private final int timeoutMs;
    private final ObjectMapper objectMapper;

    private RestClient restClient;

    public GeminiClient(
            @Value("${gemini.api-key:}") String apiKey,
            @Value("${gemini.model:gemini-3.1-flash-lite}") String model,
            @Value("${gemini.base-url:https://generativelanguage.googleapis.com/v1beta}") String baseUrl,
            @Value("${gemini.timeout-ms:120000}") int timeoutMs,
            ObjectMapper objectMapper) {
        this.apiKey = apiKey;
        this.model = model;
        this.baseUrl = baseUrl;
        this.timeoutMs = timeoutMs;
        this.objectMapper = objectMapper;
    }

    @PostConstruct
    void init() {
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout((int) Duration.ofSeconds(10).toMillis());
        factory.setReadTimeout(timeoutMs);

        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(factory)
                .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
                .build();

        if (apiKey == null || apiKey.isBlank()) {
            log.warn("GeminiClient: gemini.api-key not set; AI problem authoring will return 503 until configured");
        } else {
            log.info("GeminiClient initialized: model={}, baseUrl={}", model, baseUrl);
        }
    }

    public boolean isConfigured() {
        return apiKey != null && !apiKey.isBlank();
    }

    /**
     * Run one generation and return the concatenated text of the model reply.
     *
     * @param systemInstruction persona / rules for the model
     * @param userPrompt        the task
     * @param useSearch         attach the google_search grounding tool
     */
    public String generate(String systemInstruction, String userPrompt, boolean useSearch) {
        if (!isConfigured()) {
            throw new ResponseStatusException(HttpStatus.SERVICE_UNAVAILABLE,
                    "Gemini is not configured (set GEMINI_API_KEY)");
        }

        Map<String, Object> body = new java.util.LinkedHashMap<>();
        body.put("system_instruction", Map.of("parts", List.of(Map.of("text", systemInstruction))));
        body.put("contents", List.of(Map.of(
                "role", "user",
                "parts", List.of(Map.of("text", userPrompt)))));
        if (useSearch) {
            body.put("tools", List.of(Map.of("google_search", Map.of())));
        }
        body.put("generationConfig", Map.of("temperature", 0.2, "maxOutputTokens", 8192));

        JsonNode response;
        try {
            response = restClient.post()
                    .uri("/models/{model}:generateContent?key={key}", model, apiKey)
                    .body(body)
                    .retrieve()
                    .body(JsonNode.class);
        } catch (ResponseStatusException e) {
            throw e;
        } catch (Exception e) {
            log.error("Gemini call failed: {}", e.getMessage());
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY,
                    "Gemini request failed: " + e.getMessage(), e);
        }

        return extractText(response);
    }

    /** Pull and concatenate every text part from {@code candidates[0].content.parts[]}. */
    private String extractText(JsonNode response) {
        if (response == null) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Empty Gemini response");
        }
        JsonNode candidates = response.path("candidates");
        if (!candidates.isArray() || candidates.isEmpty()) {
            // Surface safety blocks / errors clearly instead of a generic NPE.
            String reason = response.path("promptFeedback").path("blockReason").asText("");
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY,
                    "Gemini returned no candidates" + (reason.isBlank() ? "" : " (blocked: " + reason + ")"));
        }
        StringBuilder sb = new StringBuilder();
        for (JsonNode part : candidates.get(0).path("content").path("parts")) {
            String text = part.path("text").asText("");
            if (!text.isBlank()) {
                sb.append(text);
            }
        }
        String text = sb.toString().trim();
        if (text.isEmpty()) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "Gemini returned an empty answer");
        }
        return text;
    }

    /**
     * Parse a JSON object out of free-form model text. Handles ```json fences and
     * leading/trailing prose by slicing from the first '{' to the matching last '}'.
     */
    public <T> T extractJson(String modelText, Class<T> type) {
        String json = sliceJsonObject(modelText);
        try {
            return objectMapper.readValue(json, type);
        } catch (Exception e) {
            log.warn("Failed to parse Gemini JSON ({}). First 400 chars: {}", e.getMessage(),
                    json.length() > 400 ? json.substring(0, 400) : json);
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY,
                    "Gemini returned malformed JSON: " + e.getMessage(), e);
        }
    }

    private String sliceJsonObject(String text) {
        String t = text.trim();
        // Strip ```json ... ``` or ``` ... ``` fences if present.
        if (t.startsWith("```")) {
            int firstNewline = t.indexOf('\n');
            if (firstNewline >= 0) {
                t = t.substring(firstNewline + 1);
            }
            int lastFence = t.lastIndexOf("```");
            if (lastFence >= 0) {
                t = t.substring(0, lastFence);
            }
            t = t.trim();
        }
        int start = t.indexOf('{');
        int end = t.lastIndexOf('}');
        if (start < 0 || end < 0 || end <= start) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY,
                    "Gemini response did not contain a JSON object");
        }
        return t.substring(start, end + 1);
    }
}
