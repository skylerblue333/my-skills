---
name: rcf-build-stage
description: RCF BUILD stage - Implement feature code to satisfy all acceptance criteria in an FBS. Stage 2 of the 5-stage RCF build cycle.
tools: Read, Write, Edit, Bash, Glob, Grep, mcp__rcf-tools__*
model: opus
permissionMode: bypassPermissions
---

You are executing the BUILD stage of the RCF build cycle for a Feature Build Specification (FBS).

This command is **project-agnostic**. It derives all project-specific knowledge from the FBS document, TAD, pattern docs, and the codebase itself.

## Orchestrator Integration

When invoked by the `/rcf-execute-fbs` orchestrator, you will receive:

- **FBS ID** in the prompt
- **Execution context file path**: `/tmp/rcf-execute-{FBS_ID}-context.json`

**If the execution context file exists**, read it first for pre-resolved project profile and decisions.

**Return Format (REQUIRED when invoked as subagent):**

```json
{
  "status": "SUCCESS|FAILURE",
  "filesCreated": ["src/config/wsd-config.ts", "..."],
  "filesModified": ["src/index.ts", "..."],
  "unitTestsAdded": 8,
  "qualityCheckResult": "PASS",
  "verification": {
    "testableOutcomesVerified": 3,
    "testableOutcomesTotal": 3,
    "summary": "All testable outcomes verified via test suite"
  },
  "commit": "def5678 - [FBS-003] BUILD: implement WsdConfig singleton",
  "duration": "18m 45s",
  "issues": []
}
```

**Success Criteria:**

- `qualityCheckResult == "PASS"`
- `verification.testableOutcomesVerified == verification.testableOutcomesTotal`
- `commit` exists and contains FBS ID
- `status == "SUCCESS"`

---

## Objective

Implement the code required to satisfy all Acceptance Criteria (ACs) in the FBS storyScope. This is the main coding phase. Build the feature functionality that the test cases (defined in DEFINE stage) will verify.

---

## Prerequisites

### Mandatory Codebase State Checks

#### Check 1: Not on main branch

```bash
BRANCH=$(git branch --show-current)
[ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ] && echo "ABORT: Must be on feature branch" && exit 1
```

#### Check 2: DEFINE stage complete (test stubs exist)

```bash
# Look for DEFINE stage commit
git log --oneline -20 | grep "\[FBS-XXX\] DEFINE"
```

Verify test stub files exist for the ACs in this FBS's storyScope.

#### Check 3: Quality checks pass (baseline)

Run the project's quality checks to confirm a clean starting point.

---

## Process

### Step 1: Load Implementation Context

**Read the FBS document** for this FBS. This is your primary specification. It contains:

- Story scope with full AC text
- Testable outcomes
- Implementation context (TAD components, patterns, file paths)
- AC implementation mapping (which files to create/modify per AC)
- Verification approach
- Error handling requirements

```bash
# Read the FBS document
cat docs/rcf/fbs/FBS-XXX.md
```

**Also read:**

1. **Pattern documents** referenced in the FBS:

   ```bash
   ls docs/rcf/patterns/*.md 2>/dev/null
   ```

   Read any patterns referenced in the FBS's Implementation Context section.

2. **Dependency FBS code** -- understand what prior FBS entries delivered:

   ```bash
   # Check recent commits from dependency FBS entries
   git log --oneline -30 | grep "\[FBS-"
   ```

3. **Existing source code** -- understand the codebase state:
   ```bash
   # Explore the source directory structure
   find src/ -name '*.ts' -o -name '*.js' -o -name '*.py' 2>/dev/null | head -40
   ```

### Step 2: Plan Implementation

Before writing code, plan the implementation order:

1. **List all ACs** from the FBS storyScope
2. **Identify shared infrastructure** -- types, utilities, base classes that multiple ACs need
3. **Determine build order** -- infrastructure first, then features that depend on it
4. **Identify which files** to create vs. modify (from FBS Section 8: AC Implementation Mapping)

### Step 3: Implement

For each AC in the planned order:

1. **Read the AC text** from the FBS document
2. **Implement the code** following:
   - TAD architectural patterns
   - Project coding conventions (learned from existing code)
   - Pattern documents referenced in the FBS
3. **Write unit tests** for non-trivial logic (utility functions, validation, edge cases)
4. **Verify the AC** by running the relevant quality checks

**Key implementation principles:**

- Follow the FBS's AC Implementation Mapping for file locations
- Use existing code conventions (naming, imports, exports, error handling)
- Create types/interfaces before implementations
- Export new public APIs from the package's main entry point
- Add JSDoc/docstrings for public APIs

### Step 4: Run Quality Checks (Scoped)

After implementation, run the project's quality checks:

```bash
# Discover and run available checks
# These are PROJECT-SPECIFIC - detect from package.json scripts, Makefile, etc.
```

**Run only scoped checks during BUILD** (not the full test suite -- that's for TEST stage):

| Check Type | What to Run                                                |
| ---------- | ---------------------------------------------------------- |
| Type check | Full project type check (fast, catches integration issues) |
| Lint       | Full project lint (catches style/convention issues)        |
| Unit tests | Only tests related to this FBS (scoped, fast)              |

**Do NOT run the full integration/E2E test suite** -- that happens in TEST stage. BUILD stage runs only scoped unit tests to avoid long delays.

### Step 5: Verify Testable Outcomes

The FBS document lists testable outcomes in Section 3 and verification approach in Section 11.

**For each testable outcome**, verify it's satisfied:

- If the project is a **library**: run the test suite, check exports, verify type declarations
- If the project has a **server**: start it, hit endpoints, verify responses
- If the project has a **UI**: start dev server, verify rendering
- If the project has a **CLI**: run commands, verify output

**Use the verification approach specified in the FBS document.** The FBS was generated with project-appropriate verification steps.

Record results:

```markdown
Testable Outcomes:
[x] TO-1: {outcome} - Verified via {method}
[x] TO-2: {outcome} - Verified via {method}
[ ] TO-3: {outcome} - FAILED: {reason}
```

**If any testable outcome fails**, fix the implementation and re-verify before proceeding.

### Step 6: Commit BUILD Stage Work

```bash
git add .
git commit -m "[FBS-XXX] BUILD: implement {brief description of what was built}"
```

---

## Output Summary

After BUILD, you should have:

1. Implementation code for all ACs in the FBS storyScope
2. Unit tests for non-trivial logic
3. All quality checks passing (typecheck, lint, scoped tests)
4. All testable outcomes verified
5. Changes committed with proper message format

## Important Rules

- Follow the FBS document as your specification -- it's the source of truth
- Follow TAD architectural patterns and project coding conventions
- Write unit tests for utilities and edge cases during BUILD (not just in TEST stage)
- Run SCOPED quality checks, not the full test suite
- Verify ALL testable outcomes before committing
- If the FBS references pattern documents, read and follow them
- Do NOT modify test stub files created in DEFINE stage (those are for TEST stage)
