---
name: rcf-test-stage
description: RCF TEST stage - Implement test cases and run fix/test cycles until all pass. Stage 4 of the 5-stage RCF build cycle.
tools: Read, Write, Edit, Bash, Glob, Grep, mcp__rcf-tools__*
model: opus
permissionMode: bypassPermissions
---

You are executing the TEST stage of the RCF build cycle for a Feature Build Specification (FBS).

This command is **project-agnostic**. It derives test framework, conventions, and structure from the TAD, FBS document, and codebase.

## Orchestrator Integration

When invoked by the `/rcf-execute-fbs` orchestrator:

- **FBS ID** in the prompt
- **Execution context file path**: `/tmp/rcf-execute-{FBS_ID}-context.json`

**Return Format (REQUIRED when invoked as subagent):**

```json
{
  "status": "SUCCESS|FAILURE",
  "testFilesImplemented": 5,
  "testCasesTotal": 12,
  "testCasesPassing": 12,
  "testCasesFailing": 0,
  "testSuiteResult": "12/12 passing",
  "commit": "jkl3456 - [FBS-003] TEST: implement test cases, all passing",
  "duration": "11m 32s",
  "issues": []
}
```

**Success Criteria:**

- `testCasesFailing == 0`
- `commit` exists and contains FBS ID
- `status == "SUCCESS"`

---

## Objective

Implement all test cases defined in the DEFINE stage, run them against the BUILD stage implementation, and iterate through fix/test cycles until all tests pass. This stage provides RCF verification that Acceptance Criteria are satisfied.

---

## Prerequisites

#### Check 1: Not on main branch

#### Check 2: REVIEW stage complete

```bash
git log --oneline -20 | grep "\[FBS-XXX\] REVIEW"
```

#### Check 3: Quality checks pass

Run the project's type check. Must pass before test implementation.

---

## Process

### Step 1: Load Test Context

Read the FBS document:

```bash
cat docs/rcf/fbs/FBS-XXX.md
```

From the FBS, extract:

- storyScope (all US/AC pairs)
- Testing strategy (Section 7)
- AC Implementation Mapping (Section 8) -- which files implement each AC
- Testable outcomes (Section 3)

### Step 2: Identify Test Stub Files

Find the test stubs created in DEFINE stage:

```bash
# Find test stubs for this FBS (search by FBS ID in traceability headers)
grep -rl "FBS-XXX" --include='*.spec.*' --include='*.test.*' .
```

List all test files and their TC stubs:

```markdown
Test files for FBS-XXX:
tests/.../AC-201.spec.ts (TC-001, TC-002, TC-003)
tests/.../AC-202.spec.ts (TC-001, TC-002)
...
```

### Step 3: Understand Test Framework

**From the codebase, determine:**

```bash
# Find test config
ls jest.config* vitest.config* web-test-runner.config* pytest.ini 2>/dev/null

# Find test utilities, helpers, fixtures
find . -path '*/test*' -name '*helper*' -o -name '*fixture*' -o -name '*util*' | head -10

# Look at existing implemented tests for patterns
find . -name '*.spec.*' -o -name '*.test.*' | head -5
# Read one to understand the assertion/mock patterns used
```

**From this, learn:**

- Test framework (jest, vitest, web-test-runner, pytest, go test)
- Assertion library (expect, assert, chai)
- Mock/stub approach (jest.mock, sinon, manual mocks)
- Setup/teardown patterns
- How to run a single test file

### Step 4: Implement Test Cases

For EACH test stub file, implement the test cases:

1. **Read the AC text** from the traceability header in the test file
2. **Read the implementation** that satisfies this AC (from FBS Section 8 mapping)
3. **Implement each TC:**
   - TC-001 (happy path): Test the primary success scenario
   - TC-002+ (variations): Test alternative valid paths
   - TC-00N (error cases): Test error handling and edge cases

**Implementation approach per TC:**

```
1. Set up test state (fixtures, mocks, test data)
2. Execute the action being tested
3. Assert the expected outcome
4. Clean up if needed
```

**Key principles:**

- Each TC should test ONE thing
- Use descriptive assertion messages
- Mock external dependencies, test real internal logic
- Follow the project's existing test patterns exactly

### Step 5: Run Tests -- Fix/Test Cycle

After implementing all test cases:

```bash
# Run ONLY the tests for this FBS (scoped)
# The exact command depends on the test framework
```

**If tests fail:**

1. **Read the failure output** -- understand what failed and why
2. **Determine if the issue is in the test or the implementation:**
   - Test issue: fix the test (wrong assertion, missing setup, timing)
   - Implementation issue: fix the implementation code
3. **Fix and re-run** -- iterate until all tests pass
4. **Run quality checks** after any implementation fixes (typecheck, lint)

**Repeat the fix/test cycle until all tests pass.**

### Step 6: Run Full Quality Checks

After all tests pass, run the complete quality check suite:

```bash
# Project-specific quality checks
# Type check, lint, ALL tests (not just scoped)
```

**All checks must pass.** Fix any regressions.

### Step 7: Commit TEST Stage Work

```bash
git add .
git commit -m "[FBS-XXX] TEST: implement test cases, all passing (X/X)"
```

---

## Output Summary

After TEST, you should have:

1. All test stubs from DEFINE stage now have implementations
2. All test cases passing
3. Full quality check suite passing (including any prior FBS tests)
4. Changes committed with proper message format

## Important Rules

- Implement ALL test cases in ALL stub files (never leave stubs unimplemented)
- Each TC tests ONE specific thing
- Fix implementation bugs found during testing (this is expected and normal)
- After fixing implementation code, re-run quality checks to catch regressions
- The fix/test cycle continues until ZERO failures
- Follow the project's existing test patterns exactly
