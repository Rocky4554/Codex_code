package com.codex.platform.playlist.repository;

import com.codex.platform.playlist.entity.Playlist;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface PlaylistRepository extends JpaRepository<Playlist, UUID> {
    List<Playlist> findByOwnerUserIdOrderByUpdatedAtDesc(UUID ownerUserId);

    Optional<Playlist> findByIdAndOwnerUserId(UUID id, UUID ownerUserId);
}
