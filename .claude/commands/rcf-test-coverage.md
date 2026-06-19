---
description: Analyze test coverage for a specific FBS - checks backend integration tests and frontend E2E tests against acceptance criteria
---

# RCF Test Coverage Analysis

Perform comprehensive test coverage analysis for a specific FBS (Feature Build Specification), identifying which acceptance criteria have backend integration tests and frontend E2E tests.

## Arguments

$ARGUMENTS

FBS identifier (e.g., `FBS-005`, `fbs-010`, `5`, `10`)

The command accepts flexible formats - it will normalize to `FBS-XXX` format.

## Objective

Generate a detailed test coverage report that shows:

1. **Backend Integration Test Coverage** - Which ACs have integration tests
2. **Frontend E2E Test Coverage** - Which ACs with Admin UI requirements have E2E tests
3. **Coverage Gaps** - Missing tests that need to be created
4. **Actionable Recommendations** - Next steps to achieve full coverage

## Prerequisites

Before running this command:

1. **Connect to the RCF project** using:

   ```
   rcf_connect({ repo: "owner/repo", branch: "current-branch" })
   ```

2. **Ensure the FBS exists** in the Build Sequence

## Execution Steps

### Step 1: Normalize FBS Identifier

Parse the provided argument and normalize to `FBS-XXX` format:

- `5` → `FBS-005`
- `fbs-005` → `FBS-005`
- `FBS-005` → `FBS-005`

### Step 2: Query FBS Details

Use the RCF MCP tool to get FBS information:

```
rcf_build_sequence_query({
  type: "fbs",
  target: "FBS-XXX"
})
```

Extract from the response:

- `id` - FBS identifier
- `title` - FBS title
- `summary` - FBS description
- `storyScope` - User stories and acceptance criteria in scope
- `status` - Current implementation status
- `domain` - Feature domain
- `riskLevel` - Risk classification

### Step 3: Parse Story Scope

Parse the `storyScope` field to extract:

- User Story IDs (e.g., `US-011`, `US-012`)
- Acceptance Criteria IDs (e.g., `AC-057`, `AC-058`)

Example storyScope format:

```
"US-011(AC-057,AC-058,AC-059), US-012(AC-063,AC-064)"
```

### Step 4: Query Acceptance Criteria Details

Use the RCF MCP tool to get full AC details:

```
rcf_query({
  type: "acs-for-stories",
  target: "US-011,US-012,..."  // comma-separated list of story IDs
})
```

From the response, categorize each AC:

- **Backend ACs** - Pure backend functionality (JWT validation, API responses, etc.)
- **Frontend ACs** - Mentions "Admin UI", "I am in the Admin UI", "through the Admin UI"

### Step 5: Search for Integration Tests

For each User Story, search for integration test files:

```
Glob: tests/integration/**/US-{XXX}/*.spec.ts
```

Map found test files to their AC numbers (e.g., `AC-057.spec.ts` → AC-057).

### Step 6: Search for E2E Tests

For each User Story with frontend ACs, search for E2E test files:

```
Glob: tests/e2e/**/US-{XXX}/*.spec.ts
```

Map found test files to their AC numbers.

### Step 7: Generate Coverage Report

Produce a structured report with the following format:

---

## Report Output Format

```markdown
## RCF Test Coverage Report: FBS-XXX

**Title:** [FBS Title]
**Status:** [complete/in-progress/etc.]
**Domain:** [Domain]
**Risk Level:** [high/medium/low]

---

### Summary

| Metric                    | Count | Coverage |
| ------------------------- | ----- | -------- |
| Total Acceptance Criteria | XX    | -        |
| Backend ACs               | XX    | XX%      |
| Frontend (Admin UI) ACs   | XX    | XX%      |
| **Overall Coverage**      | -     | **XX%**  |

---

### Backend Integration Test Coverage

| User Story | AC     | Description         | Test File                              | Status     |
| ---------- | ------ | ------------------- | -------------------------------------- | ---------- |
| US-XXX     | AC-XXX | [Brief description] | `tests/integration/.../AC-XXX.spec.ts` | ✅ Covered |
| US-YYY     | AC-YYY | [Brief description] | -                                      | ❌ Missing |

**Backend Coverage:** XX/XX ACs (XX%)

---

### Frontend E2E Test Coverage

#### ACs Requiring E2E Tests

These acceptance criteria explicitly mention Admin UI interactions:

| User Story | AC     | Requirement                     | Test File                      | Status     |
| ---------- | ------ | ------------------------------- | ------------------------------ | ---------- |
| US-XXX     | AC-XXX | "Given I am in the Admin UI..." | `tests/e2e/.../AC-XXX.spec.ts` | ✅ Covered |
| US-YYY     | AC-YYY | "Given the Admin UI..."         | -                              | ❌ Missing |

**Frontend Coverage:** XX/XX ACs (XX%)

#### ACs NOT Requiring E2E Tests

These acceptance criteria are backend-only (no UI interaction):

| User Story | AC     | Reason                 |
| ---------- | ------ | ---------------------- |
| US-XXX     | AC-XXX | Pure API validation    |
| US-YYY     | AC-YYY | Server-side processing |

---

### Coverage Gaps

#### Missing Backend Integration Tests

[List any ACs without integration tests, or state "None - all backend ACs covered"]

#### Missing Frontend E2E Tests

[List ACs with Admin UI requirements that lack E2E tests, or state "None - all frontend ACs covered"]

---

### Recommendations

1. **[Priority]** [Specific recommendation with AC reference]
2. **[Priority]** [Specific recommendation with AC reference]
   ...

---

### Test File Locations

**Integration Tests:**

- `tests/integration/api-service/US-XXX/` - [X tests]
- `tests/integration/backend/US-YYY/` - [Y tests]

**E2E Tests:**

- `tests/e2e/[domain]/US-XXX/` - [X tests]
```

---

## Classification Rules

### Identifying Frontend (Admin UI) ACs

An AC requires E2E testing if it **semantically implies user interface interaction**. Look for:

**Explicit UI references:**

- Direct mentions of "Admin UI", "UI", "interface", "dashboard", "page", "screen"

**Implied UI interactions:**

- User viewing, browsing, or listing data (e.g., "view all configurations", "see the list")
- User inputting, entering, or selecting data (e.g., "enter connection details", "select a data source")
- User saving, submitting, or confirming actions (e.g., "save changes", "confirm deletion")
- User receiving visual feedback (e.g., "displays error message", "shows validation errors")
- User navigating or accessing sections (e.g., "access settings", "navigate to")

**User-centric language patterns:**

- "Given I am..." or "Given the user..." followed by interaction verbs
- "When I [action]..." suggesting direct user manipulation
- "Then I can see..." or "Then I receive..." indicating visual feedback
- References to forms, buttons, dialogs, modals, tables, or lists in a user context

**Use judgment:** If an AC describes behavior that would only make sense with a user looking at and interacting with a screen, it likely needs E2E testing - even if "Admin UI" isn't explicitly mentioned.

### Identifying Backend-Only ACs

An AC is backend-only if it:

- Describes API responses (401, 403, 429, etc.)
- Describes token/JWT validation
- Describes logging/audit behavior
- Describes server-side processing
- Uses "when the system" language without UI context
- Describes environment variables or configuration loading

## Example Analysis

For FBS-010 (Role-Based Authorization System):

**Input:** `FBS-010` or `fbs-010` or `10`

**Story Scope:** `US-013(AC-069,AC-070,AC-071,AC-072,AC-073,AC-074), US-014(AC-075,AC-076,AC-077,AC-078)`

**Classification:**

- All 10 ACs are backend-only (role mapping, access control, audit logging)
- No Admin UI references → No E2E tests required

**Expected Output:**

```
Backend Integration Tests: 10/10 ✅
Frontend E2E Tests: 0/0 (N/A - no UI ACs)
Overall: 100% coverage
```

---

## Rules

- **DO** use RCF MCP tools to query FBS and AC details
- **DO** use Glob to search for test files
- **DO** categorize ACs as frontend vs backend based on description text
- **DO** provide specific file paths for existing tests
- **DO** list specific missing tests with AC references
- **DO** provide actionable recommendations
- **DON'T** assume tests exist without verifying with Glob
- **DON'T** require E2E tests for backend-only ACs
- **DON'T** skip any ACs in the FBS scope

## Related Commands

- `/rcf-functional-review` - Perform functional PR review for FBS implementations against their specifications
