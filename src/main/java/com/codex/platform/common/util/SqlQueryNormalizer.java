package com.codex.platform.common.util;

/**
 * Ensures a single-statement SQL reference query has a deterministic top-level
 * {@code ORDER BY}.
 *
 * <p>The judge compares SQLite stdout line-by-line ({@link OutputNormalizer}), so a
 * query whose row order is unspecified passes or fails at random depending on
 * SQLite's internal query plan. Problem authoring (both AI-generated and
 * manually-verified reference queries) runs every query through this first so
 * saved test cases are deterministic regardless of who wrote the query.
 */
public final class SqlQueryNormalizer {

    private SqlQueryNormalizer() {
    }

    public record Result(String sql, boolean appended) {
    }

    /** Appends {@code ORDER BY 1} when the query has no top-level ORDER BY clause. */
    public static Result ensureOrderBy(String sql) {
        if (sql == null || sql.isBlank()) {
            return new Result(sql, false);
        }

        String trimmed = sql.strip();
        boolean hadSemicolon = trimmed.endsWith(";");
        String body = hadSemicolon ? trimmed.substring(0, trimmed.length() - 1).stripTrailing() : trimmed;

        if (hasTopLevelOrderBy(body)) {
            return new Result(sql, false);
        }

        String withOrderBy = body + " ORDER BY 1";
        return new Result(hadSemicolon ? withOrderBy + ";" : withOrderBy, true);
    }

    /** Scans for an "ORDER BY" keyword outside of parentheses (subqueries) and string literals. */
    private static boolean hasTopLevelOrderBy(String sql) {
        int depth = 0;
        char quote = 0;
        for (int i = 0; i < sql.length(); i++) {
            char c = sql.charAt(i);
            if (quote != 0) {
                if (c == quote) quote = 0;
                continue;
            }
            if (c == '\'' || c == '"') {
                quote = c;
                continue;
            }
            if (c == '(') {
                depth++;
                continue;
            }
            if (c == ')') {
                depth = Math.max(0, depth - 1);
                continue;
            }
            if (depth == 0 && isOrderByAt(sql, i)) {
                return true;
            }
        }
        return false;
    }

    private static boolean isOrderByAt(String sql, int i) {
        int len = sql.length();
        if (!sql.regionMatches(true, i, "order", 0, 5)) return false;
        if (i > 0 && Character.isLetterOrDigit(sql.charAt(i - 1))) return false; // whole word only
        int j = i + 5;
        if (j >= len || !Character.isWhitespace(sql.charAt(j))) return false;
        while (j < len && Character.isWhitespace(sql.charAt(j))) j++;
        if (j + 2 > len || !sql.regionMatches(true, j, "by", 0, 2)) return false;
        int after = j + 2;
        return after >= len || !Character.isLetterOrDigit(sql.charAt(after));
    }
}
