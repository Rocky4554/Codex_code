package com.codex.platform.playlist.controller;

import com.codex.platform.auth.filter.JwtAuthenticationFilter;
import com.codex.platform.playlist.dto.AddProblemToPlaylistRequest;
import com.codex.platform.playlist.dto.PlaylistCreateRequest;
import com.codex.platform.playlist.dto.PlaylistResponse;
import com.codex.platform.playlist.dto.PlaylistUpdateRequest;
import com.codex.platform.playlist.dto.ReorderPlaylistProblemsRequest;
import com.codex.platform.playlist.service.PlaylistService;
import com.codex.platform.problem.dto.ProblemRequest;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/playlists")
@RequiredArgsConstructor
public class PlaylistController {

    private final PlaylistService playlistService;

    @GetMapping
    public List<PlaylistResponse> listMine() {
        return playlistService.listMine(JwtAuthenticationFilter.getCurrentUserId());
    }

    @PostMapping
    public ResponseEntity<PlaylistResponse> create(@Valid @RequestBody PlaylistCreateRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED)
                .body(playlistService.create(JwtAuthenticationFilter.getCurrentUserId(), request));
    }

    @GetMapping("/{id}")
    public PlaylistResponse get(@PathVariable UUID id) {
        return playlistService.getMine(JwtAuthenticationFilter.getCurrentUserId(), id);
    }

    @PutMapping("/{id}")
    public PlaylistResponse update(@PathVariable UUID id, @Valid @RequestBody PlaylistUpdateRequest request) {
        return playlistService.update(JwtAuthenticationFilter.getCurrentUserId(), id, request);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        playlistService.delete(JwtAuthenticationFilter.getCurrentUserId(), id);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/{id}/problems")
    public PlaylistResponse addProblem(
            @PathVariable UUID id,
            @Valid @RequestBody AddProblemToPlaylistRequest request) {
        return playlistService.addExistingProblem(
                JwtAuthenticationFilter.getCurrentUserId(), id, request.getProblemId());
    }

    @PostMapping("/{id}/problems/create")
    public ResponseEntity<PlaylistResponse> createAndAddProblem(
            @PathVariable UUID id,
            @Valid @RequestBody ProblemRequest request) {
        return ResponseEntity.status(HttpStatus.CREATED).body(
                playlistService.createAndAddProblem(
                        JwtAuthenticationFilter.getCurrentUserId(), id, request));
    }

    @DeleteMapping("/{id}/problems/{problemId}")
    public PlaylistResponse removeProblem(@PathVariable UUID id, @PathVariable UUID problemId) {
        return playlistService.removeProblem(
                JwtAuthenticationFilter.getCurrentUserId(), id, problemId);
    }

    @PutMapping("/{id}/problems/reorder")
    public PlaylistResponse reorderProblems(
            @PathVariable UUID id,
            @Valid @RequestBody ReorderPlaylistProblemsRequest request) {
        return playlistService.reorderProblems(
                JwtAuthenticationFilter.getCurrentUserId(), id, request.getProblemIds());
    }
}
