package com.codex.platform.playlist.entity;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;
import java.util.UUID;

@Entity
@Table(name = "playlists", indexes = {
        @Index(name = "idx_playlists_owner", columnList = "ownerUserId")
})
@Data
@NoArgsConstructor
public class Playlist {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private UUID ownerUserId;

    @Column(nullable = false, length = 120)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    /** Hex accent used by the neo-brutalist card UI, e.g. #A8E6CF */
    @Column(nullable = false, length = 16)
    private String accentColor;

    /** System playlists (curated topic / interview lists) are visible to everyone and read-only. */
    @Column(nullable = false, columnDefinition = "boolean not null default false")
    private Boolean featured = false;

    @Column(nullable = false, updatable = false)
    private Instant createdAt;

    @Column(nullable = false)
    private Instant updatedAt;

    @PrePersist
    void onCreate() {
        if (featured == null) {
            featured = false;
        }
        Instant now = Instant.now();
        this.createdAt = now;
        this.updatedAt = now;
    }

    @PreUpdate
    void onUpdate() {
        this.updatedAt = Instant.now();
    }
}
