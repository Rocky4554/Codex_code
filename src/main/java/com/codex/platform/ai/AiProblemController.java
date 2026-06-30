package com.codex.platform.ai;

import com.codex.platform.ai.dto.AiEditRequest;
import com.codex.platform.ai.dto.AiGenerateRequest;
import com.codex.platform.ai.dto.ProblemDraft;
import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

/**
 * Admin-only AI problem authoring.
 *
 * <p>These endpoints never persist anything. They return a {@link ProblemDraft}
 * which the admin reviews and edits in the existing form, then saves through the
 * normal {@code POST /api/problems} flow. Both require an ADMIN JWT (the
 * {@code POST /api/problems/**} matcher already forces authentication; the role
 * check below restricts it to admins, mirroring {@code ProblemController}).
 */
@RestController
@RequestMapping("/api/problems/ai")
@RequiredArgsConstructor
public class AiProblemController {

    private final AiProblemService aiProblemService;

    @PostMapping("/generate")
    public ResponseEntity<ProblemDraft> generate(@Valid @RequestBody AiGenerateRequest request) {
        requireAdmin();
        return ResponseEntity.ok(aiProblemService.generate(request.getName(), request.getNotes()));
    }

    @PostMapping("/edit")
    public ResponseEntity<ProblemDraft> edit(@Valid @RequestBody AiEditRequest request) {
        requireAdmin();
        return ResponseEntity.ok(aiProblemService.edit(request.getCurrent(), request.getInstruction()));
    }

    private void requireAdmin() {
        String role = JwtAuthenticationFilter.getCurrentUserRole();
        if (!"ADMIN".equals(role)) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Admin access required");
        }
    }
}
