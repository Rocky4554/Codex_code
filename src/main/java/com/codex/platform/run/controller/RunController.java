package com.codex.platform.run.controller;

import com.codex.platform.run.dto.RunCodeRequest;
import com.codex.platform.run.dto.RunCodeResponse;
import com.codex.platform.run.service.RunService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/run")
@RequiredArgsConstructor
public class RunController {

    private final RunService runService;

    @PostMapping
    public ResponseEntity<RunCodeResponse> run(@Valid @RequestBody RunCodeRequest request) {
        return ResponseEntity.ok(runService.run(request));
    }
}
