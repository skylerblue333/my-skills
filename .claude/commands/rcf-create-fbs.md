---
description: Generate an RCF Feature Build Specification (FBS) document from Build Sequence context
argument-hint: <FBS-ID> (e.g., FBS-011)
---

# Generate FBS Document: $ARGUMENTS

You are generating a Feature Build Specification (FBS) document for **$ARGUMENTS** following the RCF methodology.

This command is **project-agnostic**. It derives all project-specific knowledge from RCF artefacts (TAD, PRD, User Stories, Build Sequence) and the codebase itself. It does NOT assume any particular tech stack, framework, or project type.

---

## CRITICAL: Data Access Rules

**You MUST use MCP tools for all RCF context and data. NEVER read local RCF JSON files directly.**

### ALLOWED - Use MCP Tools:

- `rcf_status` - Connection and project status
- `rcf_fbs_context` - FBS context including TAD, PRD, User Stories, Build Sequence, **FBS Template**
- `rcf_query` - Traceability queries (coverage, trace-forward, trace-back)
- `rcf_tad_view` - View Technical Architecture Document
- `rcf_stories_view` - View User Stories
- `rcf_prd_view` - View Product Requirements Document
- `rcf_build_sequence_view` - View Build Sequence

### PROHIBITED - Never Read These Files Directly:

- `docs/rcf/*.json` - All RCF JSON files (PRD, User Stories, TAD, Build Sequence)
- `docs/rcf/**/*.json` - Any nested RCF JSON files
- Local file reads for PRD content, User Story content, AC content, or TAD content

**Why?** The MCP tools provide parsed, validated, and contextually-enriched data. Reading raw JSON files bypasses validation, may access stale data, and loses the traceability context the MCP server provides.

---

## Step 1: Verify Connection

Check that the RCF MCP server is connected and has the required data:

**Call:** `rcf_status`

If not connected, stop and inform the user to run `rcf_connect` with their repository and branch first.

---

## Step 2: Retrieve FBS Context and Template

**Call:** `rcf_fbs_context` with `fbsId: "$ARGUMENTS"`

This returns comprehensive context including:

- **FBS entry** from Build Sequence (title, summary, story scope, dependencies, testable outcomes)
- **Build Sequence position** (what comes before/after)
- **User Stories** with full AC text (filtered to FBS scope)
- **TAD sections** (relevant components, patterns, decisions)
- **PRD requirements** context
- **Dependency FBS summaries**
- **FBS Template** (`template` field) - **The authoritative template to use for document generation**
- **Section-by-section generation guidance** (`guidance` field)

**CRITICAL:** The `template` field contains the FBS-TEMPLATE.md content. You **MUST** use this template structure for the generated document. Do **NOT** use any other FBS document or inline structure as a reference.

**If the FBS entry is not found**, stop and inform the user that $ARGUMENTS does not exist in the Build Sequence.

---

## Step 3: Build Project Profile (from TAD and Codebase)

**CRITICAL: Do NOT skip this step.** The project profile drives all subsequent analysis. Every downstream decision (layer detection, dependency analysis, verification approach) depends on understanding what kind of project this is.

### 3.1 Extract Tech Stack from TAD

From the TAD sections returned by `rcf_fbs_context`, extract:

```
PROJECT PROFILE (derived from TAD):
  Language:       {e.g., TypeScript, Python, Go, Rust}
  Project Type:   {e.g., library, web application, API service, CLI tool, monorepo}
  Framework:      {e.g., Lit, React, Express, FastAPI, none}
  Build Tool:     {e.g., tsc, webpack, vite, cargo, go build}
  Test Framework: {e.g., @open-wc/testing + Web Test Runner, Jest, pytest, go test}
  Package System: {e.g., npm/pnpm, pip, cargo, go modules}
  Source Root:    {e.g., src/, lib/, packages/}
  Test Root:      {e.g., tests/, src/**/*.test.ts, __tests__/}
```

### 3.2 Detect Project Characteristics

Scan the TAD and codebase to determine which of these apply:

| Characteristic         | How to Detect                                                  |
| ---------------------- | -------------------------------------------------------------- |
| Has a runtime server   | TAD mentions endpoints, ports, middleware, request handling     |
| Has a UI               | TAD mentions components, rendering, DOM, browser               |
| Has a database         | TAD mentions persistence, schema, migrations, ORM              |
| Has external services  | TAD mentions integrations, third-party APIs, webhooks          |
| Has authentication     | TAD mentions auth, tokens, sessions, permissions               |
| Is a library/package   | TAD mentions consumers, exports, package distribution, API surface |
| Has CI/CD              | TAD mentions pipelines, workflows, deployment                  |

**Store these as boolean flags.** They determine which analysis steps are relevant and which sections of the FBS need detailed content vs. "N/A".

### 3.3 Learn Conventions from Codebase

Explore the actual codebase to understand established patterns:

```bash
# Find existing source files to understand directory structure
find . -name '*.ts' -o -name '*.js' -o -name '*.py' -o -name '*.go' -o -name '*.rs' | head -30

# Find existing test files to understand test conventions
find . -path '*/test*' -name '*.spec.*' -o -name '*.test.*' | head -20

# Check for project config files
ls -la package.json tsconfig.json pyproject.toml Cargo.toml go.mod 2>/dev/null

# Check for build/quality scripts
cat package.json | jq '.scripts' 2>/dev/null || cat Makefile 2>/dev/null | head -30
```

**From this, note:**
- Directory naming conventions (kebab-case, camelCase, etc.)
- File naming conventions for source and tests
- Import/export patterns
- Test file placement (co-located vs. separate test directory)

### 3.4 Learn from Prior FBS Documents

Check if prior FBS documents exist and learn from their conventions:

```bash
ls docs/rcf/fbs/ 2>/dev/null
```

**If prior FBS documents exist**, read the most recent 1-2 to understand:
- How sections were populated for this specific project
- What verification approach was used
- How implementation tasks were structured
- What level of detail was appropriate

**This is how the command avoids reinventing conventions on every run.** By FBS-020, the agent should be producing documents that are stylistically consistent with FBS-001 through FBS-019.

---

## Step 4: Semantic Dependency Analysis

Analyze the acceptance criteria to identify ALL implied dependencies and work required for full implementation.

### 4.1 AC-Driven Layer Detection

Analyze each Acceptance Criterion in the FBS storyScope to identify which implementation concerns are involved.

**Generic keyword scan** (apply regardless of project type):

| Concern                  | Detection Keywords/Patterns                                                                      |
| ------------------------ | ------------------------------------------------------------------------------------------------ |
| **User-facing output**   | "displays", "shows", "renders", "user sees", "output", "visible", "notification"                |
| **Input/configuration**  | "accepts", "configures", "sets", "provides", "input", "parameter", "option", "property"         |
| **Data persistence**     | "stores", "persists", "retrieves", "saves", "caches", "records"                                 |
| **Network/API**          | "requests", "endpoint", "response", "fetches", "calls", "sends", "receives", "connects"        |
| **Authentication/authz** | "authenticated", "authorized", "permission", "token", "session", "credential"                   |
| **Validation**           | "validates", "rejects", "throws error", "invalid", "required field", "format"                   |
| **Events/messaging**     | "emits", "dispatches", "listens", "subscribes", "publishes", "triggers", "callback"             |
| **Lifecycle/state**      | "initialises", "destroys", "connected", "disconnected", "updates", "transitions", "state"       |
| **Error handling**       | "error", "fails gracefully", "fallback", "retry", "timeout", "catches"                         |
| **Integration**          | "integrates", "third-party", "external", "webhook", "plugin"                                    |
| **Performance**          | "within X ms", "efficiently", "lazy", "deferred", "throttle", "debounce"                       |

**Cross-reference with TAD.** The TAD defines the project's actual architectural layers (e.g., for WAIF: WsdConfig, ApiController, SseController, PollingController, WsdErrorBoundary). Map each detected concern to the TAD-defined components that handle it.

**Output a table:**

```markdown
| AC     | Primary Concerns               | TAD Components Involved            |
| ------ | ------------------------------ | ---------------------------------- |
| AC-105 | Input/configuration, Lifecycle | WsdConfig                          |
| AC-226 | Network/API, Authentication    | ApiController, WsdConfig           |
```

### 4.2 Implied Dependency Detection

**Do NOT use a hardcoded list of prerequisites.** Instead, derive implied dependencies from:

1. **The TAD** -- What modules, components, or services does the TAD define? Which are prerequisites for the detected concerns?

2. **The dependency FBS summaries** -- What do the explicit FBS dependencies deliver? What capabilities do they provide that this FBS builds on?

3. **The codebase** -- What already exists? What's missing?

**For each detected concern, ask:**

> "Given this project's TAD-defined architecture, what must exist for this AC to be implementable? Is it provided by a dependency FBS, already in the codebase, or does this FBS need to create it?"

**Document the results as:**

```markdown
| Capability Needed         | Source                | Status                        |
| ------------------------- | --------------------- | ----------------------------- |
| WsdConfig singleton       | FBS-003 (dependency)  | Must be complete before build |
| CSS custom properties     | FBS-004 (dependency)  | Must be complete before build |
| Test framework setup      | This FBS creates it   | In scope                      |
| ESLint configuration      | Already in codebase   | Available                     |
```

### 4.3 Cross-Cutting Concerns Analysis

Identify cross-cutting concerns relevant to this FBS:

| Concern            | Analysis Question                            | If Yes, Requires                     |
| ------------------ | -------------------------------------------- | ------------------------------------ |
| **Error Handling** | Do any ACs involve operations that can fail? | Error types, handlers, user feedback |
| **Logging**        | Are there operations that need audit trails? | Structured logging, log levels       |
| **Validation**     | Is input accepted from users or consumers?   | Validation logic, error messages     |
| **Security**       | Is sensitive data handled?                   | Input sanitization, output encoding  |
| **Performance**    | Are there latency-sensitive operations?      | Optimisation, caching, lazy loading  |
| **Testing**        | How will each AC be verified?                | See RCF Testing Classification below |

### 4.4 RCF Testing Classification

**CRITICAL:** Every AC must be classified for test type. This classification drives the Testing Strategy section of the FBS and ensures RCF traceability from AC through to test verification.

**Read the project's testing pattern** (e.g., `docs/rcf/patterns/14-testing-strategy.md` or equivalent) to understand the project's specific conventions. The following principles apply universally:

#### RCF Traceability Chain for Tests

```
PRD → REQ → US → AC → TS (Test Suite) → TC (Test Case)
```

- Each AC maps to exactly **one Test Suite (TS)** — a single test file
- Each TS contains multiple **Test Cases (TC)** numbered `TC-001`, `TC-002`, etc.
- The full traceability path (e.g., `US-123/AC-456/TC-002`) provides global uniqueness

#### AC Test Type Decision

For EACH AC in the FBS storyScope, apply this decision:

```
Does the AC describe UI interaction (clicks, renders, navigation, visual feedback)?
│
├── YES → E2E test
│         File: tests/e2e/US-{XXX}/AC-{XXX}.spec.ts
│         Framework: Playwright (or project's E2E framework)
│
└── NO  → Integration test
          File: tests/integration/api/US-{XXX}/AC-{XXX}.test.ts
          Framework: supertest / HTTP client (or project's integration framework)
```

**No-duplication rule:** If an E2E test exercises a backend endpoint as part of a UI flow, that satisfies the AC. Do NOT also write an integration test for the same AC.

#### Traceability Header Requirement

Every RCF-traced test file (integration and E2E) MUST include a JSDoc header:

```typescript
/**
 * TS: AC-{XXX} - {AC title/description}
 * US: US-{XXX} - {User story title}
 * REQ: REQ-{XXX}
 */
```

#### Unit Tests (Non-RCF)

Unit tests verify implementation logic in isolation (mock all dependencies). They are:
- Colocated with source files as `{module}.test.ts`
- Outside RCF traceability (no TS/US/REQ headers required)
- Complementary to, not a replacement for, RCF-traced integration/E2E tests

#### Output: AC Test Classification Table

Produce a table classifying every AC:

```markdown
| AC      | Test Type   | Test File Path                                    | Rationale        |
| ------- | ----------- | ------------------------------------------------- | ---------------- |
| AC-101  | Integration | tests/integration/api/US-050/AC-101.test.ts       | API endpoint, no UI |
| AC-102  | E2E         | tests/e2e/US-050/AC-102.spec.ts                   | User clicks button |
| AC-103  | Integration | tests/integration/api/US-051/AC-103.test.ts       | Webhook handler  |
```

This table feeds directly into the FBS Testing Strategy section (Section 7) and AC Implementation Mapping section (Section 8).

### 4.5 Dependency FBS Verification

For each explicit dependency listed in the FBS entry:

1. **Check dependency status** -- Is it `verified` or at least `complete`?
2. **Verify deliverables** -- What capabilities does it provide?
3. **Identify gaps** -- Does this FBS need something the dependency doesn't deliver?

**If a dependency is NOT complete:**

```markdown
WARNING: Dependency FBS-XXX is not verified (status: {status})

- Risk: Implementation may be blocked or require rework
- Recommendation: Verify FBS-XXX completion before starting this FBS
```

---

## Step 5: Project Pattern Analysis

### 5.1 Discover All Project Patterns

**Search for existing pattern documentation:**

```bash
find docs/rcf/patterns/ -name '*.md' 2>/dev/null
```

**Read each pattern file** to understand what's documented.

### 5.2 Pattern Relevance Assessment

For each discovered pattern, assess relevance to this FBS:

| Pattern File        | Pattern Name    | Relevant to $ARGUMENTS? | Reason                |
| ------------------- | --------------- | ----------------------- | --------------------- |
| `{filename}.md`     | {Pattern Name}  | Yes/No                  | {Why relevant or not} |

**Relevance criteria:**

- Pattern addresses a concern identified in Step 4
- Pattern provides implementation guidance for detected layers
- Pattern defines conventions this FBS should follow
- Pattern establishes contracts this FBS must implement

### 5.3 Cross-Reference with TAD

From TAD context (returned in Step 2):

1. **TAD Architectural Decisions (ADRs)** -- What patterns do they mandate?
2. **TAD Components** -- What patterns do they use?
3. **TAD Integration Architecture** -- What integration patterns apply?

### 5.4 Pattern Gap Analysis

Compare required patterns against available patterns.

**For each required but missing pattern**, present to user:

```markdown
## Pattern Required: {Pattern Name}

**Problem:** {What problem does this pattern solve?}
**Proposed Approach:** {Brief description of the pattern}
**Applies to $ARGUMENTS:** {How this FBS will use the pattern}

Would you like me to create this pattern document before proceeding with the FBS?
Options:

1. Yes, create the pattern document
2. Skip (document approach inline in FBS instead)
3. Modify the proposed approach
```

### 5.5 Create Missing Patterns (If Approved)

For each approved pattern, generate and save to `docs/rcf/patterns/{pattern-name}.md`.

### 5.6 Compile Pattern Reference Table

Compile the complete pattern reference for the FBS template's Implementation Context and References sections.

---

## Step 6: Implementation Completeness Verification

Before generating the FBS document, verify implementation can succeed.

### 6.1 AC Implementation Feasibility

For EACH Acceptance Criterion, verify:

| AC ID  | AC Description | All Concerns Covered? | Prerequisites Met? | Blockers            |
| ------ | -------------- | --------------------- | ------------------ | ------------------- |
| AC-XXX | {Description}  | Yes/No                | Yes/No             | {List any blockers} |

### 6.2 Missing Capability Identification

For each missing capability, decide:

1. **Add to this FBS** -- Include in implementation tasks
2. **Add as prerequisite** -- Must be done before this FBS
3. **Create separate FBS** -- Split into infrastructure FBS
4. **Document as risk** -- Proceed with documented gap

### 6.3 Completeness Checklist

Before proceeding, verify:

- [ ] **All ACs are implementable** -- No blockers identified
- [ ] **All concerns are covered** -- Implementation tasks planned for each
- [ ] **All dependencies verified** -- Prior FBS work complete or in-scope
- [ ] **All patterns documented** -- Referenced or created
- [ ] **Cross-cutting concerns addressed** -- Error handling, validation, etc.
- [ ] **Test strategy viable** -- Every AC classified as Integration or E2E (Step 4.4), test file paths specified, traceability headers defined

**If any item fails**, inform the user and recommend action before proceeding.

---

## Step 7: Generate FBS Document Using Template

**CRITICAL:** Use the `template` field from the `rcf_fbs_context` response as your document structure.

### Template Population Guidance

Use the `guidance` field from `rcf_fbs_context` for section-by-section instructions:

- **from-context**: Populate directly from the MCP context data
- **agent-codebase**: Requires exploring the codebase for real paths/patterns
- **agent-inference**: Requires analysis and professional judgment

### Key Section Requirements

**Implementation Context section:**

- Include the concern-to-component mapping table from Step 4.1
- Include pattern table from Step 5.6 with `docs/rcf/patterns/` links where available
- Include dependency analysis from Steps 4.2 and 4.4
- Use REAL file paths from codebase exploration (Step 3.3)
- Use REAL interfaces/types from codebase where they exist

**AC Implementation Mapping section:**

For EACH AC, document:

- Implementation concerns involved (from Step 4.1)
- Source files to create or modify (use project's actual directory conventions)
- TAD components involved
- **Test classification** from Step 4.4 (Integration or E2E, with exact file path)
- Traceability header content (TS/US/REQ values for the test file)

**Do NOT use hardcoded layer names like "Backend", "Frontend", "Database".** Use the actual TAD-defined component names and the concerns identified in Step 4.1.

**Verification section:**

This section tells the BUILD stage agent how to verify the implementation works.

**Adapt verification approach to the project type (from Step 3.2):**

| Project Characteristic | Verification Approach                                                   |
| ---------------------- | ----------------------------------------------------------------------- |
| Is a library/package   | Run test suite, verify exports, check type declarations                |
| Has a runtime server   | Start server, hit endpoints, verify responses                          |
| Has a UI               | Start dev server, interact with UI, verify rendering                   |
| Has a database         | Run migrations, verify schema, check queries                           |
| Is a CLI tool          | Run commands, verify output, check exit codes                          |

**Populate the verification section with project-appropriate content.** For a library, this might be:

```markdown
### Verification Approach

| Item                | Value                              |
| ------------------- | ---------------------------------- |
| Build command        | `{from project profile}`          |
| Test command         | `{from project profile}`          |
| Type check command   | `{from project profile}`          |

### Verification Checkpoints

- [ ] **TO-1:** {Testable outcome}
  - Verify: `{specific test command or assertion}`
  - Expected: {what should happen}
```

For a web application with auth, it might include URLs, credentials, and API testing steps. **Let the project profile drive the content, not a hardcoded template.**

**Appendix: Execution Readiness**

Complete the pre-execution verification checklist to confirm the FBS is ready for the 5-stage execute workflow.

---

## Step 8: Review and Validate

Before saving, verify:

1. **Template adherence** -- Document follows the template structure from `rcf_fbs_context`
2. **Traceability complete** -- Every AC maps to implementation AND a classified test file (Integration or E2E) with RCF traceability header (TS/US/REQ)
3. **All testable outcomes** have verification methods appropriate to the project type
4. **Verification section** provides sufficient info for a BUILD stage agent to verify the implementation works autonomously
5. **No open blockers** in Open Questions section that would prevent execution
6. **Execution readiness** checklist is complete
7. **Consistency with prior FBS documents** -- If prior FBS docs exist, this one follows the same conventions for structure, detail level, and terminology

---

## Step 9: Save the Document

After generating the complete FBS markdown:

1. **Review** the generated document for completeness
2. **Save** using the `rcf_fbs_save` tool:

```
rcf_fbs_save({
  fbsId: "$ARGUMENTS",
  markdown: "<generated markdown content>"
})
```

This will:

- Commit the FBS to the connected branch
- Update the manifest
- Return the file path and next steps

## Post-Save Actions

After saving:

1. Run `git pull` to sync the committed FBS locally
2. The FBS document will be at `docs/rcf/fbs/$ARGUMENTS.md`
3. Ask user if they want to:
   - Generate the next FBS in the build sequence
   - Proceed with `/rcf-execute-fbs $ARGUMENTS`
   - Review the generated document first

---

## Summary

The FBS generation workflow:

1. **Verify connection** -- `rcf_status`
2. **Get context and template** -- `rcf_fbs_context({ fbsId: "$ARGUMENTS" })` returns data AND template
3. **Build project profile** (Step 3) -- Derive tech stack, conventions, and project type from TAD and codebase
4. **Semantic analysis** (Step 4) -- Concerns, dependencies, cross-cutting issues (guided by project profile)
5. **Pattern analysis** (Step 5) -- Discover, assess, create missing patterns
6. **Completeness verification** (Step 6) -- Ensure implementation can succeed
7. **Generate document** (Step 7) -- Use template from context, populate all sections using project-specific conventions
8. **Review and validate** (Step 8) -- Confirm execution readiness and consistency
9. **Save** (Step 9) -- `rcf_fbs_save`

**Key Principles:**

- Use MCP tools for all RCF data access
- **Use the template from `rcf_fbs_context`** (NOT existing FBS documents or inline structure)
- **Derive project-specific behaviour from TAD and codebase** (NOT hardcoded assumptions)
- **Learn conventions from prior FBS documents** when they exist
- The FBS must be self-contained -- a coding agent should be able to execute it using only this document plus codebase access
- The verification section must be appropriate to the project type and sufficient for autonomous BUILD stage execution
