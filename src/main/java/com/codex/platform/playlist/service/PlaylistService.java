package com.codex.platform.playlist.service;

import com.codex.platform.playlist.dto.PlaylistCreateRequest;
import com.codex.platform.playlist.dto.PlaylistResponse;
import com.codex.platform.playlist.dto.PlaylistUpdateRequest;
import com.codex.platform.playlist.entity.Playlist;
import com.codex.platform.playlist.entity.PlaylistItem;
import com.codex.platform.playlist.repository.PlaylistItemRepository;
import com.codex.platform.playlist.repository.PlaylistRepository;
import com.codex.platform.problem.dto.ProblemRequest;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.problem.service.ProblemService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.server.ResponseStatusException;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ThreadLocalRandom;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class PlaylistService {

    private static final String[] ACCENT_COLORS = {
            "#A8E6CF", // mint
            "#B8C5F2", // periwinkle
            "#F5A9A9", // salmon
            "#F7E36D", // yellow
            "#FFD6A5", // peach
            "#C9B1FF", // lavender
            "#A0E7E5", // aqua
            "#FFADAD", // soft red
    };

    private final PlaylistRepository playlistRepository;
    private final PlaylistItemRepository itemRepository;
    private final ProblemRepository problemRepository;
    private final ProblemService problemService;

    public List<PlaylistResponse> listMine(UUID userId) {
        List<Playlist> all = new ArrayList<>(playlistRepository.findByOwnerUserIdOrderByUpdatedAtDesc(userId));
        all.addAll(playlistRepository.findByFeaturedTrueOrderByCreatedAtAsc());
        return all.stream()
                .map(p -> toSummary(p, (int) itemRepository.countByPlaylistId(p.getId())))
                .toList();
    }

    public PlaylistResponse getMine(UUID userId, UUID playlistId) {
        Playlist playlist = playlistRepository.findByIdAndFeaturedTrue(playlistId)
                .orElseGet(() -> requireOwned(userId, playlistId));
        return toDetail(playlist);
    }

    @Transactional
    public PlaylistResponse create(UUID userId, PlaylistCreateRequest request) {
        Playlist playlist = new Playlist();
        playlist.setOwnerUserId(userId);
        playlist.setTitle(request.getTitle().trim());
        playlist.setDescription(blankToNull(request.getDescription()));
        playlist.setAccentColor(ACCENT_COLORS[ThreadLocalRandom.current().nextInt(ACCENT_COLORS.length)]);
        return toSummary(playlistRepository.save(playlist), 0);
    }

    @Transactional
    public PlaylistResponse update(UUID userId, UUID playlistId, PlaylistUpdateRequest request) {
        Playlist playlist = requireOwned(userId, playlistId);
        if (request.getTitle() != null && !request.getTitle().isBlank()) {
            playlist.setTitle(request.getTitle().trim());
        }
        if (request.getDescription() != null) {
            playlist.setDescription(blankToNull(request.getDescription()));
        }
        return toDetail(playlistRepository.save(playlist));
    }

    @Transactional
    public void delete(UUID userId, UUID playlistId) {
        Playlist playlist = requireOwned(userId, playlistId);
        itemRepository.deleteByPlaylistId(playlist.getId());
        playlistRepository.delete(playlist);
    }

    @Transactional
    public PlaylistResponse addExistingProblem(UUID userId, UUID playlistId, UUID problemId) {
        Playlist playlist = requireOwned(userId, playlistId);
        Problem problem = problemRepository.findById(problemId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Problem not found"));

        // Users may only add catalog problems, or problems they created themselves.
        if (!Boolean.TRUE.equals(problem.getInCatalog())
                && (problem.getCreatedByUserId() == null || !problem.getCreatedByUserId().equals(userId))) {
            throw new ResponseStatusException(HttpStatus.FORBIDDEN, "Cannot add this problem to your playlist");
        }

        if (itemRepository.existsByPlaylistIdAndProblemId(playlistId, problemId)) {
            throw new ResponseStatusException(HttpStatus.CONFLICT, "Problem already in playlist");
        }

        PlaylistItem item = new PlaylistItem();
        item.setPlaylistId(playlistId);
        item.setProblemId(problemId);
        item.setPosition((int) itemRepository.countByPlaylistId(playlistId));
        itemRepository.save(item);
        playlistRepository.save(playlist); // bump updatedAt
        return toDetail(playlist);
    }

    @Transactional
    public PlaylistResponse createAndAddProblem(UUID userId, UUID playlistId, ProblemRequest request) {
        requireOwned(userId, playlistId);
        Problem created = problemService.createUserProblem(userId, request);
        return addExistingProblem(userId, playlistId, created.getId());
    }

    @Transactional
    public PlaylistResponse removeProblem(UUID userId, UUID playlistId, UUID problemId) {
        Playlist playlist = requireOwned(userId, playlistId);
        if (!itemRepository.existsByPlaylistIdAndProblemId(playlistId, problemId)) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "Problem not in playlist");
        }
        itemRepository.deleteByPlaylistIdAndProblemId(playlistId, problemId);
        // Re-pack positions
        List<PlaylistItem> remaining = itemRepository.findByPlaylistIdOrderByPositionAsc(playlistId);
        for (int i = 0; i < remaining.size(); i++) {
            remaining.get(i).setPosition(i);
        }
        itemRepository.saveAll(remaining);
        playlistRepository.save(playlist);
        return toDetail(playlist);
    }

    @Transactional
    public PlaylistResponse reorderProblems(UUID userId, UUID playlistId, List<UUID> problemIds) {
        Playlist playlist = requireOwned(userId, playlistId);
        List<PlaylistItem> items = itemRepository.findByPlaylistIdOrderByPositionAsc(playlistId);
        if (problemIds == null || problemIds.size() != items.size()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                    "problemIds must include every problem in the playlist exactly once");
        }

        Map<UUID, PlaylistItem> byProblemId = items.stream()
                .collect(Collectors.toMap(PlaylistItem::getProblemId, Function.identity()));

        for (UUID problemId : problemIds) {
            if (!byProblemId.containsKey(problemId)) {
                throw new ResponseStatusException(HttpStatus.BAD_REQUEST,
                        "Unknown problem in reorder list: " + problemId);
            }
        }

        for (int i = 0; i < problemIds.size(); i++) {
            byProblemId.get(problemIds.get(i)).setPosition(i);
        }
        itemRepository.saveAll(items);
        playlistRepository.save(playlist);
        return toDetail(playlist);
    }

    public boolean userCanAccessProblem(UUID userId, UUID problemId) {
        if (userId == null) return false;
        List<UUID> playlistIds = new ArrayList<>(playlistRepository.findByOwnerUserIdOrderByUpdatedAtDesc(userId).stream()
                .map(Playlist::getId)
                .toList());
        playlistRepository.findByFeaturedTrueOrderByCreatedAtAsc().forEach(pl -> playlistIds.add(pl.getId()));
        if (playlistIds.isEmpty()) return false;
        return itemRepository.existsByProblemIdAndPlaylistIdIn(problemId, playlistIds);
    }

    private Playlist requireOwned(UUID userId, UUID playlistId) {
        return playlistRepository.findByIdAndOwnerUserId(playlistId, userId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Playlist not found"));
    }

    private PlaylistResponse toSummary(Playlist playlist, int count) {
        return PlaylistResponse.builder()
                .id(playlist.getId())
                .title(playlist.getTitle())
                .description(playlist.getDescription())
                .accentColor(playlist.getAccentColor())
                .problemCount(count)
                .featured(Boolean.TRUE.equals(playlist.getFeatured()))
                .createdAt(playlist.getCreatedAt())
                .updatedAt(playlist.getUpdatedAt())
                .problems(List.of())
                .build();
    }

    private PlaylistResponse toDetail(Playlist playlist) {
        List<PlaylistItem> items = itemRepository.findByPlaylistIdOrderByPositionAsc(playlist.getId());
        List<UUID> problemIds = items.stream().map(PlaylistItem::getProblemId).toList();
        Map<UUID, Problem> byId = problemIds.isEmpty()
                ? Map.of()
                : problemRepository.findAllById(problemIds).stream()
                .collect(Collectors.toMap(Problem::getId, Function.identity()));

        List<PlaylistResponse.PlaylistProblemSummary> problems = new ArrayList<>();
        for (PlaylistItem item : items) {
            Problem problem = byId.get(item.getProblemId());
            if (problem == null) continue;
            problems.add(PlaylistResponse.PlaylistProblemSummary.builder()
                    .id(problem.getId())
                    .title(problem.getTitle())
                    .difficulty(problem.getDifficulty())
                    .position(item.getPosition())
                    .userCreated(problem.getCreatedByUserId() != null)
                    .build());
        }

        return PlaylistResponse.builder()
                .id(playlist.getId())
                .title(playlist.getTitle())
                .description(playlist.getDescription())
                .accentColor(playlist.getAccentColor())
                .problemCount(problems.size())
                .featured(Boolean.TRUE.equals(playlist.getFeatured()))
                .createdAt(playlist.getCreatedAt())
                .updatedAt(playlist.getUpdatedAt())
                .problems(problems)
                .build();
    }

    private static String blankToNull(String s) {
        if (s == null) return null;
        String t = s.trim();
        return t.isEmpty() ? null : t;
    }
}
