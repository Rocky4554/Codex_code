package com.codex.platform.config;

import com.codex.platform.common.enums.ProblemDifficulty;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.ProblemExample;
import com.codex.platform.problem.entity.TestCase;
import com.codex.platform.problem.repository.ProblemExampleRepository;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.problem.repository.TestCaseRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.UUID;

/**
 * Curated catalog sync runs on {@link ApplicationReadyEvent} so the servlet container and health
 * checks can complete before a long DB upsert, and to avoid the Render/SIGTERM race with
 * {@code CommandLineRunner} when startup takes minutes.
 */
@Component
@Order(10)
@RequiredArgsConstructor
@Slf4j
public class CuratedProblemCatalogInitializer {

    private final ProblemRepository problemRepository;
    private final ProblemExampleRepository exampleRepository;
    private final TestCaseRepository testCaseRepository;
    private final ObjectMapper objectMapper;

    @EventListener(ApplicationReadyEvent.class)
    @Transactional
    public void onApplicationReady() throws Exception {
        int upserted = 0;
        for (ProblemSeed seed : catalog()) {
            upsert(seed);
            upserted++;
        }
        log.info("Curated problem catalog synced: {} problem(s)", upserted);
    }

    private void upsert(ProblemSeed seed) throws Exception {
        Problem problem = problemRepository.findByTitleIgnoreCase(seed.title()).orElseGet(Problem::new);
        problem.setTitle(seed.title());
        problem.setDescription(seed.description());
        problem.setDifficulty(seed.difficulty());
        problem.setTimeLimitMs(5000);
        problem.setMemoryLimitMb(256);
        problem.setOrderNum(seed.orderNum());
        problem.setConstraintsJson(seed.constraints().isEmpty() ? null : objectMapper.writeValueAsString(seed.constraints()));
        problem.setTopicsJson(seed.topics().isEmpty() ? null : objectMapper.writeValueAsString(seed.topics()));
        Problem saved = problemRepository.save(problem);

        replaceExamples(saved.getId(), seed.examples());
        replaceTestCases(saved.getId(), seed.testCases());
    }

    private void replaceExamples(UUID problemId, List<ExampleSeed> examples) {
        exampleRepository.deleteByProblemId(problemId);
        if (examples.isEmpty()) return;
        List<ProblemExample> rows = examples.stream()
                .map(example -> {
                    ProblemExample row = new ProblemExample();
                    row.setProblemId(problemId);
                    row.setInput(example.input());
                    row.setOutput(example.output());
                    row.setExplanation(example.explanation());
                    row.setDisplayOrder(example.displayOrder());
                    return row;
                })
                .toList();
        exampleRepository.saveAll(rows);
    }

    private void replaceTestCases(UUID problemId, List<TestCaseSeed> testCases) {
        testCaseRepository.deleteByProblemId(problemId);
        List<TestCase> rows = testCases.stream()
                .map(testCase -> {
                    TestCase row = new TestCase();
                    row.setProblemId(problemId);
                    row.setInput(testCase.input());
                    row.setExpectedOutput(testCase.expectedOutput());
                    row.setIsSample(testCase.sample());
                    return row;
                })
                .toList();
        testCaseRepository.saveAll(rows);
    }

    private List<ProblemSeed> catalog() {
        return List.of(
                seed(
                        1,
                        "Reverse an Array",
                        ProblemDifficulty.EASY,
                        "Read an integer array and print it in reverse order.\nInput: one line of space-separated integers.\nOutput: the reversed array as space-separated integers.",
                        List.of("Array"),
                        List.of("1 <= n <= 10^5"),
                        List.of(ex("1 2 3 4 5", "5 4 3 2 1", "Reverse the order of all elements.")),
                        List.of(tc("1 2 3 4 5", "5 4 3 2 1", true), tc("9", "9", false))
                ),
                seed(
                        2,
                        "Find Largest / Smallest Element",
                        ProblemDifficulty.EASY,
                        "Find the largest and smallest element in an integer array.\nInput: one line of space-separated integers.\nOutput: print '<largest> <smallest>'.",
                        List.of("Array"),
                        List.of("1 <= n <= 10^5"),
                        List.of(ex("4 7 1 9 3", "9 1", "Largest is 9 and smallest is 1.")),
                        List.of(tc("4 7 1 9 3", "9 1", true), tc("-5 -2 -9 -1", "-1 -9", false))
                ),
                seed(
                        3,
                        "Find Second Largest Number",
                        ProblemDifficulty.EASY,
                        "Find the second largest distinct number in an array.\nInput: one line of space-separated integers.\nOutput: the second largest distinct value, or -1 if it does not exist.",
                        List.of("Array"),
                        List.of("1 <= n <= 10^5"),
                        List.of(ex("10 5 8 20 15", "15", "20 is largest, 15 is second largest.")),
                        List.of(tc("10 5 8 20 15", "15", true), tc("7 7 7", "-1", false))
                ),
                seed(
                        4,
                        "Remove Duplicates from Sorted Array",
                        ProblemDifficulty.EASY,
                        "Remove duplicates from a sorted array and print the unique values in order.\nInput: one line of sorted space-separated integers.\nOutput: the de-duplicated array.",
                        List.of("Array", "Two Pointers"),
                        List.of("Array is already sorted"),
                        List.of(ex("1 1 2 2 3 4 4", "1 2 3 4", "Keep only the first occurrence of each value.")),
                        List.of(tc("1 1 2 2 3 4 4", "1 2 3 4", true), tc("5 5 5 5", "5", false))
                ),
                seed(
                        5,
                        "Move All Zeros to End",
                        ProblemDifficulty.EASY,
                        "Move all zero values to the end while preserving the relative order of non-zero elements.\nInput: one line of space-separated integers.\nOutput: the transformed array.",
                        List.of("Array", "Two Pointers"),
                        List.of(),
                        List.of(ex("0 1 0 3 12", "1 3 12 0 0", "Non-zero elements stay in order.")),
                        List.of(tc("0 1 0 3 12", "1 3 12 0 0", true), tc("1 2 3", "1 2 3", false))
                ),
                seed(
                        6,
                        "Rotate Array by K Positions",
                        ProblemDifficulty.MEDIUM,
                        "Rotate an array to the right by k positions.\nInput: first line has the array, second line has k.\nOutput: the rotated array.",
                        List.of("Array"),
                        List.of("0 <= k <= 10^9"),
                        List.of(ex("1 2 3 4 5\n2", "4 5 1 2 3", "Rotate right by 2.")),
                        List.of(tc("1 2 3 4 5\n2", "4 5 1 2 3", true), tc("10 20 30\n4", "30 10 20", false))
                ),
                seed(
                        7,
                        "Find Missing Number in Array",
                        ProblemDifficulty.EASY,
                        "The array contains n distinct numbers from 0 to n with one number missing.\nInput: one line of space-separated integers.\nOutput: the missing number.",
                        List.of("Array", "Math"),
                        List.of("Values are distinct"),
                        List.of(ex("3 0 1", "2", "2 is missing from the range 0..3.")),
                        List.of(tc("3 0 1", "2", true), tc("0 1", "2", false))
                ),
                seed(
                        8,
                        "Find Duplicates in Array",
                        ProblemDifficulty.EASY,
                        "Print all values that appear more than once.\nInput: one line of space-separated integers.\nOutput: duplicate values in ascending order, or NONE if no duplicates exist.",
                        List.of("Array", "Hash Map"),
                        List.of(),
                        List.of(ex("4 3 2 7 8 2 3 1", "2 3", "2 and 3 appear twice.")),
                        List.of(tc("4 3 2 7 8 2 3 1", "2 3", true), tc("1 2 3 4", "NONE", false))
                ),
                seed(
                        9,
                        "Merge Two Sorted Arrays",
                        ProblemDifficulty.MEDIUM,
                        "Merge two already-sorted integer arrays.\nInput: first line has array A, second line has array B.\nOutput: the merged sorted array.",
                        List.of("Array", "Two Pointers"),
                        List.of(),
                        List.of(ex("1 2 3\n2 5 6", "1 2 2 3 5 6", "Merge both sorted arrays.")),
                        List.of(tc("1 2 3\n2 5 6", "1 2 2 3 5 6", true), tc("-5 -3\n-4 -2 0", "-5 -4 -3 -2 0", false))
                ),
                seed(
                        10,
                        "Two Sum",
                        ProblemDifficulty.EASY,
                        "Find the indices of the two numbers that add up to target.\nInput: first line has the array, second line has target.\nOutput: the two indices in ascending order.",
                        List.of("Array", "Hash Table"),
                        List.of("Exactly one answer exists"),
                        List.of(ex("2 7 11 15\n9", "0 1", "nums[0] + nums[1] = 9.")),
                        List.of(tc("2 7 11 15\n9", "0 1", true), tc("3 2 4\n6", "1 2", false))
                ),
                seed(
                        11,
                        "Reverse String",
                        ProblemDifficulty.EASY,
                        "Read a string and print it reversed.\nInput: one line string.\nOutput: the reversed string.",
                        List.of("String"),
                        List.of(),
                        List.of(ex("hello", "olleh", "Reverse character order.")),
                        List.of(tc("hello", "olleh", true), tc("Hannah", "hannaH", false))
                ),
                seed(
                        12,
                        "Check Palindrome",
                        ProblemDifficulty.EASY,
                        "Check whether a string is a palindrome.\nInput: one line string.\nOutput: true or false.",
                        List.of("String", "Two Pointers"),
                        List.of("Case-sensitive"),
                        List.of(ex("madam", "true", "The string reads the same both ways.")),
                        List.of(tc("madam", "true", true), tc("hello", "false", false))
                ),
                seed(
                        13,
                        "Count Vowels",
                        ProblemDifficulty.EASY,
                        "Count vowels in a string.\nInput: one line string.\nOutput: the number of vowels.",
                        List.of("String"),
                        List.of("Treat a, e, i, o, u as vowels"),
                        List.of(ex("programming", "3", "The vowels are o, a, i.")),
                        List.of(tc("programming", "3", true), tc("AEIOU", "5", false))
                ),
                seed(
                        14,
                        "First Non-Repeating Character",
                        ProblemDifficulty.MEDIUM,
                        "Find the first character that appears exactly once.\nInput: one line string.\nOutput: the character, or -1 if none exists.",
                        List.of("String", "Hash Map"),
                        List.of(),
                        List.of(ex("swiss", "w", "w is the first non-repeating character.")),
                        List.of(tc("swiss", "w", true), tc("aabbcc", "-1", false))
                ),
                seed(
                        15,
                        "Check Anagram",
                        ProblemDifficulty.EASY,
                        "Check whether two strings are anagrams.\nInput: first line string a, second line string b.\nOutput: true or false.",
                        List.of("String", "Hash Map"),
                        List.of("Case-sensitive"),
                        List.of(ex("listen\nsilent", "true", "Both strings contain the same characters.")),
                        List.of(tc("listen\nsilent", "true", true), tc("rat\ncar", "false", false))
                ),
                seed(
                        16,
                        "Longest Common Prefix",
                        ProblemDifficulty.MEDIUM,
                        "Find the longest common prefix among strings.\nInput: first line n, followed by n lines.\nOutput: the prefix, or an empty line.",
                        List.of("String"),
                        List.of("1 <= n <= 10^3"),
                        List.of(ex("3\nflower\nflow\nflight", "fl", "All strings share the prefix 'fl'.")),
                        List.of(tc("3\nflower\nflow\nflight", "fl", true), tc("3\ndog\nracecar\ncar", "", false))
                ),
                seed(
                        17,
                        "Remove Duplicate Characters",
                        ProblemDifficulty.EASY,
                        "Remove duplicate characters while preserving first appearance order.\nInput: one line string.\nOutput: the de-duplicated string.",
                        List.of("String", "Hash Set"),
                        List.of(),
                        List.of(ex("programming", "progamin", "Keep only first appearances.")),
                        List.of(tc("programming", "progamin", true), tc("aaaa", "a", false))
                ),
                seed(
                        18,
                        "String Compression",
                        ProblemDifficulty.MEDIUM,
                        "Compress consecutive repeating characters using count notation.\nInput: one line string.\nOutput: the compressed string like a2b1c5a3.",
                        List.of("String"),
                        List.of("Input is non-empty"),
                        List.of(ex("aabcccccaaa", "a2b1c5a3", "Count consecutive repeating characters.")),
                        List.of(tc("aabcccccaaa", "a2b1c5a3", true), tc("abcd", "a1b1c1d1", false))
                ),
                seed(
                        19,
                        "Frequency of Elements",
                        ProblemDifficulty.EASY,
                        "Count the frequency of each distinct integer.\nInput: one line of space-separated integers.\nOutput: key:value pairs sorted by key ascending.",
                        List.of("Hash Map"),
                        List.of("Format output exactly as '1:2 3:1'"),
                        List.of(ex("1 2 2 3 3 3", "1:1 2:2 3:3", "Count every distinct value.")),
                        List.of(tc("1 2 2 3 3 3", "1:1 2:2 3:3", true), tc("5 5 5", "5:3", false))
                ),
                seed(
                        20,
                        "Find First Duplicate",
                        ProblemDifficulty.EASY,
                        "Return the first value whose second occurrence appears earliest.\nInput: one line of space-separated integers.\nOutput: the first duplicate value, or -1.",
                        List.of("Hash Map"),
                        List.of(),
                        List.of(ex("2 1 3 5 3 2", "3", "3 is the first value to repeat.")),
                        List.of(tc("2 1 3 5 3 2", "3", true), tc("1 2 3 4", "-1", false))
                ),
                seed(
                        21,
                        "Group Anagrams",
                        ProblemDifficulty.MEDIUM,
                        "Group words that are anagrams.\nInput: first line n, then n words.\nOutput: words inside each group sorted alphabetically, groups ordered by their first word, groups separated by ' | '.",
                        List.of("Hash Map", "String"),
                        List.of(),
                        List.of(ex("6\neat\ntea\ntan\nate\nnat\nbat", "ate eat tea | bat | nat tan", "Words with the same sorted signature belong together.")),
                        List.of(tc("6\neat\ntea\ntan\nate\nnat\nbat", "ate eat tea | bat | nat tan", true), tc("3\nabc\nbca\nxyz", "abc bca | xyz", false))
                ),
                seed(
                        22,
                        "Count Occurrences in Array",
                        ProblemDifficulty.EASY,
                        "Count how many times a target appears in an array.\nInput: first line array, second line target.\nOutput: occurrence count.",
                        List.of("Hash Map", "Array"),
                        List.of(),
                        List.of(ex("1 2 2 2 3 4\n2", "3", "2 appears three times.")),
                        List.of(tc("1 2 2 2 3 4\n2", "3", true), tc("5 6 7\n1", "0", false))
                ),
                seed(
                        23,
                        "Find Intersection of Arrays",
                        ProblemDifficulty.EASY,
                        "Print the unique intersection of two arrays in ascending order.\nInput: first line array A, second line array B.\nOutput: intersecting values, or NONE.",
                        List.of("Hash Set", "Array"),
                        List.of(),
                        List.of(ex("1 2 2 3 4\n2 2 4 6", "2 4", "The common unique values are 2 and 4.")),
                        List.of(tc("1 2 2 3 4\n2 2 4 6", "2 4", true), tc("1 3 5\n2 4 6", "NONE", false))
                ),
                seed(
                        24,
                        "Reverse Linked List",
                        ProblemDifficulty.EASY,
                        "A linked list is provided as space-separated node values.\nInput: one line list values.\nOutput: the reversed list values.",
                        List.of("Linked List"),
                        List.of(),
                        List.of(ex("1 2 3 4 5", "5 4 3 2 1", "Reverse the node links.")),
                        List.of(tc("1 2 3 4 5", "5 4 3 2 1", true), tc("7", "7", false))
                ),
                seed(
                        25,
                        "Detect Cycle in Linked List",
                        ProblemDifficulty.MEDIUM,
                        "Build a linked list from values and connect the tail to the node at index pos.\nInput: first line values, second line pos (-1 for no cycle).\nOutput: true or false.",
                        List.of("Linked List", "Two Pointers"),
                        List.of("0-indexed pos"),
                        List.of(ex("3 2 0 -4\n1", "true", "Tail connects back to value 2 at index 1.")),
                        List.of(tc("3 2 0 -4\n1", "true", true), tc("1 2 3\n-1", "false", false))
                ),
                seed(
                        26,
                        "Find Middle Node",
                        ProblemDifficulty.EASY,
                        "Return the middle node value of a linked list.\nInput: one line list values.\nOutput: the middle node value. For even length, return the second middle.",
                        List.of("Linked List", "Two Pointers"),
                        List.of(),
                        List.of(ex("1 2 3 4 5", "3", "3 is the middle node.")),
                        List.of(tc("1 2 3 4 5", "3", true), tc("1 2 3 4 5 6", "4", false))
                ),
                seed(
                        27,
                        "Remove Nth Node From End",
                        ProblemDifficulty.MEDIUM,
                        "Remove the nth node from the end of a linked list.\nInput: first line values, second line n.\nOutput: the resulting list values, or EMPTY.",
                        List.of("Linked List", "Two Pointers"),
                        List.of("1 <= n <= list length"),
                        List.of(ex("1 2 3 4 5\n2", "1 2 3 5", "Remove the 2nd node from the end.")),
                        List.of(tc("1 2 3 4 5\n2", "1 2 3 5", true), tc("1\n1", "EMPTY", false))
                ),
                seed(
                        28,
                        "Merge Two Sorted Linked Lists",
                        ProblemDifficulty.MEDIUM,
                        "Merge two sorted linked lists.\nInput: first line list A, second line list B.\nOutput: merged sorted list values.",
                        List.of("Linked List"),
                        List.of(),
                        List.of(ex("1 2 4\n1 3 4", "1 1 2 3 4 4", "Merge both sorted lists.")),
                        List.of(tc("1 2 4\n1 3 4", "1 1 2 3 4 4", true), tc("1 5 7\n2 6 8", "1 2 5 6 7 8", false))
                ),
                seed(
                        29,
                        "Valid Parentheses",
                        ProblemDifficulty.EASY,
                        "Check whether a bracket string is valid.\nInput: one line string containing ()[]{}.\nOutput: true or false.",
                        List.of("Stack", "String"),
                        List.of(),
                        List.of(ex("()[]{}", "true", "Every opening bracket is properly closed.")),
                        List.of(tc("()[]{}", "true", true), tc("([)]", "false", false))
                ),
                seed(
                        30,
                        "Implement Stack Using Array",
                        ProblemDifficulty.EASY,
                        "Simulate a stack using an array.\nInput: first line q, followed by q commands (push x, pop, top, empty).\nOutput: print results of pop/top/empty commands line by line.",
                        List.of("Stack"),
                        List.of(),
                        List.of(ex("6\npush 1\npush 2\ntop\npop\nempty\npop", "2\n2\nfalse\n1", "Only commands that query the stack produce output.")),
                        List.of(tc("6\npush 1\npush 2\ntop\npop\nempty\npop", "2\n2\nfalse\n1", true), tc("4\npush 7\nempty\npop\nempty", "false\n7\ntrue", false))
                ),
                seed(
                        31,
                        "Implement Queue Using Array",
                        ProblemDifficulty.EASY,
                        "Simulate a queue using an array.\nInput: first line q, followed by q commands (enqueue x, dequeue, front, empty).\nOutput: print results of dequeue/front/empty commands line by line.",
                        List.of("Queue"),
                        List.of(),
                        List.of(ex("6\nenqueue 1\nenqueue 2\nfront\ndequeue\nempty\ndequeue", "1\n1\nfalse\n2", "FIFO order must be preserved.")),
                        List.of(tc("6\nenqueue 1\nenqueue 2\nfront\ndequeue\nempty\ndequeue", "1\n1\nfalse\n2", true), tc("4\nenqueue 7\nempty\ndequeue\nempty", "false\n7\ntrue", false))
                ),
                seed(
                        32,
                        "Next Greater Element",
                        ProblemDifficulty.MEDIUM,
                        "For every element, find the next greater element to its right.\nInput: one line of space-separated integers.\nOutput: the answer array using -1 where no greater element exists.",
                        List.of("Stack", "Array"),
                        List.of(),
                        List.of(ex("2 1 2 4 3", "4 2 4 -1 -1", "Use a monotonic stack.")),
                        List.of(tc("2 1 2 4 3", "4 2 4 -1 -1", true), tc("4 3 2 1", "-1 -1 -1 -1", false))
                ),
                seed(
                        33,
                        "Min Stack",
                        ProblemDifficulty.MEDIUM,
                        "Implement a stack that supports getMin in O(1).\nInput: first line q, then commands (push x, pop, top, getMin).\nOutput: print results of pop/top/getMin commands line by line.",
                        List.of("Stack"),
                        List.of(),
                        List.of(ex("8\npush -2\npush 0\npush -3\ngetMin\npop\ntop\ngetMin\npop", "-3\n-3\n0\n-2", "Track the current minimum at each step.")),
                        List.of(tc("8\npush -2\npush 0\npush -3\ngetMin\npop\ntop\ngetMin\npop", "-3\n-3\n0\n-2", true), tc("5\npush 5\npush 4\ngetMin\npop\ngetMin", "4\n4\n5", false))
                ),
                seed(
                        34,
                        "Inorder Traversal",
                        ProblemDifficulty.MEDIUM,
                        "Traverse a binary tree in inorder.\nInput: one line level-order values using 'null' for missing nodes.\nOutput: inorder traversal values.",
                        List.of("Tree", "DFS"),
                        List.of(),
                        List.of(ex("1 null 2 3", "1 3 2", "Visit left, root, right.")),
                        List.of(tc("1 null 2 3", "1 3 2", true), tc("4 2 6 1 3 5 7", "1 2 3 4 5 6 7", false))
                ),
                seed(
                        35,
                        "Preorder Traversal",
                        ProblemDifficulty.MEDIUM,
                        "Traverse a binary tree in preorder.\nInput: one line level-order values using 'null' for missing nodes.\nOutput: preorder traversal values.",
                        List.of("Tree", "DFS"),
                        List.of(),
                        List.of(ex("1 null 2 3", "1 2 3", "Visit root, left, right.")),
                        List.of(tc("1 null 2 3", "1 2 3", true), tc("4 2 6 1 3 5 7", "4 2 1 3 6 5 7", false))
                ),
                seed(
                        36,
                        "Level Order Traversal",
                        ProblemDifficulty.MEDIUM,
                        "Traverse a binary tree level by level.\nInput: one line level-order values using 'null' for missing nodes.\nOutput: levels separated by ' | '.",
                        List.of("Tree", "BFS"),
                        List.of(),
                        List.of(ex("3 9 20 null null 15 7", "3 | 9 20 | 15 7", "Breadth-first traversal grouped by depth.")),
                        List.of(tc("3 9 20 null null 15 7", "3 | 9 20 | 15 7", true), tc("1", "1", false))
                ),
                seed(
                        37,
                        "Height of Tree",
                        ProblemDifficulty.EASY,
                        "Find the height (number of levels) of a binary tree.\nInput: one line level-order values using 'null' for missing nodes.\nOutput: the height.",
                        List.of("Tree", "DFS"),
                        List.of(),
                        List.of(ex("3 9 20 null null 15 7", "3", "The tree has three levels.")),
                        List.of(tc("3 9 20 null null 15 7", "3", true), tc("1", "1", false))
                ),
                seed(
                        38,
                        "Check Balanced Tree",
                        ProblemDifficulty.MEDIUM,
                        "Determine whether a binary tree is height-balanced.\nInput: one line level-order values using 'null' for missing nodes.\nOutput: true or false.",
                        List.of("Tree", "DFS"),
                        List.of(),
                        List.of(ex("3 9 20 null null 15 7", "true", "The subtree heights differ by at most 1.")),
                        List.of(tc("3 9 20 null null 15 7", "true", true), tc("1 2 2 3 3 null null 4 4", "false", false))
                ),
                seed(
                        39,
                        "Factorial",
                        ProblemDifficulty.EASY,
                        "Compute n!.\nInput: one integer n.\nOutput: factorial of n.",
                        List.of("Recursion", "Math"),
                        List.of("0 <= n <= 20"),
                        List.of(ex("5", "120", "5! = 120.")),
                        List.of(tc("5", "120", true), tc("0", "1", false))
                ),
                seed(
                        40,
                        "Fibonacci",
                        ProblemDifficulty.EASY,
                        "Compute the nth Fibonacci number.\nInput: one integer n.\nOutput: F(n).",
                        List.of("Recursion", "DP"),
                        List.of("0 <= n <= 30"),
                        List.of(ex("10", "55", "The 10th Fibonacci number is 55.")),
                        List.of(tc("10", "55", true), tc("0", "0", false))
                ),
                seed(
                        41,
                        "Print 1 to N",
                        ProblemDifficulty.EASY,
                        "Print integers from 1 to N using recursion.\nInput: one integer n.\nOutput: numbers from 1 to n separated by spaces.",
                        List.of("Recursion"),
                        List.of("1 <= n <= 1000"),
                        List.of(ex("5", "1 2 3 4 5", "Print all numbers in ascending order.")),
                        List.of(tc("5", "1 2 3 4 5", true), tc("1", "1", false))
                ),
                seed(
                        42,
                        "Sum of Digits",
                        ProblemDifficulty.EASY,
                        "Find the sum of digits of a non-negative integer using recursion.\nInput: one integer n.\nOutput: digit sum.",
                        List.of("Recursion", "Math"),
                        List.of(),
                        List.of(ex("12345", "15", "1+2+3+4+5 = 15.")),
                        List.of(tc("12345", "15", true), tc("0", "0", false))
                ),
                seed(
                        43,
                        "Reverse String Using Recursion",
                        ProblemDifficulty.EASY,
                        "Reverse a string using recursion.\nInput: one line string.\nOutput: reversed string.",
                        List.of("Recursion", "String"),
                        List.of(),
                        List.of(ex("codex", "xedoc", "Reverse the string recursively.")),
                        List.of(tc("codex", "xedoc", true), tc("a", "a", false))
                ),
                seed(
                        44,
                        "Binary Search",
                        ProblemDifficulty.EASY,
                        "Find the index of target in a sorted array using binary search.\nInput: first line sorted array, second line target.\nOutput: index or -1.",
                        List.of("Binary Search", "Array"),
                        List.of("Array is sorted ascending"),
                        List.of(ex("-1 0 3 5 9 12\n9", "4", "9 is found at index 4.")),
                        List.of(tc("-1 0 3 5 9 12\n9", "4", true), tc("-1 0 3 5 9 12\n2", "-1", false))
                ),
                seed(
                        45,
                        "Bubble Sort",
                        ProblemDifficulty.EASY,
                        "Sort an integer array using bubble sort.\nInput: one line of space-separated integers.\nOutput: sorted array ascending.",
                        List.of("Sorting", "Array"),
                        List.of(),
                        List.of(ex("5 1 4 2 8", "1 2 4 5 8", "Repeatedly swap adjacent out-of-order values.")),
                        List.of(tc("5 1 4 2 8", "1 2 4 5 8", true), tc("3 3 2 1", "1 2 3 3", false))
                ),
                seed(
                        46,
                        "Selection Sort",
                        ProblemDifficulty.EASY,
                        "Sort an integer array using selection sort.\nInput: one line of space-separated integers.\nOutput: sorted array ascending.",
                        List.of("Sorting", "Array"),
                        List.of(),
                        List.of(ex("64 25 12 22 11", "11 12 22 25 64", "Select the minimum each pass.")),
                        List.of(tc("64 25 12 22 11", "11 12 22 25 64", true), tc("5 4 3 2 1", "1 2 3 4 5", false))
                ),
                seed(
                        47,
                        "Merge Sort",
                        ProblemDifficulty.MEDIUM,
                        "Sort an integer array using merge sort.\nInput: one line of space-separated integers.\nOutput: sorted array ascending.",
                        List.of("Sorting", "Divide and Conquer"),
                        List.of(),
                        List.of(ex("38 27 43 3 9 82 10", "3 9 10 27 38 43 82", "Split, sort, then merge.")),
                        List.of(tc("38 27 43 3 9 82 10", "3 9 10 27 38 43 82", true), tc("2 1", "1 2", false))
                ),
                seed(
                        48,
                        "Quick Sort",
                        ProblemDifficulty.MEDIUM,
                        "Sort an integer array using quick sort.\nInput: one line of space-separated integers.\nOutput: sorted array ascending.",
                        List.of("Sorting", "Divide and Conquer"),
                        List.of(),
                        List.of(ex("10 7 8 9 1 5", "1 5 7 8 9 10", "Partition around a pivot and recurse.")),
                        List.of(tc("10 7 8 9 1 5", "1 5 7 8 9 10", true), tc("4 2 6 2 1", "1 2 2 4 6", false))
                )
        );
    }

    private ProblemSeed seed(
            int orderNum,
            String title,
            ProblemDifficulty difficulty,
            String description,
            List<String> topics,
            List<String> constraints,
            List<ExampleSeed> examples,
            List<TestCaseSeed> testCases
    ) {
        return new ProblemSeed(title, description, difficulty, orderNum, constraints, topics, examples, testCases);
    }

    private ExampleSeed ex(String input, String output, String explanation) {
        return new ExampleSeed(input, output, explanation, 0);
    }

    private TestCaseSeed tc(String input, String expectedOutput, boolean sample) {
        return new TestCaseSeed(input, expectedOutput, sample);
    }

    private record ProblemSeed(
            String title,
            String description,
            ProblemDifficulty difficulty,
            int orderNum,
            List<String> constraints,
            List<String> topics,
            List<ExampleSeed> examples,
            List<TestCaseSeed> testCases
    ) {}

    private record ExampleSeed(
            String input,
            String output,
            String explanation,
            Integer displayOrder
    ) {}

    private record TestCaseSeed(
            String input,
            String expectedOutput,
            boolean sample
    ) {}
}
