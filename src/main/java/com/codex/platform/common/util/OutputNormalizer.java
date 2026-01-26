package com.codex.platform.common.util;

public class OutputNormalizer {

    /**
     * Normalizes output for comparison:
     * - Trims leading/trailing whitespace
     * - Normalizes newlines to \n
     * - Removes trailing spaces from each line
     * - Removes empty lines at the end
     */
    public static String normalize(String output) {
        if (output == null) {
            return "";
        }

        // Normalize newlines
        String normalized = output.replace("\r\n", "\n").replace("\r", "\n");

        // Split into lines, trim trailing spaces from each line
        String[] lines = normalized.split("\n");
        StringBuilder sb = new StringBuilder();

        for (String line : lines) {
            sb.append(line.replaceAll("\\s+$", "")).append("\n");
        }

        // Remove trailing newlines and trim
        return sb.toString().replaceAll("\n+$", "").trim();
    }

    /**
     * Compares two outputs after normalization
     */
    public static boolean areEqual(String expected, String actual) {
        return normalize(expected).equals(normalize(actual));
    }
}
