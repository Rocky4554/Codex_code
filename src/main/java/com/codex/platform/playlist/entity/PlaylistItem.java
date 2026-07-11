package com.codex.platform.playlist.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "playlist_items", indexes = {
        @Index(name = "idx_playlist_items_playlist", columnList = "playlistId")
}, uniqueConstraints = {
        @UniqueConstraint(name = "uk_playlist_problem", columnNames = {"playlistId", "problemId"})
})
@Data
@NoArgsConstructor
public class PlaylistItem {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private UUID playlistId;

    @Column(nullable = false)
    private UUID problemId;

    @Column(nullable = false)
    private Integer position = 0;

    @Column(nullable = false, updatable = false)
    private Instant addedAt;

    @PrePersist
    void onCreate() {
        this.addedAt = Instant.now();
        if (this.position == null) {
            this.position = 0;
        }
    }
}
