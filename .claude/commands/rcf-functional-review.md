---
description: Perform independent functional verification for a range of FBS implementations
argument-hint: <START-FBS-ID> <END-FBS-ID> [--plan-only] (e.g., FBS-001 FBS-010 --plan-only)
---

# Functional Verification: $1 to $2

You are performing **independent functional verification** for Feature Build Specifications **$1 through $2** following the RCF methodology.

**IMPORTANT**: This verification focuses on independently testing that implemented features work correctly. You are NOT running existing test suites - you are manually verifying functionality using Playwright MCP, cURL, and temporary scripts.

## Command Parameters

- **$1**: START-FBS-ID (e.g., FBS-001)
- **$2**: END-FBS-ID (e.g., FBS-010)
- **$3** (optional): `--plan-only` - Generate test plan without executing verification

---

## Step 1: Verify RCF Connection

**Call:** `rcf_status`

Verify that:

- RCF MCP server is connected
- Build Sequence is available
- User Stories and Acceptance Criteria are accessible

If not connected, stop and inform the user to run `rcf_connect` with their repository and branch first.

## Step 2: Extract FBS Range

Parse the FBS IDs from $1 to $2 (e.g., FBS-001 to FBS-010).

**Call:** `rcf_build_sequence_query` with `type: "fbs"` for each FBS ID in the range.

For each FBS, extract:

- FBS ID, title, and summary
- Story scope (User Stories and Acceptance Criteria)
- **Testable outcomes** (critical for verification)
- Dependencies

If any FBS in the range is not found, note it in the final report and continue with available FBS entries.

## Step 2.5: Environment Discovery & Setup

Before testing, establish the testing environment.

### 2.5.1 Discover Base URL

Search for the application's base URL in order of priority:

1. **Check package.json** - Look for `scripts.dev` or `scripts.start` for port numbers
2. **Check .env files** - Look for `API_URL`, `BASE_URL`, `VITE_API_URL`, `PORT`
3. **Check docker-compose.yml** - Look for exposed ports
4. **If not found**, prompt the user:

```
What is the base URL for testing? (e.g., http://localhost:3000)
```

### 2.5.2 Authentication Setup

Prompt the user:

```
Does this application require authentication for API/UI testing? (y/n)
```

If yes:

```
Please provide an authentication token or credentials:
- For Bearer token: "Bearer eyJhbG..."
- For API key: "X-API-Key: abc123"
- For cookie-based: "session=xyz123"
```

Store the authentication method for use in subsequent cURL commands and Playwright sessions.

### 2.5.3 Verify Application Running

Before proceeding:

1. **For API testing**: Execute `curl -s -o /dev/null -w "%{http_code}" {BASE_URL}/health` (or similar endpoint)
2. **For UI testing**: `mcp__playwright__browser_navigate` to BASE_URL

If unreachable:

```
The application at {BASE_URL} is not responding.

Please ensure the application is running:
- Check: npm run dev / pnpm dev / docker compose up
- Verify the correct port is exposed
- Check for any startup errors in the console

Once running, confirm to continue.
```

---

## Step 3: Build Functional Test Plan

Use RCF MCP tools to extract comprehensive test scenarios from the acceptance criteria.

### 3.1 Fetch User Stories and Acceptance Criteria

For each FBS in the range:

**Call:** `rcf_query` with `type: "stories-for-fbs"` and `target: "<FBS-ID>"`

This returns the full list of User Stories with their Acceptance Criteria.

### 3.2 Get FBS Context (Optional - for complex verification)

**Call:** `rcf_fbs_context` with `fbsId: "<FBS-ID>"`

This provides:

- TAD architecture context
- Component information
- Technical patterns

Use this for complex scenarios requiring understanding of the system architecture.

### 3.3 Derive Test Scenarios from Acceptance Criteria

For each Acceptance Criterion, analyze the description to extract:

| Element              | How to Extract                                 |
| -------------------- | ---------------------------------------------- |
| **Inputs**           | What data, state, or preconditions are needed? |
| **Actions**          | What user or system actions are described?     |
| **Expected Outputs** | What should happen? What state should change?  |

### 3.4 Categorize by Verification Method

Based on the AC content, determine the verification method:

| AC Contains                                             | Verification Method                   |
| ------------------------------------------------------- | ------------------------------------- |
| UI elements (button, form, page, modal, click, display) | **Playwright MCP**                    |
| API endpoints (POST, GET, endpoint, response, request)  | **cURL**                              |
| Data transformation, business logic, multi-step flows   | **Temporary Node.js script**          |
| External services, third-party APIs                     | **Mark as "Cannot Verify" with note** |

### 3.5 Build Test Plan Structure

Create an in-memory test plan:

```markdown
## Test Plan: FBS-XXX - [Title]

### US-XXX: [User Story Title]

#### AC-XXX: [AC Description]

- **Verification Method**: [Playwright MCP | cURL | Script]
- **Preconditions**: [Required state/data]
- **Test Steps**:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
- **Expected Result**: [What success looks like]
- **FBS Testable Outcome**: [Link to relevant testable outcome]
```

---

## Step 3.5: Plan-Only Mode Check

**If `--plan-only` was specified:**

1. Save the test plan to `docs/review/functional/$1_$2-test-plan.md`
2. Display the test plan summary to the user
3. **STOP HERE** - Do not execute verification steps

```
Test plan generated and saved to: docs/review/functional/$1_$2-test-plan.md

Review the plan and run without --plan-only to execute verification.
```

---

## Step 4: Execute Independent Verification

For each AC in the test plan, perform verification using the appropriate method.

### 4.1 UI Verification (Playwright MCP)

For acceptance criteria involving user interface interactions:

#### Workflow:

```
1. Navigate to the relevant page
   Call: mcp__playwright__browser_navigate({ url: "{BASE_URL}/path" })

2. Capture initial state
   Call: mcp__playwright__browser_snapshot()
   - Review the accessibility tree to identify elements
   - Note element refs for interaction

3. Perform AC actions
   For clicks:
     Call: mcp__playwright__browser_click({ element: "description", ref: "element-ref" })

   For form input:
     Call: mcp__playwright__browser_type({ element: "description", ref: "element-ref", text: "value" })

   For complex forms:
     Call: mcp__playwright__browser_fill_form({ fields: [...] })

   For waiting:
     Call: mcp__playwright__browser_wait_for({ text: "expected text" })

4. Verify expected state
   Call: mcp__playwright__browser_snapshot()
   - Compare current state to expected AC outcome
   - Check for expected text, elements, or state changes

5. Capture evidence (optional)
   Call: mcp__playwright__browser_take_screenshot({ filename: "AC-XXX-result.png" })

6. Record result
   - PASS: Observed behavior matches AC expectation
   - FAIL: Observed behavior differs (document difference)
   - BLOCKED: Could not complete test (document reason)
```

#### Authentication for UI:

If authentication is required:

```
1. Navigate to login page
2. Fill credentials using mcp__playwright__browser_fill_form
3. Click login button
4. Verify authentication succeeded
5. Continue with AC verification
```

### 4.2 API Verification (cURL)

For acceptance criteria involving API endpoints:

#### Workflow:

```
1. Construct the cURL command from AC requirements

   GET request:
   curl -s -X GET "{BASE_URL}/api/endpoint" \
     -H "Content-Type: application/json" \
     -H "Authorization: {AUTH_TOKEN}"

   POST request:
   curl -s -X POST "{BASE_URL}/api/endpoint" \
     -H "Content-Type: application/json" \
     -H "Authorization: {AUTH_TOKEN}" \
     -d '{"key": "value"}'

2. Execute via Bash tool
   - Capture full response including status code
   - Use: curl -s -w "\n%{http_code}" to get status

3. Parse and verify response
   - Check HTTP status code matches expectation
   - Parse JSON response body
   - Verify required fields/values present
   - Compare to AC expected behavior

4. Record result with evidence
   - Include: command executed, response body, status code
   - PASS/FAIL determination with explanation
```

#### Common API Test Patterns:

```bash
# Health check
curl -s -o /dev/null -w "%{http_code}" {BASE_URL}/health

# GET with auth
curl -s -X GET "{BASE_URL}/api/resource" -H "Authorization: Bearer {TOKEN}"

# POST with JSON body
curl -s -X POST "{BASE_URL}/api/resource" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{"name": "test", "value": 123}'

# Check specific response field (with jq if available)
curl -s {BASE_URL}/api/resource | jq '.data.id'
```

### 4.3 Complex Verification (Temporary Scripts)

For acceptance criteria requiring multi-step flows, data setup, or complex assertions:

#### Workflow:

```
1. Design the verification script
   - Setup: Prepare required data/state
   - Action: Execute the behavior being tested
   - Assert: Verify the expected outcome
   - Cleanup: Remove test data if needed

2. Create and execute temporary Node.js script

   Option A - Inline execution:
   node -e "
     const http = require('http');
     // ... verification logic
     console.log(result ? 'PASS' : 'FAIL');
   "

   Option B - Temporary file (for complex scripts):
   Write to: /tmp/verify-ac-xxx.mjs
   Execute: node /tmp/verify-ac-xxx.mjs
   Delete after execution

3. Parse script output
   - Capture stdout for results
   - Check exit code (0 = pass, non-zero = fail)

4. Record result with script and output as evidence
```

#### Example Complex Verification Script:

```javascript
// /tmp/verify-ac-xxx.mjs
const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

async function verify() {
  // Setup: Create test data
  const setupRes = await fetch(`${BASE_URL}/api/items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: 'test-item' }),
  });
  const item = await setupRes.json();

  // Action: Perform the operation being tested
  const actionRes = await fetch(`${BASE_URL}/api/items/${item.id}/process`, {
    method: 'POST',
  });

  // Assert: Check expected outcome
  const result = await actionRes.json();
  const passed = result.status === 'processed' && result.processedAt !== null;

  // Cleanup
  await fetch(`${BASE_URL}/api/items/${item.id}`, { method: 'DELETE' });

  // Report
  console.log(passed ? 'PASS: Item processed correctly' : 'FAIL: Processing did not complete');
  process.exit(passed ? 0 : 1);
}

verify().catch((err) => {
  console.log('FAIL: ' + err.message);
  process.exit(1);
});
```

---

## Step 4.5: Regression Testing (Earlier FBSs)

**Purpose**: Verify that new code hasn't broken existing functionality from earlier FBSs.

### 4.5.1 Identify Regression Test Candidates

**Call:** `rcf_build_sequence_query` with `type: "by-status"` and `target: "verified"`

From the results, filter FBSs that come BEFORE $1 in the sequence. These are candidates for regression testing.

### 4.5.2 Select Critical Paths

For each earlier FBS, identify 1-2 **critical testable outcomes** to verify:

- Prefer outcomes that touch shared components
- Prefer authentication, data persistence, and core workflows
- Skip UI-only outcomes if time is limited

### 4.5.3 Execute Regression Tests

For each selected testable outcome:

1. Use the same verification methods (Playwright MCP, cURL, scripts)
2. Test the **happy path only** (not edge cases)
3. Record results with **Failure Type: Regression** if they fail

### 4.5.4 Regression Test Scope Guidelines

| FBS Range Being Reviewed | Recommended Regression Scope             |
| ------------------------ | ---------------------------------------- |
| FBS-001 to FBS-003       | None (first FBSs)                        |
| FBS-004 to FBS-006       | 2-3 outcomes from FBS-001 to FBS-003     |
| FBS-007 to FBS-010       | 3-5 outcomes from FBS-001 to FBS-006     |
| FBS-011+                 | 5-8 outcomes covering all major features |

**Note**: Regression testing is a **smoke test**, not exhaustive. The goal is to catch obvious breakages quickly.

---

## Step 5: Compile Verification Results

After executing all verifications, compile results into categories:

### Result Categories

| Status      | Meaning                                           |
| ----------- | ------------------------------------------------- |
| **PASS**    | AC behavior verified - works as specified         |
| **FAIL**    | AC behavior differs from specification            |
| **PARTIAL** | Some aspects pass, others fail                    |
| **BLOCKED** | Cannot verify (dependency unavailable, env issue) |
| **SKIPPED** | Requires external service or manual verification  |

### Failure Classification (CRITICAL for PR Decision)

**All failures MUST be classified into one of two categories:**

| Failure Type             | Definition                                                                | PR Impact      |
| ------------------------ | ------------------------------------------------------------------------- | -------------- |
| **Current FBS Failures** | Failures in ACs that belong to the FBS range being reviewed ($1-$2)       | **PR BLOCKED** |
| **Regression Failures**  | Failures in ACs from FBSs OUTSIDE the reviewed range (previously passing) | **PR BLOCKED** |

**IMPORTANT**: Both failure types block PR approval. The distinction helps developers prioritize fixes:

- **Current FBS Failures** = New implementation is incomplete or broken
- **Regression Failures** = New code broke existing functionality (more severe)

### How to Identify Regression Failures

When verifying the FBS range $1 to $2, also run a **quick smoke test** of critical paths from earlier FBSs:

1. Identify FBSs with `status: "verified"` that come BEFORE $1 in the Build Sequence
2. For each, test 1-2 critical testable outcomes (happy path only)
3. Any failure in these is a **Regression Failure**

Example: If reviewing FBS-005 to FBS-008:

- FBS-001 through FBS-004 are candidates for regression testing
- Test their core functionality to ensure nothing broke

### For Each AC, Record:

```markdown
#### AC-XXX: [Description]

**Status**: [PASS | FAIL | PARTIAL | BLOCKED | SKIPPED]
**Verification Method**: [Playwright MCP | cURL | Script]
**FBS Testable Outcome**: [Which outcome this verifies]

**Evidence**:

- [Screenshot path / cURL command+response / Script output]

**Notes**:

- [Any observations, differences from expected, or issues encountered]
```

---

## Step 6: Generate Verification Report

### 6.1 Detailed Results Section

For each FBS, compile all AC verification results:

```markdown
## FBS-XXX: [Title]

### Summary

- Total ACs: X
- PASS: X
- FAIL: X (Current FBS: Y, Regression: Z)
- PARTIAL: X
- BLOCKED: X
- SKIPPED: X

### US-XXX: [User Story Title]

#### AC-XXX: [AC Description]

**Status**: PASS/FAIL/PARTIAL/BLOCKED/SKIPPED
**Failure Type**: [Current FBS | Regression | N/A] _(only for FAIL/PARTIAL)_
**Method**: Playwright MCP / cURL / Script
**Testable Outcome**: [FBS outcome verified]

**Evidence**:
[Include relevant evidence]

**Details**:

- Expected: [What AC specifies]
- Actual: [What was observed]
- Difference: [If FAIL/PARTIAL, explain gap]

**Recommendation**: [If FAIL, what needs to be fixed]
```

**Failure Type Classification:**

- **Current FBS**: This AC belongs to an FBS within the reviewed range ($1-$2)
- **Regression**: This AC belongs to an FBS BEFORE the reviewed range (was previously passing)

### 6.2 Summary Section (PR Review Format)

Generate a concise summary suitable for PR comments:

```markdown
## Functional Verification Summary: $1 to $2

**Scope**: [X] FBS entries, [Y] User Stories, [Z] Acceptance Criteria
**Date**: [Current Date]
**Branch**: [Current Git Branch]

### PR VERDICT: [APPROVED | BLOCKED]

> **BLOCKED** if ANY failures exist (Current FBS OR Regression)
> **APPROVED** only if all tests PASS (excluding SKIPPED/BLOCKED items)

### Overall Results

| Status  | Count | Percentage |
| ------- | ----- | ---------- |
| PASS    | X     | XX%        |
| FAIL    | X     | XX%        |
| PARTIAL | X     | XX%        |
| BLOCKED | X     | XX%        |
| SKIPPED | X     | XX%        |

### Verification Score: XX%

*Calculation: (PASS + 0.5*PARTIAL) / (Total - SKIPPED - BLOCKED) _ 100_

---

### 🔴 Current FBS Failures (New Implementation Issues)

Failures in acceptance criteria within the reviewed range ($1-$2).
**These indicate incomplete or broken new functionality.**

| FBS     | AC     | Description         | Expected vs Actual |
| ------- | ------ | ------------------- | ------------------ |
| FBS-XXX | AC-XXX | [Brief description] | [What went wrong]  |

**Total Current FBS Failures: X**

---

### 🟠 Regression Failures (Broken Existing Functionality)

Failures in acceptance criteria from FBSs BEFORE $1 that previously passed.
**These indicate the new code broke existing features - HIGH PRIORITY.**

| FBS     | AC     | Description         | Expected vs Actual |
| ------- | ------ | ------------------- | ------------------ |
| FBS-XXX | AC-XXX | [Brief description] | [What went wrong]  |

**Total Regression Failures: X**

---

### Partial Issues

[List PARTIAL results with specific gaps]

### Blocked/Skipped Items

[List items that couldn't be verified and why]

### Recommendations

**Priority 1 - Regression Fixes (MUST fix before merge):**

1. [Regression fix 1]
2. [Regression fix 2]

**Priority 2 - Current FBS Fixes (MUST fix before merge):**

1. [Current FBS fix 1]
2. [Current FBS fix 2]

**Priority 3 - Improvements (Can address post-merge):**

1. [Optional improvement]
```

---

## Step 7: Save Verification Reports

### 7.1 Create Directory Structure

**Command:** `mkdir -p docs/review/functional`

### 7.2 Save Reports

Generate standardized filenames based on FBS range:

| Report                     | Filename                                               |
| -------------------------- | ------------------------------------------------------ |
| Detailed Results           | `docs/review/functional/$1_$2-verification-results.md` |
| PR Summary                 | `docs/review/functional/$1_$2-pr-summary.md`           |
| Test Plan (if --plan-only) | `docs/review/functional/$1_$2-test-plan.md`            |

### 7.3 Confirm Saved Reports

```
Functional verification reports saved:
  - Detailed: docs/review/functional/$1_$2-verification-results.md
  - Summary: docs/review/functional/$1_$2-pr-summary.md

PR Summary displayed above for immediate review.
```

---

## Output

**Two markdown reports will be saved:**

1. **Detailed Results** (`docs/review/functional/$1_$2-verification-results.md`)
   - Full verification results by FBS/US/AC
   - Evidence (commands, responses, screenshots)
   - Specific failure details and recommendations

2. **PR Summary** (`docs/review/functional/$1_$2-pr-summary.md`)
   - Concise markdown for GitHub PR comment
   - Verification score and high-level metrics
   - Critical failures and recommendations

**Additionally**, display the PR Summary in the console for immediate review.

---

**Remember**: This is INDEPENDENT VERIFICATION. You are testing actual functionality, not running existing tests. Use the tools (Playwright MCP, cURL, scripts) to verify that the implementation matches the acceptance criteria.
