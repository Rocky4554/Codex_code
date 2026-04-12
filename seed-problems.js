/**
 * Seed script to add problems and test cases to Codex backend
 * Usage: node seed-problems.js <backend-url> <jwt-token>
 * Example: node seed-problems.js https://your-backend.onrender.com your-jwt-token
 */

const problems = [
    {
        title: "Reverse String",
        description: "Write a function that reverses a string. The input string is given as an array of characters.\n\nYou must do this by modifying the input array in-place with O(1) extra memory.\n\nInput: A single line containing the string to reverse.\nOutput: The reversed string.",
        difficulty: "MEDIUM",
        timeLimitMs: 5000,
        memoryLimitMb: 256,
        testCases: [
            { input: "hello", expectedOutput: "olleh", isSample: true },
            { input: "Hannah", expectedOutput: "hannaH", isSample: false },
            { input: "A man a plan a canal Panama", expectedOutput: "amanaP lanac a nalp a nam A", isSample: false },
            { input: "1234567890", expectedOutput: "0987654321", isSample: false }
        ]
    },
    {
        title: "Palindrome Number",
        description: "Given an integer x, return true if x is a palindrome, and false otherwise.\n\nAn integer is a palindrome when it reads the same forward and backward.\n\nInput: A single integer x.\nOutput: Print 'true' if x is a palindrome, 'false' otherwise.",
        difficulty: "MEDIUM",
        timeLimitMs: 5000,
        memoryLimitMb: 256,
        testCases: [
            { input: "121", expectedOutput: "true", isSample: true },
            { input: "-121", expectedOutput: "false", isSample: true },
            { input: "12321", expectedOutput: "true", isSample: false },
            { input: "123456", expectedOutput: "false", isSample: false },
            { input: "0", expectedOutput: "true", isSample: false }
        ]
    },
    {
        title: "Factorial",
        description: "Write a function to calculate the factorial of a given non-negative integer n.\n\nThe factorial of n is the product of all positive integers less than or equal to n.\n\nInput: A single integer n (0 <= n <= 20).\nOutput: The factorial of n.",
        difficulty: "EASY",
        timeLimitMs: 5000,
        memoryLimitMb: 256,
        testCases: [
            { input: "5", expectedOutput: "120", isSample: true },
            { input: "0", expectedOutput: "1", isSample: true },
            { input: "10", expectedOutput: "3628800", isSample: false },
            { input: "20", expectedOutput: "2432902008176640000", isSample: false }
        ]
    },
    {
        title: "Longest Common Prefix",
        description: "Write a function to find the longest common prefix string amongst an array of strings.\n\nIf there is no common prefix, return an empty string.\n\nInput: First line contains n (number of strings), followed by n lines of strings.\nOutput: The longest common prefix.",
        difficulty: "MEDIUM",
        timeLimitMs: 5000,
        memoryLimitMb: 256,
        testCases: [
            { input: "3\nflower\nflow\nflight", expectedOutput: "fl", isSample: true },
            { input: "3\ndog\nracecar\ncar", expectedOutput: "", isSample: true },
            { input: "1\nalone", expectedOutput: "alone", isSample: false },
            { input: "4\ninterspecies\ninterstellar\ninterstate\ninternet", expectedOutput: "inters", isSample: false }
        ]
    },
    {
        title: "Merge Two Sorted Arrays",
        description: "You are given two integer arrays nums1 and nums2, sorted in non-decreasing order, and two integers m and n, representing the number of elements in nums1 and nums2 respectively.\n\nMerge nums1 and nums2 into a single array sorted in non-decreasing order.\n\nThe final sorted array should not be returned by the function, but instead be stored inside nums1. To accommodate this, nums1 has a length of m + n, where the first m elements denote the elements that should be merged, and the last n elements are set to 0 and should be ignored. nums2 has a length of n.\n\nInput: First line contains m and n.\nSecond line contains m integers (nums1).\nThird line contains n integers (nums2).\nOutput: m+n space-separated integers representing the merged sorted array.",
        difficulty: "HARD",
        timeLimitMs: 5000,
        memoryLimitMb: 256,
        testCases: [
            { input: "3 3\n1 2 3\n2 5 6", expectedOutput: "1 2 2 3 5 6", isSample: true },
            { input: "1 0\n1", expectedOutput: "1", isSample: true },
            { input: "0 1\n\n1", expectedOutput: "1", isSample: false },
            { input: "4 4\n1 3 5 7\n2 4 6 8", expectedOutput: "1 2 3 4 5 6 7 8", isSample: false },
            { input: "2 3\n-5 -3\n-4 -2 0", expectedOutput: "-5 -4 -3 -2 0", isSample: false }
        ]
    },
    {
        title: "Fibonacci Number",
        description: "The Fibonacci numbers, commonly denoted F(n) form a sequence, called the Fibonacci sequence, such that each number is the sum of the two preceding ones, starting from 0 and 1.\n\nF(0) = 0, F(1) = 1\nF(n) = F(n - 1) + F(n - 2), for n > 1.\n\nGiven n, calculate F(n).\n\nInput: A single integer n (0 <= n <= 30).\nOutput: The nth Fibonacci number.",
        difficulty: "EASY",
        timeLimitMs: 5000,
        memoryLimitMb: 256,
        testCases: [
            { input: "2", expectedOutput: "1", isSample: true },
            { input: "3", expectedOutput: "2", isSample: true },
            { input: "4", expectedOutput: "3", isSample: false },
            { input: "10", expectedOutput: "55", isSample: false },
            { input: "30", expectedOutput: "832040", isSample: false }
        ]
    },
    {
        title: "Valid Parentheses",
        description: "Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.\n\nInput: A single line containing the string s.\nOutput: Print 'true' if valid, 'false' otherwise.",
        difficulty: "MEDIUM",
        timeLimitMs: 5000,
        memoryLimitMb: 256,
        testCases: [
            { input: "()", expectedOutput: "true", isSample: true },
            { input: "()[]{}", expectedOutput: "true", isSample: true },
            { input: "(]", expectedOutput: "false", isSample: true },
            { input: "([)]", expectedOutput: "false", isSample: false },
            { input: "{[]}", expectedOutput: "true", isSample: false },
            { input: "((()))", expectedOutput: "true", isSample: false }
        ]
    },
    {
        title: "Binary Search",
        description: "Given an array of integers nums which is sorted in ascending order, and an integer target, write a function to search target in nums. If target exists, then return its index. Otherwise, return -1.\n\nYou must write an algorithm with O(log n) runtime complexity.\n\nInput: First line contains n (array length).\nSecond line contains n space-separated integers (sorted array).\nThird line contains the target value.\nOutput: The index of target if found, -1 otherwise.",
        difficulty: "MEDIUM",
        timeLimitMs: 5000,
        memoryLimitMb: 256,
        testCases: [
            { input: "6\n-1 0 3 5 9 12\n9", expectedOutput: "4", isSample: true },
            { input: "6\n-1 0 3 5 9 12\n2", expectedOutput: "-1", isSample: true },
            { input: "1\n5\n5", expectedOutput: "0", isSample: false },
            { input: "5\n1 2 3 4 5\n6", expectedOutput: "-1", isSample: false },
            { input: "7\n-10 -5 0 3 7 11 15\n-5", expectedOutput: "1", isSample: false }
        ]
    }
];

async function seedProblems() {
    const baseUrl = process.argv[2] || 'http://localhost:8080';
    const jwtToken = process.argv[3];
    
    console.log(`Seeding problems to ${baseUrl}...\n`);
    
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (jwtToken) {
        headers['Authorization'] = `Bearer ${jwtToken}`;
    }
    
    for (const problem of problems) {
        try {
            // Create problem
            const problemRes = await fetch(`${baseUrl}/api/problems`, {
                method: 'POST',
                headers,
                body: JSON.stringify({
                    title: problem.title,
                    description: problem.description,
                    difficulty: problem.difficulty,
                    timeLimitMs: problem.timeLimitMs,
                    memoryLimitMb: problem.memoryLimitMb
                })
            });
            
            if (!problemRes.ok) {
                const error = await problemRes.text();
                console.error(`Failed to create "${problem.title}": ${error}`);
                continue;
            }
            
            const createdProblem = await problemRes.json();
            console.log(`✓ Created problem: "${problem.title}" (ID: ${createdProblem.id})`);
            
            // Create test cases
            const testCaseRequests = problem.testCases.map(tc => ({
                problemId: createdProblem.id,
                input: tc.input,
                expectedOutput: tc.expectedOutput,
                isSample: tc.isSample
            }));
            
            const tcRes = await fetch(`${baseUrl}/api/test-cases/batch`, {
                method: 'POST',
                headers,
                body: JSON.stringify(testCaseRequests)
            });
            
            if (!tcRes.ok) {
                const error = await tcRes.text();
                console.error(`  Failed to create test cases: ${error}`);
            } else {
                const createdTCs = await tcRes.json();
                console.log(`  ✓ Created ${createdTCs.length} test cases`);
            }
        } catch (error) {
            console.error(`Error creating "${problem.title}":`, error.message);
        }
    }
    
    console.log('\n✓ Seeding complete!');
}

seedProblems();
