/**
 * Patch seed — re-creates test cases for "Longest Common Prefix"
 * Run AFTER the backend redeploys with the @NotNull fix.
 * Usage: node seed-patch.js [backend-url]
 */

const PROBLEM_ID = 'd6afcc3e-2ef6-478d-a634-a121712d8aa2'; // ID from first seed run
const DEFAULT_BACKEND_URL = 'https://codex-code-1.onrender.com';

async function patch() {
    const baseUrl = process.argv[2] || DEFAULT_BACKEND_URL;
    console.log(`Patching test cases at ${baseUrl}...\n`);

    const testCases = [
        { problemId: PROBLEM_ID, input: "3\nflower\nflow\nflight", expectedOutput: "fl",    isSample: true  },
        { problemId: PROBLEM_ID, input: "3\ndog\nracecar\ncar",    expectedOutput: "",      isSample: true  },
        { problemId: PROBLEM_ID, input: "1\nalone",                expectedOutput: "alone", isSample: false },
        { problemId: PROBLEM_ID, input: "4\ninterspecies\ninterstellar\ninterstate\ninternet", expectedOutput: "inters", isSample: false }
    ];

    const res = await fetch(`${baseUrl}/api/test-cases/batch`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testCases)
    });

    if (!res.ok) {
        console.error('Failed:', await res.text());
    } else {
        const created = await res.json();
        console.log(`✓ Created ${created.length} test cases for "Longest Common Prefix"`);
    }
}

patch();
    