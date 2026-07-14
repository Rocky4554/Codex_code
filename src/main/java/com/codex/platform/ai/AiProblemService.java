package com.codex.platform.ai;

import com.codex.platform.ai.dto.ProblemDraft;
import com.codex.platform.common.util.SqlQueryNormalizer;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Orchestrates AI problem authoring:
 * <ol>
 *   <li>Ask Gemini (with web search) to write a full problem as JSON in the exact
 *       shape the admin form accepts, plus a stdin/stdout reference solution.</li>
 *   <li>Run that reference solution through the real execution engine to replace
 *       the AI-guessed test outputs with ground truth ({@link SolutionVerifier}).</li>
 *   <li>Return a {@link ProblemDraft} the admin reviews, edits, and saves via the
 *       normal {@code POST /api/problems} path.</li>
 * </ol>
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AiProblemService {

    private final GeminiClient geminiClient;
    private final SolutionVerifier solutionVerifier;
    private final ObjectMapper objectMapper;

    private static final int DEFAULT_TIME_LIMIT_MS = 5000;
    private static final int DEFAULT_MEMORY_LIMIT_MB = 256;

    private static final String SYSTEM_INSTRUCTION = """
            You are an expert competitive-programming problem author for an online judge
            similar to LeetCode. The judge runs each submission as a program that reads
            from standard input (stdin) and writes its answer to standard output (stdout),
            then compares stdout against the stored expected output after trimming
            trailing whitespace.

            You MUST return a single valid JSON object and nothing else — no markdown,
            no commentary. The JSON object must use EXACTLY this schema:

            {
              "title": string,
              "description": string,   // full statement; MUST include an "Input:" and
                                       // "Output:" section describing the exact stdin
                                       // format and stdout format
              "difficulty": "EASY" | "MEDIUM" | "HARD",
              "timeLimitMs": integer,  // 100..120000, typically 2000-5000
              "memoryLimitMb": integer,// 16..2048, typically 256
              "constraints": [string], // e.g. "1 <= n <= 10^4"
              "topics": [string],      // e.g. "Array", "Hash Table"
              "examples": [            // human-readable, shown to users (1-3 items)
                { "input": string, "output": string, "explanation": string }
              ],
              "testCases": [           // machine-graded; exactly 5 items (a mix of
                                       // normal and edge cases) UNLESS the user's
                                       // guidance asks for a different number
                { "input": string, "expectedOutput": string, "isSample": boolean }
              ],
              "referenceSolution": {
                "language": "Python" | "Java" | "C++" | "JavaScript" | "SQL",
                "sourceCode": string   // a COMPLETE, RUNNABLE program (see rules)
              }
            }

            There are TWO kinds of problem you can author. Pick SQL MODE only when the
            requested problem is a database/SQL query problem (the user asks for SQL, a
            query, joins, aggregation over tables, etc.). Otherwise use PROGRAM MODE.

            ── PROGRAM MODE (default) ──
            Critical rules:
            - The reference solution MUST be a complete, standalone program that reads ALL
              of its input from standard input (e.g. Python input()/sys.stdin, Java Scanner,
              C++ std::cin, Node readline) and writes ONLY the answer to standard output with
              print/cout/console.log. It is executed as-is against each testCases[].input.
            - DO NOT write a class/method template. NO "class Solution", no bare function
              like "def twoSum(nums, target)". If it does not read stdin and print stdout,
              it is WRONG. The judge does not call any function — it runs the program.
            - testCases[].input is the EXACT bytes fed to stdin. testCases[].expectedOutput
              is the EXACT stdout the reference program prints for that input. The description's
              "Input:" / "Output:" sections must describe precisely the stdin the program reads
              and the stdout it writes (ordering and separators included).
            - examples[] may use friendly notation (e.g. "nums = [2,7], target = 9"); they are
              for display only and are NOT executed — they need not match the stdin format.
            - Prefer Python for the reference solution unless the problem needs otherwise.
            - Produce exactly 5 testCases by default (unless the user's guidance requests a
              different number), of which at least 2 are sample cases (isSample = true).

            Example of a VALID Python reference solution (for "read n then n ints, print their sum"):
            data = sys.stdin.read().split()
            n = int(data[0])
            print(sum(int(x) for x in data[1:1+n]))
            (with "import sys" at the top). Note: it reads stdin and prints — no class, no function.

            ── SQL MODE (only for database/query problems) ──
            The judge runs SQL problems on SQLite. For each test case it creates an EMPTY
            database, executes testCases[].input against it to build and populate the tables,
            then runs the user's query and compares its printed rows to expectedOutput.

            In SQL MODE the fields mean something different — follow this EXACTLY:
            - "referenceSolution": { "language": "SQL", "sourceCode": "<a single SELECT query>" }
              The sourceCode is ONLY the query. It must NOT contain CREATE TABLE or INSERT.
            - "testCases[].input": the COMPLETE schema + seed data for that case — the
              CREATE TABLE statement(s) followed by the INSERT statement(s), each ending with
              a semicolon. Every test case is run against a FRESH, EMPTY database, so each one
              MUST repeat its own full CREATE TABLE + INSERTs. Never assume a previous case
              created the tables.
            - "testCases[].expectedOutput": exactly what SQLite prints for the reference query
              on that case's data — ONE ROW PER LINE, columns joined by a "|" character, and
              NO header line. A single-column result is therefore just one value per line.
              An empty result set means an empty expectedOutput string.

            Critical SQL rules:
            - Every test case's "input" MUST include at least one INSERT statement per table,
              with enough rows to meaningfully exercise the query (rows that both match and
              don't match its filter, where applicable). Do NOT produce a schema-only test case
              with no INSERTs unless the problem is specifically about an empty-table edge case
              — and if so, say that explicitly in the test case (there is no dedicated field for
              this, so make it obvious from context that it is intentional).
            - The reference query MUST end with an ORDER BY that fully determines the row
              order. Rows are compared as text line-by-line, so a query whose order is
              unspecified would be graded incorrectly. State the required ordering in the
              description too (e.g. "ordered by name ascending").
            - Use SQLite dialect ONLY. Do NOT use MySQL-only constructs such as DATE_FORMAT,
              IF(), IFNULL-as-IF, or backtick-quoted identifiers. Use SQLite equivalents:
              strftime(...) for dates, CASE WHEN ... THEN ... ELSE ... END instead of IF().
            - The description is rendered as Markdown (GitHub-flavored, tables supported), so
              show the table schema as an ACTUAL Markdown table, not a prose sentence — a
              header row, a "|---|---|" separator row, and 2-3 sample data rows with realistic
              example values, one such table per table in the schema. Do not describe the
              columns in a sentence instead of or in addition to the table. MUST also state the
              required ordering as its own sentence after the table(s).
            - examples[] stay human-readable (a small table and the expected rows); they are
              for display only and are not executed.

            Example of a VALID SQL problem's pieces:
              description (excerpt):
                You are given a table `employees`:

                | id | name | department |
                |----|------|------------|
                | 1 | Alice | Engineering |
                | 2 | Bob | Sales |

                Return the name of every employee in the Engineering department, ordered by
                name ascending.
              testCases[0].input:
                CREATE TABLE employees (id INTEGER, name TEXT, department TEXT);
                INSERT INTO employees VALUES (1,'Alice','Engineering');
                INSERT INTO employees VALUES (2,'Bob','Sales');
                INSERT INTO employees VALUES (3,'Charlie','Engineering');
              referenceSolution.sourceCode:
                SELECT name FROM employees WHERE department = 'Engineering' ORDER BY name;
              testCases[0].expectedOutput:
                Alice
                Charlie
            """;

    public ProblemDraft generate(String name, String notes) {
        String userPrompt = """
                Create a complete problem for the topic/name below. Search the web to get
                the canonical statement, constraints, and correct examples, then adapt it to
                the stdin/stdout judge format described in your instructions.

                PROBLEM NAME: %s
                EXTRA GUIDANCE: %s

                Return ONLY the JSON object.
                """.formatted(name, notes == null || notes.isBlank() ? "(none)" : notes);

        boolean usedSearch = true;
        String text;
        try {
            text = geminiClient.generate(SYSTEM_INSTRUCTION, userPrompt, true);
        } catch (ResponseStatusException e) {
            // Web-search grounding has its own, much stricter quota than plain
            // generation on free-tier keys. Don't fail the whole request when only
            // grounding is exhausted — fall back to the model's own knowledge.
            if (e.getStatusCode() == HttpStatus.TOO_MANY_REQUESTS) {
                log.warn("Gemini search-grounded generation hit quota; retrying without web search: {}",
                        e.getReason());
                usedSearch = false;
                text = geminiClient.generate(SYSTEM_INSTRUCTION, userPrompt, false);
            } else {
                throw e;
            }
        }

        ProblemDraft draft = geminiClient.extractJson(text, ProblemDraft.class);
        normalize(draft);
        verify(draft);
        if (!usedSearch) {
            draft.getMeta().getWarnings().add("Web search quota was exceeded, so this problem was generated from "
                    + "the model's own knowledge instead of a live search — double-check facts and constraints.");
        }
        return draft;
    }

    public ProblemDraft edit(ProblemDraft current, String instruction) {
        String currentJson;
        try {
            // Don't feed the previous verification report back to the model.
            ProblemDraft copy = cloneWithoutMeta(current);
            currentJson = objectMapper.writeValueAsString(copy);
        } catch (Exception e) {
            throw new IllegalArgumentException("Could not serialize current draft: " + e.getMessage(), e);
        }

        String userPrompt = """
                Here is the CURRENT problem as JSON:

                %s

                Apply this change requested by the admin:
                "%s"

                Return the FULL updated problem as a single JSON object using the same schema.
                Keep everything not affected by the change. If you change any testCases inputs
                or the referenceSolution, make sure expectedOutput still matches what the
                reference solution would print. Return ONLY the JSON object.
                """.formatted(currentJson, instruction);

        // No web search for edits — the model already has the full problem.
        String text = geminiClient.generate(SYSTEM_INSTRUCTION, userPrompt, false);
        ProblemDraft draft = geminiClient.extractJson(text, ProblemDraft.class);
        normalize(draft);
        verify(draft);
        return draft;
    }

    /**
     * Verify a hand-authored (non-AI) reference solution against hand-authored test
     * cases, without going through Gemini. Used by the admin/playlist "Add manually"
     * form to run a SQL reference query on real SQLite and fill in the expected
     * output — same {@link #verify} path AI drafts go through, so a missing
     * {@code ORDER BY} on a SQL query is auto-appended here too.
     */
    public ProblemDraft verifyManual(ProblemDraft.ReferenceSolution referenceSolution,
                                     List<ProblemDraft.TestCaseDraft> testCases,
                                     Integer timeLimitMs, Integer memoryLimitMb) {
        ProblemDraft draft = new ProblemDraft();
        draft.setReferenceSolution(referenceSolution);
        draft.setTestCases(testCases != null ? new ArrayList<>(testCases) : new ArrayList<>());
        draft.setTimeLimitMs(timeLimitMs);
        draft.setMemoryLimitMb(memoryLimitMb);
        normalize(draft);
        verify(draft);
        return draft;
    }

    // ── Normalization & clamping ───────────────────────────────────────────────

    private void normalize(ProblemDraft d) {
        if (d.getTitle() != null) d.setTitle(d.getTitle().trim());
        if (d.getConstraints() == null) d.setConstraints(new ArrayList<>());
        if (d.getTopics() == null) d.setTopics(new ArrayList<>());
        if (d.getExamples() == null) d.setExamples(new ArrayList<>());
        if (d.getTestCases() == null) d.setTestCases(new ArrayList<>());

        d.setDifficulty(normalizeDifficulty(d.getDifficulty()));
        d.setTimeLimitMs(clamp(d.getTimeLimitMs(), 100, 120_000, DEFAULT_TIME_LIMIT_MS));
        d.setMemoryLimitMb(clamp(d.getMemoryLimitMb(), 16, 2048, DEFAULT_MEMORY_LIMIT_MB));

        int order = 0;
        for (ProblemDraft.Example ex : d.getExamples()) {
            if (ex.getDisplayOrder() == null) ex.setDisplayOrder(order);
            order++;
        }
        for (ProblemDraft.TestCaseDraft tc : d.getTestCases()) {
            if (tc.getIsSample() == null) tc.setIsSample(false);
            if (tc.getVerified() == null) tc.setVerified(false);
        }
    }

    private String normalizeDifficulty(String value) {
        if (value == null) return "MEDIUM";
        String v = value.trim().toUpperCase();
        return switch (v) {
            case "EASY", "MEDIUM", "HARD" -> v;
            default -> "MEDIUM";
        };
    }

    private Integer clamp(Integer value, int min, int max, int fallback) {
        if (value == null) return fallback;
        if (value < min) return min;
        if (value > max) return max;
        return value;
    }

    // ── Verification ───────────────────────────────────────────────────────────

    private void verify(ProblemDraft draft) {
        ProblemDraft.Meta meta = new ProblemDraft.Meta();
        meta.setTotalTestCases(draft.getTestCases().size());
        draft.setMeta(meta);

        ProblemDraft.ReferenceSolution ref = draft.getReferenceSolution();
        String refLang = ref != null ? ref.getLanguage() : null;
        meta.setReferenceLanguage(refLang);

        if (ref == null || ref.getSourceCode() == null || ref.getSourceCode().isBlank()
                || draft.getTestCases().isEmpty()) {
            meta.getWarnings().add("No reference solution to verify against; test outputs are AI-generated.");
            return;
        }

        if (isSqlLanguage(refLang)) {
            SqlQueryNormalizer.Result normalized = SqlQueryNormalizer.ensureOrderBy(ref.getSourceCode());
            if (normalized.appended()) {
                ref.setSourceCode(normalized.sql());
                meta.getWarnings().add("Reference query had no ORDER BY — appended \"ORDER BY 1\" automatically "
                        + "so row order is deterministic and test cases pass consistently on SQLite.");
            }
        }

        List<String> inputs = draft.getTestCases().stream()
                .map(tc -> tc.getInput() == null ? "" : tc.getInput())
                .toList();

        SolutionVerifier.VerificationResult vr = solutionVerifier.verify(
                refLang, ref.getSourceCode(), inputs,
                draft.getTimeLimitMs(), draft.getMemoryLimitMb());

        if (vr.getCompileError() != null) {
            meta.setCompileError(vr.getCompileError());
            meta.getWarnings().add("Reference solution failed to compile — test outputs are AI-generated and unverified. "
                    + "Fix the solution (via AI edit) and re-generate to verify.");
            return;
        }

        if (!vr.isExecuted()) {
            if (vr.getWarning() != null) meta.getWarnings().add(vr.getWarning());
            return;
        }

        int verified = 0;
        List<String> outputs = vr.getOutputs();
        boolean sql = isSqlLanguage(refLang);
        for (int i = 0; i < draft.getTestCases().size(); i++) {
            ProblemDraft.TestCaseDraft tc = draft.getTestCases().get(i);
            String produced = i < outputs.size() ? outputs.get(i) : null;
            if (produced != null) {
                tc.setExpectedOutput(produced); // ground truth from real execution
                tc.setVerified(true);
                tc.setNote(null);
                verified++;

                // "Ran cleanly" and "produced zero rows" both come back as an empty string,
                // so a schema with no seed INSERTs looks identical to a legitimate empty-result
                // case. Surface it as a warning instead of silently calling it Verified.
                if (sql && produced.isBlank()) {
                    boolean hasSeedData = tc.getInput() != null
                            && tc.getInput().toUpperCase(Locale.ROOT).contains("INSERT");
                    String reason = hasSeedData
                            ? "the query matched zero rows"
                            : "its input has no INSERT statements, so the table is empty";
                    meta.getWarnings().add("Test case " + (i + 1) + " ran without errors but produced no output ("
                            + reason + "). Confirm this is intentional before saving.");
                }
            } else {
                tc.setVerified(false);
                tc.setNote("Reference solution did not run cleanly on this input; output is AI-generated.");
            }
        }
        meta.setVerifiedCount(verified);
        meta.setVerified(verified == draft.getTestCases().size() && verified > 0);

        if (verified < draft.getTestCases().size()) {
            meta.getWarnings().add(verified + "/" + draft.getTestCases().size()
                    + " test cases were verified by running the reference solution.");
        }
    }

    private static boolean isSqlLanguage(String name) {
        if (name == null) return false;
        return switch (name.trim().toLowerCase()) {
            case "sql", "sqlite", "sqlite3", "mysql", "postgres", "postgresql" -> true;
            default -> false;
        };
    }

    private ProblemDraft cloneWithoutMeta(ProblemDraft current) throws Exception {
        ProblemDraft copy = objectMapper.readValue(
                objectMapper.writeValueAsString(current), ProblemDraft.class);
        copy.setMeta(null);
        return copy;
    }
}
