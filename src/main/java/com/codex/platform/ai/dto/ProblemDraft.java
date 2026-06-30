package com.codex.platform.ai.dto;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

/**
 * AI-authored draft of a problem.
 *
 * <p>This mirrors the exact shape the admin {@code ProblemForm} accepts as its
 * {@code initial} value (see {@code codex-front/app/(main)/admin/page.jsx}). The
 * frontend feeds a draft straight into the form, the admin reviews/edits it, and
 * then the normal {@code POST /api/problems} flow saves it.
 *
 * <p>It carries two extra, form-ignored fields the manual form does not:
 * <ul>
 *   <li>{@link #referenceSolution} — the stdin/stdout program the AI wrote, used
 *       to <b>verify</b> the test-case outputs against the real execution engine.</li>
 *   <li>{@link #meta} — verification report shown to the admin (which cases were
 *       verified, compile errors, warnings).</li>
 * </ul>
 *
 * <p>{@code @JsonIgnoreProperties(ignoreUnknown = true)} keeps parsing forgiving:
 * if Gemini emits an unexpected extra key we drop it instead of failing.
 */
@Data
@NoArgsConstructor
@JsonIgnoreProperties(ignoreUnknown = true)
public class ProblemDraft {

    private String title;
    private String description;
    private String difficulty;
    private Integer timeLimitMs;
    private Integer memoryLimitMb;
    private Integer orderNum;
    private List<String> constraints = new ArrayList<>();
    private List<String> topics = new ArrayList<>();
    private List<Example> examples = new ArrayList<>();
    private List<TestCaseDraft> testCases = new ArrayList<>();
    private ReferenceSolution referenceSolution;
    private Meta meta;

    @Data
    @NoArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class Example {
        private String input;
        private String output;
        private String explanation;
        private Integer displayOrder;
    }

    @Data
    @NoArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class TestCaseDraft {
        private String input;
        private String expectedOutput;
        private Boolean isSample = false;
        /** True once the output was produced by running the reference solution. */
        private Boolean verified = false;
        /** Optional per-case note (e.g. why it could not be verified). */
        private String note;
    }

    @Data
    @NoArgsConstructor
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ReferenceSolution {
        /** Language name, must match a row in the {@code languages} table (e.g. "Python"). */
        private String language;
        /** Full program: reads stdin, prints only the answer to stdout. */
        private String sourceCode;
    }

    /** Verification report attached to the draft; ignored by the save form. */
    @Data
    @NoArgsConstructor
    public static class Meta {
        private boolean verified;
        private String referenceLanguage;
        private String compileError;
        private int verifiedCount;
        private int totalTestCases;
        private List<String> warnings = new ArrayList<>();
    }
}
