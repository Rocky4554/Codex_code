package com.codex.platform.execution.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.UUID;

@Entity
@Table(name = "languages")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Language {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true)
    private String name;

    @Column(nullable = false)
    private String version;

    @Column(nullable = false)
    private String dockerImage;

    @Column
    private String fileExtension;

    @Column
    private String compileCommand;

    @Column
    private String executeCommand;
}
