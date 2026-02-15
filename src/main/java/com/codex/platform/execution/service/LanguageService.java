package com.codex.platform.execution.service;

import com.codex.platform.execution.dto.LanguageRequest;
import com.codex.platform.execution.entity.Language;
import com.codex.platform.execution.repository.LanguageRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class LanguageService {

    private final LanguageRepository languageRepository;

    @Transactional(readOnly = true)
    public List<Language> getAllLanguages() {
        return languageRepository.findAll();
    }

    @Transactional
    public Language createLanguage(LanguageRequest request) {
        if (languageRepository.existsByNameIgnoreCase(request.getName().trim())) {
            throw new IllegalArgumentException("Language with this name already exists");
        }

        Language language = new Language();
        applyRequest(language, request);
        return languageRepository.save(language);
    }

    @Transactional
    public Language updateLanguage(UUID id, LanguageRequest request) {
        UUID languageId = Objects.requireNonNull(id, "Language ID is required");
        Language language = languageRepository.findById(languageId)
                .orElseThrow(() -> new IllegalArgumentException("Language not found"));

        if (languageRepository.existsByNameIgnoreCaseAndIdNot(request.getName().trim(), languageId)) {
            throw new IllegalArgumentException("Language with this name already exists");
        }

        applyRequest(language, request);
        return languageRepository.save(language);
    }

    @Transactional
    public void deleteLanguage(UUID id) {
        UUID languageId = Objects.requireNonNull(id, "Language ID is required");
        if (!languageRepository.existsById(languageId)) {
            throw new IllegalArgumentException("Language not found");
        }
        languageRepository.deleteById(languageId);
    }

    private void applyRequest(Language language, LanguageRequest request) {
        language.setName(request.getName().trim());
        language.setVersion(request.getVersion().trim());
        language.setDockerImage(request.getDockerImage().trim());
        language.setFileExtension(request.getFileExtension().trim());
        language.setCompileCommand(request.getCompileCommand() == null ? null : request.getCompileCommand().trim());
        language.setExecuteCommand(request.getExecuteCommand().trim());
    }
}
