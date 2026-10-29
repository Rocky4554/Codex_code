package com.codex.platform.config;

import com.codex.platform.common.enums.ProblemDifficulty;
import com.codex.platform.playlist.entity.Playlist;
import com.codex.platform.playlist.entity.PlaylistItem;
import com.codex.platform.playlist.repository.PlaylistItemRepository;
import com.codex.platform.playlist.repository.PlaylistRepository;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.ProblemExample;
import com.codex.platform.problem.entity.TestCase;
import com.codex.platform.problem.repository.ProblemExampleRepository;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.problem.repository.TestCaseRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Seeds interview problems (coding + SQL) from {@code resources/catalog/*.json}, tags legacy
 * problems that have no topics, and (re)builds the featured system playlists.
 *
 * <p>Runs after {@link CuratedProblemCatalogInitializer} (order 10) so its problems already
 * exist when playlists are assembled. Everything is idempotent: problems are upserted by title
 * and playlists by (featured, title).
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class InterviewCatalogInitializer {

    /** Owner of featured playlists: no real user has this id. */
    static final UUID SYSTEM_OWNER = new UUID(0L, 0L);

    private static final int CODING_ORDER_BASE = 100;
    private static final int SQL_ORDER_BASE = 200;

    /** Topics for problems seeded before topics existed. Applied only when topics are empty. */
    private static final Map<String, List<String>> LEGACY_TOPICS = Map.of(
            "Hello World", List.of("Basics"),
            "Palindrome Number", List.of("Math"),
            "Fibonacci Number", List.of("Recursion", "DP", "Math"),
            "Two Sum", List.of("Array", "Hash Map"),
            "Reverse String", List.of("String", "Two Pointers"),
            "Factorial", List.of("Math", "Recursion"),
            "Longest Common Prefix", List.of("String"),
            "Merge Two Sorted Arrays", List.of("Array", "Two Pointers"),
            "Valid Parentheses", List.of("Stack", "String"),
            "Binary Search", List.of("Binary Search", "Array"));

    private final ProblemRepository problemRepository;
    private final ProblemExampleRepository exampleRepository;
    private final TestCaseRepository testCaseRepository;
    private final PlaylistRepository playlistRepository;
    private final PlaylistItemRepository itemRepository;
    private final ObjectMapper objectMapper;

    @EventListener(ApplicationReadyEvent.class)
    @Order(20)
    @Transactional
    public void onApplicationReady() {
        try {
            backfillLegacyTopics();
            int coding = upsertProblems("catalog/coding-interview-problems.json", CODING_ORDER_BASE);
            int sql = upsertProblems("catalog/sql-interview-problems.json", SQL_ORDER_BASE);
            tagSqlSampleProblem();
            int playlists = syncPlaylists("catalog/playlists.json");
            log.info("Interview catalog synced: {} coding, {} SQL problem(s), {} featured playlist(s)",
                    coding, sql, playlists);
        } catch (Exception e) {
            log.error("Interview catalog sync failed", e);
        }
    }

    private void backfillLegacyTopics() throws Exception {
        for (Map.Entry<String, List<String>> e : LEGACY_TOPICS.entrySet()) {
            var found = problemRepository.findByTitleIgnoreCase(e.getKey());
            if (found.isPresent() && isBlank(found.get().getTopicsJson())) {
                found.get().setTopicsJson(objectMapper.writeValueAsString(e.getValue()));
                problemRepository.save(found.get());
            }
        }
    }

    /** The original SQL sample problem predates topics; give it the fixed SQL tag. */
    private void tagSqlSampleProblem() throws Exception {
        var found = problemRepository.findByTitleIgnoreCase("SQL: Engineering Employees");
        if (found.isPresent() && isBlank(found.get().getTopicsJson())) {
            found.get().setTopicsJson(objectMapper.writeValueAsString(List.of("SQL", "Filtering")));
            problemRepository.save(found.get());
        }
    }

    private int upsertProblems(String resource, int orderBase) throws Exception {
        JsonNode root = read(resource);
        int index = 0;
        for (JsonNode n : root) {
            Problem problem = problemRepository.findByTitleIgnoreCase(n.get("title").asText()).orElseGet(Problem::new);
            problem.setTitle(n.get("title").asText());
            problem.setDescription(n.get("description").asText());
            problem.setDifficulty(ProblemDifficulty.valueOf(n.get("difficulty").asText()));
            problem.setTimeLimitMs(5000);
            problem.setMemoryLimitMb(256);
            problem.setOrderNum(orderBase + index++);
            problem.setConstraintsJson(n.get("constraints").isEmpty() ? null : n.get("constraints").toString());
            problem.setTopicsJson(n.get("topics").isEmpty() ? null : n.get("topics").toString());
            problem.setInCatalog(true);
            Problem saved = problemRepository.save(problem);

            exampleRepository.deleteByProblemId(saved.getId());
            List<ProblemExample> examples = new ArrayList<>();
            int order = 0;
            for (JsonNode e : n.get("examples")) {
                ProblemExample row = new ProblemExample();
                row.setProblemId(saved.getId());
                row.setInput(e.get("input").asText());
                row.setOutput(e.get("output").asText());
                row.setExplanation(e.path("explanation").asText(null));
                row.setDisplayOrder(order++);
                examples.add(row);
            }
            exampleRepository.saveAll(examples);

            testCaseRepository.deleteByProblemId(saved.getId());
            List<TestCase> cases = new ArrayList<>();
            for (JsonNode t : n.get("testCases")) {
                TestCase row = new TestCase();
                row.setProblemId(saved.getId());
                row.setInput(t.get("input").asText());
                row.setExpectedOutput(t.get("expectedOutput").asText());
                row.setIsSample(t.get("sample").asBoolean());
                cases.add(row);
            }
            testCaseRepository.saveAll(cases);
        }
        return index;
    }

    private int syncPlaylists(String resource) throws Exception {
        JsonNode defs = read(resource);
        List<Problem> catalog = problemRepository.findAll().stream()
                .filter(p -> !Boolean.FALSE.equals(p.getInCatalog()))
                .toList();
        Map<String, Problem> byTitle = new LinkedHashMap<>();
        Map<UUID, Set<String>> topicsById = new LinkedHashMap<>();
        for (Problem p : catalog) {
            byTitle.put(p.getTitle().toLowerCase(), p);
            Set<String> topics = new LinkedHashSet<>();
            if (!isBlank(p.getTopicsJson())) {
                objectMapper.readTree(p.getTopicsJson()).forEach(t -> topics.add(t.asText()));
            }
            topicsById.put(p.getId(), topics);
        }

        int count = 0;
        for (JsonNode def : defs) {
            Set<UUID> ids = new LinkedHashSet<>();
            for (JsonNode t : def.path("titles")) {
                Problem p = byTitle.get(t.asText().toLowerCase());
                if (p != null) ids.add(p.getId());
            }
            Set<String> wanted = new LinkedHashSet<>();
            def.path("topics").forEach(t -> wanted.add(t.asText()));
            catalog.stream()
                    .filter(p -> topicsById.get(p.getId()).stream().anyMatch(wanted::contains))
                    .sorted(Comparator.comparing((Problem p) -> p.getDifficulty().ordinal())
                            .thenComparing(p -> p.getOrderNum() == null ? Integer.MAX_VALUE : p.getOrderNum())
                            .thenComparing(Problem::getTitle))
                    .forEach(p -> ids.add(p.getId()));
            if (ids.isEmpty()) continue;

            Playlist playlist = playlistRepository
                    .findFirstByFeaturedTrueAndTitleIgnoreCase(def.get("title").asText())
                    .orElseGet(Playlist::new);
            playlist.setOwnerUserId(SYSTEM_OWNER);
            playlist.setFeatured(true);
            playlist.setTitle(def.get("title").asText());
            playlist.setDescription(def.path("description").asText(null));
            playlist.setAccentColor(def.path("accentColor").asText("#A8E6CF"));
            Playlist saved = playlistRepository.save(playlist);

            List<UUID> desired = List.copyOf(ids);
            List<UUID> current = itemRepository.findByPlaylistIdOrderByPositionAsc(saved.getId()).stream()
                    .map(PlaylistItem::getProblemId).toList();
            if (!desired.equals(current)) {
                itemRepository.deleteByPlaylistId(saved.getId());
                itemRepository.flush(); // deletes must hit the DB before re-inserting (unique playlist/problem)
                List<PlaylistItem> items = new ArrayList<>();
                for (int i = 0; i < desired.size(); i++) {
                    PlaylistItem item = new PlaylistItem();
                    item.setPlaylistId(saved.getId());
                    item.setProblemId(desired.get(i));
                    item.setPosition(i);
                    items.add(item);
                }
                itemRepository.saveAll(items);
            }
            count++;
        }
        return count;
    }

    private JsonNode read(String resource) throws Exception {
        try (InputStream in = new ClassPathResource(resource).getInputStream()) {
            return objectMapper.readTree(in);
        }
    }

    private static boolean isBlank(String s) {
        return s == null || s.isBlank() || "[]".equals(s.trim());
    }
}
