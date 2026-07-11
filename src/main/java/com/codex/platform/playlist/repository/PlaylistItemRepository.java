package com.codex.platform.playlist.repository;

import com.codex.platform.playlist.entity.PlaylistItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface PlaylistItemRepository extends JpaRepository<PlaylistItem, UUID> {
    List<PlaylistItem> findByPlaylistIdOrderByPositionAsc(UUID playlistId);

    Optional<PlaylistItem> findByPlaylistIdAndProblemId(UUID playlistId, UUID problemId);

    boolean existsByPlaylistIdAndProblemId(UUID playlistId, UUID problemId);

    long countByPlaylistId(UUID playlistId);

    void deleteByPlaylistId(UUID playlistId);

    void deleteByPlaylistIdAndProblemId(UUID playlistId, UUID problemId);

    boolean existsByProblemIdAndPlaylistIdIn(UUID problemId, List<UUID> playlistIds);
}
