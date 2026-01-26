package com.codex.platform.realtime.controller;

import com.codex.platform.realtime.service.SseService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.UUID;

@RestController
@RequestMapping("/api/submissions")
@RequiredArgsConstructor
public class SseController {

    private final SseService sseService;

    @GetMapping(value = "/{id}/events", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter streamEvents(@PathVariable UUID id) {
        return sseService.registerEmitter(id);
    }
}
