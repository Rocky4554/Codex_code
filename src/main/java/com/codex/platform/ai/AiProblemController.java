package com.codex.platform.ai;

import com.codex.platform.ai.dto.AiEditRequest;
import com.codex.platform.ai.dto.AiGenerateRequest;
import com.codex.platform.ai.dto.AiVerifyRequest;
import com.codex.platform.ai.dto.ProblemDraft;
import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

/**
 * AI problem authoring for authenticated users (admins and regular users).
 *
 * <p>These endpoints never persist anything. They return a {@link ProblemDraft}
 * which the caller reviews and then saves — admins via {@code POST /api/problems},
 * users via {@code POST /api/playlists/{id}/problems/create}.
 */
@RestController
@RequestMapping("/api/problems/ai")
@RequiredArgsConstructor
public class AiProblemController {

    private final AiProblemService aiProblemService;

    @PostMapping("/generate")
    public ResponseEntity<ProblemDraft> generate(@Valid @RequestBody AiGenerateRequest request) {
        requireAuthenticated();
        return ResponseEntity.ok(aiProblemService.generate(request.getName(), request.getNotes()));
    }

    @PostMapping("/edit")
    public ResponseEntity<ProblemDraft> edit(@Valid @RequestBody AiEditRequest request) {
        requireAuthenticated();
        return ResponseEntity.ok(aiProblemService.edit(request.getCurrent(), request.getInstruction()));
    }

    /**
     * Verify a hand-authored reference solution (no Gemini call) — lets the "Add
     * manually" form run a SQL reference query on real SQLite and fill in expected
     * output, with the same automatic {@code ORDER BY} fix-up as AI-generated problems.
     */
    @PostMapping("/verify")
    public ResponseEntity<ProblemDraft> verify(@Valid @RequestBody AiVerifyRequest request) {
        requireAuthenticated();
        return ResponseEntity.ok(aiProblemService.verifyManual(
                request.getReferenceSolution(), request.getTestCases(),
                request.getTimeLimitMs(), request.getMemoryLimitMb()));
    }

    private void requireAuthenticated() {
        try {
            JwtAuthenticationFilter.getCurrentUserId();
        } catch (IllegalStateException e) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Login required");
        }
    }
}
