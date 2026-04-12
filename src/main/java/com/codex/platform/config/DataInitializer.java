package com.codex.platform.config;

import com.codex.platform.common.enums.ProblemDifficulty;
import com.codex.platform.execution.entity.Language;
import com.codex.platform.execution.repository.LanguageRepository;
import com.codex.platform.problem.entity.Problem;
import com.codex.platform.problem.entity.TestCase;
import com.codex.platform.problem.repository.ProblemRepository;
import com.codex.platform.problem.repository.TestCaseRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
@Slf4j
public class DataInitializer implements CommandLineRunner {

    private final LanguageRepository languageRepository;
    private final ProblemRepository problemRepository;
    private final TestCaseRepository testCaseRepository;

    @Override
    public void run(String... args) {
        if (languageRepository.count() == 0) {
            initializeLanguages();
        }

        if (problemRepository.count() == 0) {
            initializeSampleProblems();
        } else {
            synchronizeTimeLimits();
        }    
    } 

    private void synchronizeTimeLimits() {
        log.info("Synchronizing time limits to 5s...");
        problemRepository.findAll().forEach(problem -> {
            if (problem.getTimeLimitMs() != 5000) {
                problem.setTimeLimitMs(5000);
                problemRepository.save(problem);
                log.info("Updated time limit for problem: {} to 5s", problem.getTitle());
            }
        });
    }

    private void initializeLanguages() {
        log.info("Initializing languages...");

        // Python (pre-compiled .pyc bytecode)
        Language python = new Language();
        python.setName("Python");
        python.setVersion("3.11");
        python.setDockerImage("codex-python:latest");
        python.setFileExtension(".py");
        python.setCompileCommand(null);
        python.setExecuteCommand("python solution.py");
        languageRepository.save(python);

        // Java (CDS archive for fast JVM startup)
        Language java = new Language();
        java.setName("Java");
        java.setVersion("17");
        java.setDockerImage("codex-java:latest");
        java.setFileExtension(".java");
        java.setCompileCommand("javac solution.java");
        java.setExecuteCommand("java -Xshare:on solution");
        languageRepository.save(java);

        // C++ (precompiled bits/stdc++.h header)
        Language cpp = new Language();
        cpp.setName("C++");
        cpp.setVersion("11");
        cpp.setDockerImage("codex-cpp:latest");
        cpp.setFileExtension(".cpp");
        cpp.setCompileCommand("g++ -std=c++11 -o solution solution.cpp");
        cpp.setExecuteCommand("./solution");
        languageRepository.save(cpp);

        // JavaScript (V8 module cache warmed)
        Language javascript = new Language();
        javascript.setName("JavaScript");
        javascript.setVersion("20");
        javascript.setDockerImage("codex-javascript:latest");
        javascript.setFileExtension(".js");
        javascript.setCompileCommand(null);
        javascript.setExecuteCommand("node solution.js");
        languageRepository.save(javascript);

        log.info("Languages initialized successfully");
    }

    private void initializeSampleProblems() {
        log.info("Initializing sample problems...");

        // Problem 1: Two Sum
        Problem twoSum = new Problem();
        twoSum.setTitle("Two Sum");
        twoSum.setDescription(
                "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nInput: First line contains space-separated integers (nums), second line contains target.\nOutput: Two space-separated indices.");
        twoSum.setDifficulty(ProblemDifficulty.EASY);
        twoSum.setTimeLimitMs(5000);
        twoSum.setMemoryLimitMb(256);
        Problem savedTwoSum = problemRepository.save(twoSum);

        // Test cases for Two Sum
        TestCase tc1 = new TestCase();
        tc1.setProblemId(savedTwoSum.getId());
        tc1.setInput("2 7 11 15\n9");
        tc1.setExpectedOutput("0 1");
        tc1.setIsSample(true);
        testCaseRepository.save(tc1);

        TestCase tc2 = new TestCase();
        tc2.setProblemId(savedTwoSum.getId());
        tc2.setInput("3 2 4\n6");
        tc2.setExpectedOutput("1 2");
        tc2.setIsSample(false);
        testCaseRepository.save(tc2);

        // Problem 2: Hello World
        Problem helloWorld = new Problem();
        helloWorld.setTitle("Hello World");
        helloWorld.setDescription("Print 'Hello, World!' to the console.");
        helloWorld.setDifficulty(ProblemDifficulty.EASY);
        helloWorld.setTimeLimitMs(5000);
        helloWorld.setMemoryLimitMb(128);
        Problem savedHelloWorld = problemRepository.save(helloWorld);

        // Test case for Hello World
        TestCase tcHello = new TestCase();
        tcHello.setProblemId(savedHelloWorld.getId());
        tcHello.setInput("");
        tcHello.setExpectedOutput("Hello, World!");
        tcHello.setIsSample(true);
        testCaseRepository.save(tcHello);

        // Problem 3: Reverse String (MEDIUM)
        Problem reverseString = new Problem();
        reverseString.setTitle("Reverse String");
        reverseString.setDescription(
                "Write a function that reverses a string. The input string is given as an array of characters.\n\n" +
                "You must do this by modifying the input array in-place with O(1) extra memory.\n\n" +
                "Input: A single line containing the string to reverse.\n" +
                "Output: The reversed string.");
        reverseString.setDifficulty(ProblemDifficulty.MEDIUM);
        reverseString.setTimeLimitMs(5000);
        reverseString.setMemoryLimitMb(256);
        Problem savedReverseString = problemRepository.save(reverseString);

        // Test cases for Reverse String
        TestCase tcRev1 = new TestCase();
        tcRev1.setProblemId(savedReverseString.getId());
        tcRev1.setInput("hello");
        tcRev1.setExpectedOutput("olleh");
        tcRev1.setIsSample(true);
        testCaseRepository.save(tcRev1);

        TestCase tcRev2 = new TestCase();
        tcRev2.setProblemId(savedReverseString.getId());
        tcRev2.setInput("Hannah");
        tcRev2.setExpectedOutput("hannaH");
        tcRev2.setIsSample(false);
        testCaseRepository.save(tcRev2);

        TestCase tcRev3 = new TestCase();
        tcRev3.setProblemId(savedReverseString.getId());
        tcRev3.setInput("A man a plan a canal Panama");
        tcRev3.setExpectedOutput("amanaP lanac a nalp a nam A");
        tcRev3.setIsSample(false);
        testCaseRepository.save(tcRev3);

        TestCase tcRev4 = new TestCase();
        tcRev4.setProblemId(savedReverseString.getId());
        tcRev4.setInput("1234567890");
        tcRev4.setExpectedOutput("0987654321");
        tcRev4.setIsSample(false);
        testCaseRepository.save(tcRev4);

        // Problem 4: Palindrome Number (MEDIUM)
        Problem palindromeNumber = new Problem();
        palindromeNumber.setTitle("Palindrome Number");
        palindromeNumber.setDescription(
                "Given an integer x, return true if x is a palindrome, and false otherwise.\n\n" +
                "An integer is a palindrome when it reads the same forward and backward.\n\n" +
                "Input: A single integer x.\n" +
                "Output: Print 'true' if x is a palindrome, 'false' otherwise.");
        palindromeNumber.setDifficulty(ProblemDifficulty.MEDIUM);
        palindromeNumber.setTimeLimitMs(5000);
        palindromeNumber.setMemoryLimitMb(256);
        Problem savedPalindromeNumber = problemRepository.save(palindromeNumber);

        // Test cases for Palindrome Number
        TestCase tcPal1 = new TestCase();
        tcPal1.setProblemId(savedPalindromeNumber.getId());
        tcPal1.setInput("121");
        tcPal1.setExpectedOutput("true");
        tcPal1.setIsSample(true);
        testCaseRepository.save(tcPal1);

        TestCase tcPal2 = new TestCase();
        tcPal2.setProblemId(savedPalindromeNumber.getId());
        tcPal2.setInput("-121");
        tcPal2.setExpectedOutput("false");
        tcPal2.setIsSample(true);
        testCaseRepository.save(tcPal2);

        TestCase tcPal3 = new TestCase();
        tcPal3.setProblemId(savedPalindromeNumber.getId());
        tcPal3.setInput("12321");
        tcPal3.setExpectedOutput("true");
        tcPal3.setIsSample(false);
        testCaseRepository.save(tcPal3);

        TestCase tcPal4 = new TestCase();
        tcPal4.setProblemId(savedPalindromeNumber.getId());
        tcPal4.setInput("123456");
        tcPal4.setExpectedOutput("false");
        tcPal4.setIsSample(false);
        testCaseRepository.save(tcPal4);

        TestCase tcPal5 = new TestCase();
        tcPal5.setProblemId(savedPalindromeNumber.getId());
        tcPal5.setInput("0");
        tcPal5.setExpectedOutput("true");
        tcPal5.setIsSample(false);
        testCaseRepository.save(tcPal5);

        // Problem 5: Factorial (EASY)
        Problem factorial = new Problem();
        factorial.setTitle("Factorial");
        factorial.setDescription(
                "Write a function to calculate the factorial of a given non-negative integer n.\n\n" +
                "The factorial of n is the product of all positive integers less than or equal to n.\n\n" +
                "Input: A single integer n (0 <= n <= 20).\n" +
                "Output: The factorial of n.");
        factorial.setDifficulty(ProblemDifficulty.EASY);
        factorial.setTimeLimitMs(5000);
        factorial.setMemoryLimitMb(256);
        Problem savedFactorial = problemRepository.save(factorial);

        // Test cases for Factorial
        TestCase tcFact1 = new TestCase();
        tcFact1.setProblemId(savedFactorial.getId());
        tcFact1.setInput("5");
        tcFact1.setExpectedOutput("120");
        tcFact1.setIsSample(true);
        testCaseRepository.save(tcFact1);

        TestCase tcFact2 = new TestCase();
        tcFact2.setProblemId(savedFactorial.getId());
        tcFact2.setInput("0");
        tcFact2.setExpectedOutput("1");
        tcFact2.setIsSample(true);
        testCaseRepository.save(tcFact2);

        TestCase tcFact3 = new TestCase();
        tcFact3.setProblemId(savedFactorial.getId());
        tcFact3.setInput("10");
        tcFact3.setExpectedOutput("3628800");
        tcFact3.setIsSample(false);
        testCaseRepository.save(tcFact3);

        TestCase tcFact4 = new TestCase();
        tcFact4.setProblemId(savedFactorial.getId());
        tcFact4.setInput("20");
        tcFact4.setExpectedOutput("2432902008176640000");
        tcFact4.setIsSample(false);
        testCaseRepository.save(tcFact4);

        // Problem 6: Longest Common Prefix (MEDIUM)
        Problem longestCommonPrefix = new Problem();
        longestCommonPrefix.setTitle("Longest Common Prefix");
        longestCommonPrefix.setDescription(
                "Write a function to find the longest common prefix string amongst an array of strings.\n\n" +
                "If there is no common prefix, return an empty string.\n\n" +
                "Input: First line contains n (number of strings), followed by n lines of strings.\n" +
                "Output: The longest common prefix.");
        longestCommonPrefix.setDifficulty(ProblemDifficulty.MEDIUM);
        longestCommonPrefix.setTimeLimitMs(5000);
        longestCommonPrefix.setMemoryLimitMb(256);
        Problem savedLCP = problemRepository.save(longestCommonPrefix);

        // Test cases for Longest Common Prefix
        TestCase tcLcp1 = new TestCase();
        tcLcp1.setProblemId(savedLCP.getId());
        tcLcp1.setInput("3\nflower\nflow\nflight");
        tcLcp1.setExpectedOutput("fl");
        tcLcp1.setIsSample(true);
        testCaseRepository.save(tcLcp1);

        TestCase tcLcp2 = new TestCase();
        tcLcp2.setProblemId(savedLCP.getId());
        tcLcp2.setInput("3\ndog\nracecar\ncar");
        tcLcp2.setExpectedOutput("");
        tcLcp2.setIsSample(true);
        testCaseRepository.save(tcLcp2);

        TestCase tcLcp3 = new TestCase();
        tcLcp3.setProblemId(savedLCP.getId());
        tcLcp3.setInput("1\nalone");
        tcLcp3.setExpectedOutput("alone");
        tcLcp3.setIsSample(false);
        testCaseRepository.save(tcLcp3);

        TestCase tcLcp4 = new TestCase();
        tcLcp4.setProblemId(savedLCP.getId());
        tcLcp4.setInput("4\ninterspecies\ninterstellar\ninterstate\ninternet");
        tcLcp4.setExpectedOutput("inters");
        tcLcp4.setIsSample(false);
        testCaseRepository.save(tcLcp4);

        // Problem 7: Merge Two Sorted Arrays (HARD)
        Problem mergeSortedArrays = new Problem();
        mergeSortedArrays.setTitle("Merge Two Sorted Arrays");
        mergeSortedArrays.setDescription(
                "You are given two integer arrays nums1 and nums2, sorted in non-decreasing order, " +
                "and two integers m and n, representing the number of elements in nums1 and nums2 respectively.\n\n" +
                "Merge nums1 and nums2 into a single array sorted in non-decreasing order.\n\n" +
                "The final sorted array should not be returned by the function, but instead be stored inside nums1. " +
                "To accommodate this, nums1 has a length of m + n, where the first m elements denote the elements that should be merged, " +
                "and the last n elements are set to 0 and should be ignored. nums2 has a length of n.\n\n" +
                "Input: First line contains m and n.\n" +
                "Second line contains m integers (nums1).\n" +
                "Third line contains n integers (nums2).\n" +
                "Output: m+n space-separated integers representing the merged sorted array.");
        mergeSortedArrays.setDifficulty(ProblemDifficulty.HARD);
        mergeSortedArrays.setTimeLimitMs(5000);
        mergeSortedArrays.setMemoryLimitMb(256);
        Problem savedMerge = problemRepository.save(mergeSortedArrays);

        // Test cases for Merge Two Sorted Arrays
        TestCase tcMerge1 = new TestCase();
        tcMerge1.setProblemId(savedMerge.getId());
        tcMerge1.setInput("3 3\n1 2 3\n2 5 6");
        tcMerge1.setExpectedOutput("1 2 2 3 5 6");
        tcMerge1.setIsSample(true);
        testCaseRepository.save(tcMerge1);

        TestCase tcMerge2 = new TestCase();
        tcMerge2.setProblemId(savedMerge.getId());
        tcMerge2.setInput("1 0\n1");
        tcMerge2.setExpectedOutput("1");
        tcMerge2.setIsSample(true);
        testCaseRepository.save(tcMerge2);

        TestCase tcMerge3 = new TestCase();
        tcMerge3.setProblemId(savedMerge.getId());
        tcMerge3.setInput("0 1\n\n1");
        tcMerge3.setExpectedOutput("1");
        tcMerge3.setIsSample(false);
        testCaseRepository.save(tcMerge3);

        TestCase tcMerge4 = new TestCase();
        tcMerge4.setProblemId(savedMerge.getId());
        tcMerge4.setInput("4 4\n1 3 5 7\n2 4 6 8");
        tcMerge4.setExpectedOutput("1 2 3 4 5 6 7 8");
        tcMerge4.setIsSample(false);
        testCaseRepository.save(tcMerge4);

        TestCase tcMerge5 = new TestCase();
        tcMerge5.setProblemId(savedMerge.getId());
        tcMerge5.setInput("2 3\n-5 -3\n-4 -2 0");
        tcMerge5.setExpectedOutput("-5 -4 -3 -2 0");
        tcMerge5.setIsSample(false);
        testCaseRepository.save(tcMerge5);

        // Problem 8: Fibonacci Number (EASY)
        Problem fibonacci = new Problem();
        fibonacci.setTitle("Fibonacci Number");
        fibonacci.setDescription(
                "The Fibonacci numbers, commonly denoted F(n) form a sequence, called the Fibonacci sequence, " +
                "such that each number is the sum of the two preceding ones, starting from 0 and 1.\n\n" +
                "F(0) = 0, F(1) = 1\n" +
                "F(n) = F(n - 1) + F(n - 2), for n > 1.\n\n" +
                "Given n, calculate F(n).\n\n" +
                "Input: A single integer n (0 <= n <= 30).\n" +
                "Output: The nth Fibonacci number.");
        fibonacci.setDifficulty(ProblemDifficulty.EASY);
        fibonacci.setTimeLimitMs(5000);
        fibonacci.setMemoryLimitMb(256);
        Problem savedFibonacci = problemRepository.save(fibonacci);

        // Test cases for Fibonacci
        TestCase tcFib1 = new TestCase();
        tcFib1.setProblemId(savedFibonacci.getId());
        tcFib1.setInput("2");
        tcFib1.setExpectedOutput("1");
        tcFib1.setIsSample(true);
        testCaseRepository.save(tcFib1);

        TestCase tcFib2 = new TestCase();
        tcFib2.setProblemId(savedFibonacci.getId());
        tcFib2.setInput("3");
        tcFib2.setExpectedOutput("2");
        tcFib2.setIsSample(true);
        testCaseRepository.save(tcFib2);

        TestCase tcFib3 = new TestCase();
        tcFib3.setProblemId(savedFibonacci.getId());
        tcFib3.setInput("4");
        tcFib3.setExpectedOutput("3");
        tcFib3.setIsSample(false);
        testCaseRepository.save(tcFib3);

        TestCase tcFib4 = new TestCase();
        tcFib4.setProblemId(savedFibonacci.getId());
        tcFib4.setInput("10");
        tcFib4.setExpectedOutput("55");
        tcFib4.setIsSample(false);
        testCaseRepository.save(tcFib4);

        TestCase tcFib5 = new TestCase();
        tcFib5.setProblemId(savedFibonacci.getId());
        tcFib5.setInput("30");
        tcFib5.setExpectedOutput("832040");
        tcFib5.setIsSample(false);
        testCaseRepository.save(tcFib5);

        // Problem 9: Valid Parentheses (MEDIUM)
        Problem validParentheses = new Problem();
        validParentheses.setTitle("Valid Parentheses");
        validParentheses.setDescription(
                "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', " +
                "determine if the input string is valid.\n\n" +
                "An input string is valid if:\n" +
                "1. Open brackets must be closed by the same type of brackets.\n" +
                "2. Open brackets must be closed in the correct order.\n" +
                "3. Every close bracket has a corresponding open bracket of the same type.\n\n" +
                "Input: A single line containing the string s.\n" +
                "Output: Print 'true' if valid, 'false' otherwise.");
        validParentheses.setDifficulty(ProblemDifficulty.MEDIUM);
        validParentheses.setTimeLimitMs(5000);
        validParentheses.setMemoryLimitMb(256);
        Problem savedVP = problemRepository.save(validParentheses);

        // Test cases for Valid Parentheses
        TestCase tcVp1 = new TestCase();
        tcVp1.setProblemId(savedVP.getId());
        tcVp1.setInput("()");
        tcVp1.setExpectedOutput("true");
        tcVp1.setIsSample(true);
        testCaseRepository.save(tcVp1);

        TestCase tcVp2 = new TestCase();
        tcVp2.setProblemId(savedVP.getId());
        tcVp2.setInput("()[]{}");
        tcVp2.setExpectedOutput("true");
        tcVp2.setIsSample(true);
        testCaseRepository.save(tcVp2);

        TestCase tcVp3 = new TestCase();
        tcVp3.setProblemId(savedVP.getId());
        tcVp3.setInput("(]");
        tcVp3.setExpectedOutput("false");
        tcVp3.setIsSample(true);
        testCaseRepository.save(tcVp3);

        TestCase tcVp4 = new TestCase();
        tcVp4.setProblemId(savedVP.getId());
        tcVp4.setInput("([)]");
        tcVp4.setExpectedOutput("false");
        tcVp4.setIsSample(false);
        testCaseRepository.save(tcVp4);

        TestCase tcVp5 = new TestCase();
        tcVp5.setProblemId(savedVP.getId());
        tcVp5.setInput("{[]}");
        tcVp5.setExpectedOutput("true");
        tcVp5.setIsSample(false);
        testCaseRepository.save(tcVp5);

        TestCase tcVp6 = new TestCase();
        tcVp6.setProblemId(savedVP.getId());
        tcVp6.setInput("((()))");
        tcVp6.setExpectedOutput("true");
        tcVp6.setIsSample(false);
        testCaseRepository.save(tcVp6);

        // Problem 10: Binary Search (MEDIUM)
        Problem binarySearch = new Problem();
        binarySearch.setTitle("Binary Search");
        binarySearch.setDescription(
                "Given an array of integers nums which is sorted in ascending order, and an integer target, " +
                "write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.\n\n" +
                "You must write an algorithm with O(log n) runtime complexity.\n\n" +
                "Input: First line contains n (array length).\n" +
                "Second line contains n space-separated integers (sorted array).\n" +
                "Third line contains the target value.\n" +
                "Output: The index of target if found, -1 otherwise.");
        binarySearch.setDifficulty(ProblemDifficulty.MEDIUM);
        binarySearch.setTimeLimitMs(5000);
        binarySearch.setMemoryLimitMb(256);
        Problem savedBS = problemRepository.save(binarySearch);

        // Test cases for Binary Search
        TestCase tcBs1 = new TestCase();
        tcBs1.setProblemId(savedBS.getId());
        tcBs1.setInput("6\n-1 0 3 5 9 12\n9");
        tcBs1.setExpectedOutput("4");
        tcBs1.setIsSample(true);
        testCaseRepository.save(tcBs1);

        TestCase tcBs2 = new TestCase();
        tcBs2.setProblemId(savedBS.getId());
        tcBs2.setInput("6\n-1 0 3 5 9 12\n2");
        tcBs2.setExpectedOutput("-1");
        tcBs2.setIsSample(true);
        testCaseRepository.save(tcBs2);

        TestCase tcBs3 = new TestCase();
        tcBs3.setProblemId(savedBS.getId());
        tcBs3.setInput("1\n5\n5");
        tcBs3.setExpectedOutput("0");
        tcBs3.setIsSample(false);
        testCaseRepository.save(tcBs3);

        TestCase tcBs4 = new TestCase();
        tcBs4.setProblemId(savedBS.getId());
        tcBs4.setInput("5\n1 2 3 4 5\n6");
        tcBs4.setExpectedOutput("-1");
        tcBs4.setIsSample(false);
        testCaseRepository.save(tcBs4);

        TestCase tcBs5 = new TestCase();
        tcBs5.setProblemId(savedBS.getId());
        tcBs5.setInput("7\n-10 -5 0 3 7 11 15\n-5");
        tcBs5.setExpectedOutput("1");
        tcBs5.setIsSample(false);
        testCaseRepository.save(tcBs5);

        log.info("Sample problems initialized successfully. Total problems: {}", problemRepository.count());
    }
}
