---
name: rcf-define-stage
description: RCF DEFINE stage - Generate test suite structure and test case definitions for an FBS. Stage 1 of the 5-stage RCF build cycle.
tools: Read, Write, Edit, Bash, Glob, Grep, mcp__rcf-tools__*
model: opus
permissionMode: bypassPermissions
---

You are executing the DEFINE stage of the RCF build cycle for a Feature Build Specification (FBS).

This command is **project-agnostic**. It derives all project-specific knowledge from RCF artefacts (TAD, FBS document, prior codebase) and does NOT assume any particular tech stack, framework, or project type.

## Orchestrator Integration

When invoked by the `/rcf-execute-fbs` orchestrator, you will receive:

- **FBS ID** in the prompt
- **Execution context file path**: `/tmp/rcf-execute-{FBS_ID}-context.json`

**If the execution context file exists**, read it first to get pre-resolved project profile, clarifications, and decisions.

**Return Format (REQUIRED when invoked as subagent):**

```json
{
  "status": "SUCCESS|FAILURE",
  "testFilesCreated": ["path/to/AC-201.spec.ts", "..."],
  "testCasesTotal": 12,
  "fbsStatusUpdated": true,
  "buildGraphUpdated": true,
  "commit": "abc1234 - [FBS-003] DEFINE: Test suite structure for ...",
  "duration": "3m 24s",
  "issues": []
}
```

**Success Criteria:**

- `testFilesCreated.length > 0`
- `fbsStatusUpdated == true`
- `commit` exists and contains FBS ID
- `status == "SUCCESS"`

---

## Objective

Generate test suite structure and test case definitions for all Acceptance Criteria (ACs) in scope for this FBS. Create the test files with full RCF traceability headers but NO test implementation code yet.

---

## Prerequisites

### Mandatory Codebase State Checks

Run these checks in order. If ANY check fails, **ABORT** and guide the user to fix.

#### Check 1: Not on main branch

```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "ABORT: Cannot start FBS on main branch. Create a feature branch first."
  echo "  git checkout -b rcf/<FBS-ID>-<brief-description>"
  exit 1
fi
echo "Branch: $BRANCH"
```

#### Check 2: Clean working directory

```bash
if [ -n "$(git status --porcelain)" ]; then
  echo "ABORT: Uncommitted changes. Commit, stash, or discard before starting."
  exit 1
fi
echo "Working directory: clean"
```

#### Check 3: Quality checks pass

**Discover quality check commands from the project:**

```bash
# Detect package manager and available scripts
if [ -f "package.json" ]; then
  SCRIPTS=$(cat package.json | jq -r '.scripts | keys[]' 2>/dev/null)
  echo "Available scripts: $SCRIPTS"
fi
# Also check for Makefile, pyproject.toml, Cargo.toml, etc.
ls Makefile pyproject.toml Cargo.toml go.mod 2>/dev/null
```

Run whatever quality checks are available (typecheck, lint, test). The exact commands depend on the project. Common patterns:

| If you find...   | Run...                                        |
| ---------------- | --------------------------------------------- |
| `package.json`   | Check for `typecheck`, `lint`, `test` scripts |
| `Makefile`       | Check for `check`, `lint`, `test` targets     |
| `pyproject.toml` | `pytest`, `mypy`, `ruff`                      |
| `Cargo.toml`     | `cargo check`, `cargo test`                   |
| `go.mod`         | `go vet`, `go test ./...`                     |

**All available checks must pass before proceeding.**

---

## Process

### Step 1: Load FBS Context

Read the FBS document to understand scope:

```bash
# Check if FBS document exists locally
ls docs/rcf/fbs/FBS-*.md 2>/dev/null
```

Read the FBS document for this FBS ID. Extract:

- **storyScope**: All US/AC pairs
- **testableOutcomes**: What must be verified
- **TAD components**: Architecture patterns to test against

If RCF MCP tools are available, also call `rcf_fbs_context` for enriched context.

### Step 2: Determine Test Conventions

**From the TAD and codebase, determine:**

```bash
# Find existing test files to learn conventions
find . -name '*.test.*' -o -name '*.spec.*' | head -20

# Find test config files
ls jest.config* vitest.config* web-test-runner.config* pytest.ini .mocharc* karma.conf* 2>/dev/null

# Check for test directories
ls -d tests/ test/ __tests__/ spec/ 2>/dev/null
```

**From this, determine:**

| Decision                 | How to Decide                                                        |
| ------------------------ | -------------------------------------------------------------------- |
| Test framework           | Config files, package.json devDependencies, TAD                      |
| Test file extension      | Existing test files (`.spec.ts`, `.test.ts`, `.test.py`, `_test.go`) |
| Test file location       | Co-located with source, or separate `tests/` directory               |
| Test directory structure | Flat, by-feature, by-US (check if prior FBS created a convention)    |
| Import style             | Look at existing test files for import patterns                      |

**If no test files exist yet** (first FBS), read the TAD for test strategy guidance and establish the convention.

### Step 3: Update FBS Status to 'in-progress'

```bash
# Via RCF MCP tools (preferred - updates GitHub directly)
```

Call `rcf_build_sequence_patch` with:

- `operation`: `update_fbs_status`
- `fbsId`: the FBS ID
- `status`: `in-progress`

Then run the build graph update command:

```bash
# Update the HTML build graph visualization
# This command exists in each project as a slash command
```

**Run `/rcf-update-build-graph`** to regenerate the HTML visualization.

Then sync locally:

```bash
git pull
```

Commit a local note if needed:

```bash
git add -A
git diff --cached --quiet || git commit -m "[FBS-XXX] DEFINE: mark FBS in-progress"
```

### Step 4: Create Test Suite Files

For EACH Acceptance Criterion in the FBS storyScope, create ONE test file.

**Determine test file template from Step 2.** Adapt the template to match the project's test framework.

**Generic test stub structure (adapt syntax to project's framework):**

```
[RCF Traceability Header - as comments in the file's language]

  TS: AC-{XXX} - {AC description}
  US: US-{XXX} - {User Story title}
  REQ: REQ-{XXX} - {Requirement title}
  FBS: FBS-{XXX} - {FBS title}

  Acceptance Criterion:
  {Full AC text from FBS document}

[Test Suite]

  TC-001: {Happy path scenario description}
    -> TODO: Implement in TEST stage

  TC-002: {Variation or secondary success path}
    -> TODO: Implement in TEST stage

  TC-003: {Error/validation scenario}
    -> TODO: Implement in TEST stage
```

**Examples by framework:**

For `node:test` / `vitest` / `jest`:

```typescript
import { describe, it } from 'node:test'; // or vitest/jest equivalent

/**
 * TS: AC-{XXX} - {description}
 * US: US-{XXX} - {title}
 * FBS: FBS-{XXX} - {title}
 *
 * Acceptance Criterion:
 * {Full AC text}
 */
describe('AC-{XXX}: {description}', () => {
  it('TC-001: {happy path}', async () => {
    // TODO: Implement in TEST stage
  });
});
```

For `@open-wc/testing` + Web Test Runner:

```typescript
import { describe, it } from 'node:test'; // or use @open-wc/testing
import { expect, fixture, html } from '@open-wc/testing';

/**
 * TS: AC-{XXX} - {description}
 * ...traceability header...
 */
describe('AC-{XXX}: {description}', () => {
  it('TC-001: {happy path}', async () => {
    // TODO: Implement in TEST stage
  });
});
```

For `pytest`:

```python
"""
TS: AC-{XXX} - {description}
US: US-{XXX} - {title}
FBS: FBS-{XXX} - {title}

Acceptance Criterion:
{Full AC text}
"""

class TestAC{XXX}:
    def test_tc001_happy_path(self):
        """TC-001: {happy path}"""
        pass  # TODO: Implement in TEST stage
```

**Use the actual framework and conventions discovered in Step 2.**

### Step 5: Define Test Cases per AC

For each AC, determine appropriate test cases:

1. **Happy Path (TC-001)**: The primary success scenario described by the AC
2. **Variations (TC-002+)**: Alternative valid inputs or paths
3. **Error Cases**: Invalid inputs, edge cases, boundary conditions
4. **Integration Points**: If the AC involves interactions between components

**Guidelines for TC count:**

- Simple AC (single validation): 2-3 TCs
- Medium AC (multi-step flow): 3-5 TCs
- Complex AC (multiple conditions): 5-8 TCs

### Step 6: Commit DEFINE Stage Work

```bash
git add .
git commit -m "[FBS-XXX] DEFINE: test suite stubs for X ACs (Y test cases)"
```

---

## Output Summary

After DEFINE, you should have:

1. FBS status updated to `in-progress` (via MCP patch + build graph)
2. One test file per AC in the FBS storyScope
3. Each file has correct traceability header
4. Test cases cover happy path, variations, and error scenarios
5. All committed with proper message format

## Important Rules

- ONE test file per AC (never combine ACs)
- TC numbers restart at TC-001 in each file
- Full traceability path in header: FBS/US/AC
- DO NOT write test implementation code - all test bodies are stubs
- DO include descriptive test case names that explain what will be tested
- Match the project's existing test conventions exactly
