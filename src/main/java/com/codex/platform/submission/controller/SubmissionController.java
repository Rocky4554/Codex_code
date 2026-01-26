package com.codex.platform.submission.controller;

import com.codex.platform.submission.dto.SubmitCodeRequest;
import com.codex.platform.submission.dto.SubmitCodeResponse;
import com.codex.platform.submission.service.SubmissionService;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/submissions")
@RequiredArgsConstructor
public class SubmissionController {

    private final SubmissionService submissionService;

    @PostMapping
    public ResponseEntity<SubmitCodeResponse> submitCode(
            @Valid @RequestBody SubmitCodeRequest request,
            HttpServletRequest httpRequest) {
        return ResponseEntity.ok(submissionService.submitCode(request, httpRequest));
    }
}
