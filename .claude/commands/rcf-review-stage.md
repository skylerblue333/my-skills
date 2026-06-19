---
name: rcf-review-stage
description: RCF REVIEW stage - Verify implementation against specs and fix gaps. Stage 3 of the 5-stage RCF build cycle.
tools: Read, Write, Edit, Bash, Glob, Grep, mcp__rcf-tools__*
model: opus
permissionMode: bypassPermissions
---

You are executing the REVIEW stage of the RCF build cycle for a Feature Build Specification (FBS).

This command is **project-agnostic**. It derives all project-specific knowledge from the FBS document, TAD, and codebase.

## Orchestrator Integration

When invoked by the `/rcf-execute-fbs` orchestrator:

- **FBS ID** in the prompt
- **Execution context file path**: `/tmp/rcf-execute-{FBS_ID}-context.json`

**Return Format (REQUIRED when invoked as subagent):**

```json
{
  "status": "SUCCESS|FAILURE",
  "acsReviewed": 5,
  "issuesFound": { "critical": 0, "major": 1, "minor": 2 },
  "issuesFixed": { "critical": 0, "major": 1, "minor": 1 },
  "issuesDeferred": { "minor": 1, "reason": "cosmetic, defer to polish phase" },
  "commit": "ghi9012 - [FBS-003] REVIEW: fix validation gaps",
  "duration": "12m 18s",
  "issues": []
}
```

**Success Criteria:**

- `issuesFound.critical == 0` (no unresolved critical issues)
- All major issues fixed
- `commit` exists and contains FBS ID
- `status == "SUCCESS"`

---

## Objective

Systematically verify the BUILD stage implementation against the FBS specification, User Stories, Acceptance Criteria, and TAD architecture. Identify gaps, fix them, and ensure the implementation is ready for TEST stage.

---

## Prerequisites

#### Check 1: Not on main branch

#### Check 2: BUILD stage complete (implementation exists)

```bash
git log --oneline -20 | grep "\[FBS-XXX\] BUILD"
```

#### Check 3: Quality checks pass

Run the project's type check and lint. Must pass before review.

---

## Process

### Step 1: Load Review Context

Read the FBS document for this FBS ID:

```bash
cat docs/rcf/fbs/FBS-XXX.md
```

From the FBS document, extract:

- All ACs in storyScope with full text
- Testable outcomes
- Implementation context (TAD components, patterns)
- AC Implementation Mapping (expected files per AC)
- Error handling requirements

### Step 2: AC-by-AC Verification

For EACH Acceptance Criterion in the FBS storyScope:

**Verification checklist:**

```markdown
## AC-XXX: {description}

### Implementation Coverage

- [ ] Primary functionality implemented as described in AC text
- [ ] All conditions in AC text handled (every "when", "if", "must", "should")
- [ ] Edge cases considered
- [ ] Error scenarios handled

### Code Quality

- [ ] Follows TAD architecture patterns
- [ ] Follows project coding conventions
- [ ] Follows referenced pattern documents
- [ ] Proper error handling
- [ ] Input validation complete (if applicable)

### Traceability

- [ ] Implementation matches AC intent
- [ ] Test stubs exist for this AC (from DEFINE stage)

### Issues Found

- {List any problems}
```

### Step 3: Architecture Compliance

Verify implementation follows TAD specifications:

- [ ] Code is in correct directories per TAD/FBS mapping
- [ ] Dependencies follow allowed patterns (no circular deps)
- [ ] Public APIs match expected interfaces
- [ ] Error handling follows project conventions
- [ ] Naming conventions followed

**Read the pattern documents** referenced in the FBS and verify compliance.

### Step 4: Testable Outcomes Re-verification

Review each testable outcome from the FBS:

| #   | Outcome | Status    | Notes                |
| --- | ------- | --------- | -------------------- |
| 1   | {text}  | PASS/FAIL | {verification notes} |

### Step 5: Edge Case Analysis

Check for missing edge cases relevant to the detected concerns:

**Input Edge Cases:**

- Empty/null/undefined inputs
- Boundary values (0, -1, max)
- Invalid types

**State Edge Cases:**

- Uninitialised state access
- Double initialisation
- Concurrent access (if applicable)

**Error Edge Cases:**

- Network failures (if applicable)
- Timeout handling (if applicable)
- Invalid responses from dependencies

### Step 6: Fix Issues

For each issue found:

1. **Categorise by severity:**
   - **Critical**: Blocks AC verification, must fix now
   - **Major**: Significant gap, should fix now
   - **Minor**: Polish item, can defer

2. **Fix critical and major issues** -- make code changes, verify fix doesn't break existing work

3. **Document deferred items** in the commit message

### Step 7: Final Verification Pass

After fixes:

```bash
# Run quality checks (project-specific commands)
# Type check, lint, scoped unit tests
```

Verify all testable outcomes one more time.

### Step 8: Commit REVIEW Stage Work

```bash
git add .
git commit -m "[FBS-XXX] REVIEW: fix {brief summary of issues fixed}"
```

If no issues were found:

```bash
git commit --allow-empty -m "[FBS-XXX] REVIEW: all ACs verified, no issues found"
```

---

## Important Rules

- DO NOT skip any AC in the storyScope
- DO NOT proceed to TEST if critical issues remain
- DO document all findings, even if fixed immediately
- DO verify fixes don't introduce regressions (run quality checks after fixes)
- Be thorough -- issues caught here prevent rework in TEST stage
