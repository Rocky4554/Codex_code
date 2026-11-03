package com.codex.platform.config;

import com.codex.platform.common.enums.ProblemDifficulty;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.ProblemExample;
import com.codex.platform.problem.entity.TestCase;
import com.codex.platform.problem.repository.ProblemExampleRepository;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.problem.repository.TestCaseRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.stream.Collectors;

/**
 * Upserts catalog problems by title, writing only what changed.
 *
 * <p>Startup used to delete and re-insert every example and test case of every seeded problem,
 * one statement at a time — hundreds of round trips to a remote database on each boot. A
 * {@link Snapshot} loads problems, examples and test cases in three queries, and
 * {@link #upsert} skips problems whose stored content already matches the seed.
 */
@Component
@RequiredArgsConstructor
public class CatalogSync {

    public record ExampleSpec(String input, String output, String explanation) {}

    public record TestSpec(String input, String expectedOutput, boolean sample) {}

    /** {@code inCatalog} null leaves the stored flag alone. */
    public record ProblemSpec(
            String title,
            String description,
            ProblemDifficulty difficulty,
            int orderNum,
            String constraintsJson,
            String topicsJson,
            Boolean inCatalog,
            List<ExampleSpec> examples,
            List<TestSpec> testCases) {}

    /** Everything currently stored, loaded once per sync. */
    public static final class Snapshot {
        private final Map<String, Problem> byTitle;
        private final Map<UUID, List<ProblemExample>> examples;
        private final Map<UUID, List<TestCase>> testCases;

        private Snapshot(Map<String, Problem> byTitle, Map<UUID, List<ProblemExample>> examples, Map<UUID, List<TestCase>> testCases) {
            this.byTitle = byTitle;
            this.examples = examples;
            this.testCases = testCases;
        }
    }

    private static final int TIME_LIMIT_MS = 5000;
    private static final int MEMORY_LIMIT_MB = 256;

    private final ProblemRepository problemRepository;
    private final ProblemExampleRepository exampleRepository;
    private final TestCaseRepository testCaseRepository;

    public Snapshot snapshot() {
        Map<String, Problem> byTitle = new HashMap<>();
        // User-authored (playlist-only) problems are never matched, so a seed can't overwrite one that shares its title.
        for (Problem p : problemRepository.findAll()) {
            if (p.getCreatedByUserId() == null) byTitle.putIfAbsent(p.getTitle().toLowerCase(), p);
        }
        Map<UUID, List<ProblemExample>> examples = exampleRepository.findAll().stream()
                .collect(Collectors.groupingBy(ProblemExample::getProblemId));
        Map<UUID, List<TestCase>> testCases = testCaseRepository.findAll().stream()
                .collect(Collectors.groupingBy(TestCase::getProblemId));
        return new Snapshot(byTitle, examples, testCases);
    }

    /** Insert or update one problem. Returns true when anything was written. */
    public boolean upsert(ProblemSpec spec, Snapshot snap) {
        Problem problem = snap.byTitle.get(spec.title().toLowerCase());
        boolean isNew = problem == null;
        if (isNew) problem = new Problem();

        boolean fieldsSame = !isNew
                && Objects.equals(problem.getTitle(), spec.title())
                && Objects.equals(problem.getDescription(), spec.description())
                && problem.getDifficulty() == spec.difficulty()
                && Objects.equals(problem.getOrderNum(), spec.orderNum())
                && Objects.equals(problem.getConstraintsJson(), spec.constraintsJson())
                && Objects.equals(problem.getTopicsJson(), spec.topicsJson())
                && Objects.equals(problem.getTimeLimitMs(), TIME_LIMIT_MS)
                && Objects.equals(problem.getMemoryLimitMb(), MEMORY_LIMIT_MB)
                && (spec.inCatalog() == null || Objects.equals(problem.getInCatalog(), spec.inCatalog()));
        boolean examplesSame = !isNew && sameExamples(snap.examples.getOrDefault(problem.getId(), List.of()), spec.examples());
        boolean testsSame = !isNew && sameTests(snap.testCases.getOrDefault(problem.getId(), List.of()), spec.testCases());
        if (fieldsSame && examplesSame && testsSame) return false;

        if (!fieldsSame) {
            problem.setTitle(spec.title());
            problem.setDescription(spec.description());
            problem.setDifficulty(spec.difficulty());
            problem.setTimeLimitMs(TIME_LIMIT_MS);
            problem.setMemoryLimitMb(MEMORY_LIMIT_MB);
            problem.setOrderNum(spec.orderNum());
            problem.setConstraintsJson(spec.constraintsJson());
            problem.setTopicsJson(spec.topicsJson());
            if (spec.inCatalog() != null) problem.setInCatalog(spec.inCatalog());
            problem = problemRepository.save(problem);
            snap.byTitle.put(spec.title().toLowerCase(), problem);
        }
        UUID id = problem.getId();

        if (!examplesSame) {
            if (!isNew) exampleRepository.deleteByProblemId(id);
            List<ProblemExample> rows = new ArrayList<>();
            for (int i = 0; i < spec.examples().size(); i++) {
                ExampleSpec e = spec.examples().get(i);
                ProblemExample row = new ProblemExample();
                row.setProblemId(id);
                row.setInput(e.input());
                row.setOutput(e.output());
                row.setExplanation(e.explanation());
                row.setDisplayOrder(i);
                rows.add(row);
            }
            snap.examples.put(id, exampleRepository.saveAll(rows));
        }

        if (!testsSame) {
            if (!isNew) testCaseRepository.deleteByProblemId(id);
            List<TestCase> rows = new ArrayList<>();
            for (TestSpec t : spec.testCases()) {
                TestCase row = new TestCase();
                row.setProblemId(id);
                row.setInput(t.input());
                row.setExpectedOutput(t.expectedOutput());
                row.setIsSample(t.sample());
                rows.add(row);
            }
            snap.testCases.put(id, testCaseRepository.saveAll(rows));
        }
        return true;
    }

    private static boolean sameExamples(List<ProblemExample> stored, List<ExampleSpec> wanted) {
        if (stored.size() != wanted.size()) return false;
        List<ProblemExample> sorted = stored.stream()
                .sorted(Comparator.comparing(e -> e.getDisplayOrder() == null ? 0 : e.getDisplayOrder()))
                .toList();
        for (int i = 0; i < wanted.size(); i++) {
            ProblemExample s = sorted.get(i);
            ExampleSpec w = wanted.get(i);
            if (!Objects.equals(s.getInput(), w.input())
                    || !Objects.equals(s.getOutput(), w.output())
                    || !Objects.equals(s.getExplanation(), w.explanation())
                    || !Objects.equals(s.getDisplayOrder(), i)) return false;
        }
        return true;
    }

    /** Test cases have no order column, so compare as multisets. */
    private static boolean sameTests(List<TestCase> stored, List<TestSpec> wanted) {
        if (stored.size() != wanted.size()) return false;
        List<String> a = stored.stream()
                .map(t -> key(t.getInput(), t.getExpectedOutput(), Boolean.TRUE.equals(t.getIsSample())))
                .sorted().toList();
        List<String> b = wanted.stream()
                .map(t -> key(t.input(), t.expectedOutput(), t.sample()))
                .sorted().toList();
        return a.equals(b);
    }

    private static String key(String input, String expected, boolean sample) {
        return (sample ? "1" : "0") + '\u0000' + input + '\u0000' + expected;
    }
}
