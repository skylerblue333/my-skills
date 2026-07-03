# RCF Plan — Stock Buddy Skills Distribution & Access (PRD-002)

> **Status note.** The PRD (PRD-002, 16 requirements) was imported into RCF as a **draft**
> (validated, not committed). RCF's *AI generation* of stories/TAD/build-sequence is currently
> **blocked in this environment** — the RCF server's LLM key returns `401 invalid x-api-key`.
> The User Stories, Acceptance Criteria, TAD, and Build Sequence below are therefore authored
> directly, in RCF's structure (PRD → REQ → US → AC, plus TAD ADRs and a Build Sequence), so the
> plan is complete now. They can be loaded into RCF later via the deterministic `rcf_stories_patch`
> / `rcf_tad_patch` / `rcf_build_sequence_patch` tools (these commit to Git), or regenerated once
> the RCF key is restored.

Traceability: every Acceptance Criterion traces up to a User Story → Requirement, and references
the TAD ADR(s) that constrain its implementation.

---

## 1. User Stories & Acceptance Criteria

### REQ-001 — Land skills on default branch & pass spec validation
**US-001** — As a *maintainer*, I want the 14 skills pushed to the default branch and spec-validated,
so that downstream distribution can begin. *(TAD: ADR-008)*
- **AC-001** Given the PR is merged, when I list the default branch, then all 14 skill folders plus `README.md`, `USAGE.md`, `ACCESS_PLAN.md`, and `.gitignore` are present.
- **AC-002** Given the merged repo, when I run `gh skill publish`, then it reports 14 valid skills and 0 spec errors.
- **AC-003** Given a metadata nit, when I run `gh skill publish --fix`, then frontmatter is corrected and re-validates clean.

### REQ-002 — Install via `gh skill` across supported hosts
**US-002** — As a *coding-agent user*, I want to install a skill via `gh skill install` for my host, so that it is available inside my agent. *(TAD: ADR-001)*
- **AC-004** Given `gh` ≥ v2.90.0, when I run `gh skill install skylerblue333/my-skills technical-analysis --agent claude-code`, then the skill lands in the Claude Code skills directory.
- **AC-005** Given the same command with `--agent cursor` (and one more host), when it completes, then the skill is installed and listed by that host.
- **AC-006** Given an installed skill, when I issue a prompt matching its description, then the skill triggers and runs against sample input.

### REQ-003 — Versioned, pinnable, immutable releases
**US-003** — As a *maintainer*, I want immutable, pinnable releases, so that consumers get tamper-proof, reproducible installs. *(TAD: ADR-006)*
- **AC-007** Given the repo, when I cut tag `v1.0.0` and run `gh skill publish`, then immutable releases and tag protection are enabled.
- **AC-008** Given `v1.0.0`, when a consumer runs `gh skill install … --pin v1.0.0`, then the exact tree SHA for that tag is installed.
- **AC-009** Given an immutable release, when anyone attempts to alter it, then the change is rejected.

### REQ-004 — MCP server: one tool per skill
**US-004** — As an *MCP client developer*, I want each skill exposed as an MCP tool, so that my client can call them without understanding Agent Skills. *(TAD: ADR-002, ADR-003)*
- **AC-010** Given the server is running, when the client lists tools, then 14 tools appear, named after the skills.
- **AC-011** Given a tool call with contract-valid JSON, when it executes, then it returns the skill's Thinking Card JSON unchanged.
- **AC-012** Given malformed input, when a tool is called, then it returns a structured error (not a crash) and `isError` semantics.
- **AC-013** Given each tool, when its `inputSchema` is inspected, then it matches that skill's slice of the shared data contract.

### REQ-005 — Composite MCP pipeline tools
**US-005** — As an *MCP client developer*, I want `analyze_ticker` and `screen_market` tools, so that I get end-to-end results without orchestrating six calls. *(TAD: ADR-007)*
- **AC-014** Given a ticker payload, when I call `analyze_ticker`, then it runs leaf skills → `signal-synthesizer` → `risk-manager` and returns the dual-mode signal plus risk-checked levels.
- **AC-015** Given a universe payload, when I call `screen_market`, then it returns a ranked candidate list.
- **AC-016** Given a leaf skill error, when `analyze_ticker` runs, then the partial result and the failing stage are reported, not a silent drop.

### REQ-006 — MCP server packaging & client config
**US-006** — As an *MCP client developer*, I want zero-install runners and copy-paste config, so that setup takes minutes. *(TAD: ADR-005)*
- **AC-017** Given Node/Python installed, when I run `npx stock-buddy-mcp` (or `uvx`), then the server starts with no prior install step.
- **AC-018** Given the Dockerfile, when I build and run it, then the server serves over the configured transport.
- **AC-019** Given the docs, when I paste the Claude Desktop config block, then the tools appear in Claude Desktop.

### REQ-007 — Dual transport (stdio + HTTP)
**US-007** — As an *operator*, I want stdio and HTTP transports, so that both desktop and hosted clients work. *(TAD: ADR-005)*
- **AC-020** Given a desktop client, when it connects over stdio, then tool calls succeed.
- **AC-021** Given a hosted deployment, when a client connects over streamable HTTP, then tool calls succeed.

### REQ-008 — Pluggable DSE data adapter
**US-008** — As an *integrator*, I want a data adapter that yields the shared input contract, so that I don't hand-build JSON. *(TAD: ADR-004)*
- **AC-022** Given the adapter, when I request a ticker via the file/DB provider, then it returns a contract-valid input object.
- **AC-023** Given the DSE provider, when I request a covered ticker, then it returns OHLCV + fundamentals (+ available shareholding/news/macro).
- **AC-024** Given the provider interface, when a new provider is added, then no adapter-core changes are required.

### REQ-009 — Data access tool/CLI honouring constraints
**US-009** — As an *integrator*, I want `get_ticker_data` as a tool and CLI, so that fetch-then-analyse works from either door, compliantly. *(TAD: ADR-004)*
- **AC-025** Given a ticker, when I call `get_ticker_data`, then I receive a contract-valid object usable directly by `analyze_ticker`.
- **AC-026** Given repeated calls, when within the cache window, then the source is not re-hit (rate-limit respected).
- **AC-027** Given stale/missing data, when fetched, then data-quality flags are emitted (never silent drops); only public data is used.

### REQ-010 — CI validation on PRs
**US-010** — As a *maintainer*, I want CI on every PR, so that regressions can't merge. *(TAD: ADR-006)*
- **AC-028** Given a PR, when CI runs, then it compiles all scripts, runs each against `_fixtures/sample_input.json`, and asserts valid JSON + required Thinking-Card fields.
- **AC-029** Given a PR, when CI runs, then `gh skill publish` spec validation and the MCP server build both pass.
- **AC-030** Given a change that breaks a script's JSON output, when CI runs, then the PR check fails.

### REQ-011 — Release automation on tag
**US-011** — As a *maintainer*, I want tagging to publish artifacts, so that releases are repeatable and auditable. *(TAD: ADR-006)*
- **AC-031** Given a version tag, when the release workflow runs, then the MCP package (npm/PyPI) and Docker image are published.
- **AC-032** Given the same run, when it completes, then an immutable GitHub release is created with provenance/SBOM attached.

### REQ-012 — Supply-chain hardening
**US-012** — As a *security owner*, I want secret and code scanning enabled, so that leaks and vulnerabilities are caught. *(TAD: ADR-006)*
- **AC-033** Given the repo, when scanning is enabled, then secret scanning and code scanning run on pushes/PRs.
- **AC-034** Given a detected secret or vulnerability, when scanning runs, then an alert is surfaced to maintainers.

### REQ-013 — Discoverability & documentation
**US-013** — As a *prospective adopter*, I want clear docs and listings, so that I can find and adopt the suite quickly. *(TAD: ADR-001)*
- **AC-035** Given the README, when I read it, then it covers install for both doors, the pipeline diagram, and links to `USAGE.md`.
- **AC-036** Given the repo, when I look for sample data, then a copy-paste `gp.json` and per-skill quickstarts exist.
- **AC-037** Given the published repo, when I run `gh skill search`, then this repo's skills are discoverable.

### REQ-014 — Security & scope notice
**US-014** — As a *consumer*, I want a clear scope/safety notice, so that I understand limits before installing. *(TAD: ADR-001)*
- **AC-038** Given any consumer surface, when I read it, then an "educational only — not financial advice, public data only" notice is present.
- **AC-039** Given a skill output, when produced, then it carries the disclaimer field.
- **AC-040** Given install docs, when followed, then `gh skill preview` is recommended before install.

### REQ-015 — Versioning & maintenance policy
**US-015** — As a *maintainer*, I want a semver + provenance + changelog policy, so that consumers upgrade deliberately. *(TAD: ADR-006)*
- **AC-041** Given a release, when published, then a `CHANGELOG` entry exists and skill `metadata.version` matches the release.
- **AC-042** Given an install via `gh skill`, when frontmatter is inspected, then provenance (repo, ref, tree SHA) is recorded.

### REQ-016 — Periodic spec & host re-validation
**US-016** — As a *maintainer*, I want periodic re-validation, so that the suite stays installable as the ecosystem changes. *(TAD: ADR-006)*
- **AC-043** Given a schedule, when it fires, then `gh skill publish` validation and a host install smoke-test run.
- **AC-044** Given a spec or host change that breaks validation, when the check runs, then maintainers are notified.

---

## 2. Technical Architecture (TAD) — Decision Records

**ADR-001 — Two distribution doors.** *Context:* coding agents consume Agent Skills; many MCP
clients consume MCP tools. *Decision:* support both — Agent Skills via `gh skill` (Door 1) and an
MCP server (Door 2); keep direct CLI (Door 3). *Consequences:* one source of truth (the skill
folders), two thin delivery layers. *Related:* REQ-002, REQ-004, REQ-013, REQ-014.

**ADR-002 — MCP server implementation language.** *Context:* server must be easy for MCP clients to
run. *Options:* Node (`npx`, broadest MCP familiarity) vs Python (`uvx`, matches the skills'
runtime — no second toolchain). *Decision:* **pending user choice** (Open Decision #1); default
recommendation Python for runtime parity. *Consequences:* affects packaging and CI. *Related:*
REQ-004, REQ-006.

**ADR-003 — Skills stay pure CLIs; server invokes via subprocess JSON.** *Decision:* the MCP server
shells out to each skill script (JSON in/out) rather than re-implementing logic. *Consequences:*
zero logic duplication; skills remain independently runnable; server is a registry + dispatcher.
*Related:* REQ-004.

**ADR-004 — Separate data-adapter layer; no network in skills.** *Decision:* all fetching lives in a
pluggable adapter behind a provider interface; skills never make network calls. *Consequences:*
skills stay deterministic and portable; data concerns (caching, rate limits, public-data-only)
are isolated and testable. *Related:* REQ-008, REQ-009.

**ADR-005 — Packaging via npx/uvx + Docker; dual transport.** *Decision:* ship zero-install runners
and a container; support stdio and streamable HTTP. *Consequences:* covers desktop and hosted
clients with one server. *Related:* REQ-006, REQ-007.

**ADR-006 — Supply-chain & quality gates.** *Decision:* immutable releases + tag pinning +
provenance/SBOM; CI gates on PR; release automation on tag; secret/code scanning. *Consequences:*
trustworthy, reproducible distribution of executable instructions. *Related:* REQ-003, REQ-010,
REQ-011, REQ-012, REQ-015, REQ-016.

**ADR-007 — Composite tools orchestrate leaves server-side.** *Decision:* `analyze_ticker` /
`screen_market` run the pipeline inside the server. *Consequences:* clients get value in one call;
orchestration logic is centralised and versioned. *Related:* REQ-005.

**ADR-008 — Repository structure.** *Decision:* `skills/` (Agent Skills, Door 1), `mcp-server/`
(Door 2), `data-adapter/` (shared) in one repo. *Consequences:* single release train; clear
boundaries. *Open Decision #2:* split `mcp-server/` into its own repo later if needed. *Related:*
REQ-001, REQ-004, REQ-008.

---

## 3. Build Sequence

Ordered build units with dependencies (→ = depends on). Each maps to requirement(s) and ADR(s).

| Unit | Work | Requirements | Depends on | ADR |
|------|------|--------------|-----------|-----|
| **BU-1** | Push skills to default branch; pass `gh skill publish` | REQ-001 | — | ADR-008 |
| **BU-2** | Cut `v1.0.0`; enable immutable releases + tag protection | REQ-003 | BU-1 | ADR-006 |
| **BU-3** | Verify `gh skill install` on ≥2 hosts | REQ-002 | BU-1 | ADR-001 |
| **BU-4** | MCP server core: 14 tools, subprocess dispatch, schemas | REQ-004 | BU-1 | ADR-002, ADR-003 |
| **BU-5** | Data adapter: provider interface + file/DB + DSE provider | REQ-008 | BU-1 | ADR-004 |
| **BU-6** | `get_ticker_data` tool + CLI; caching/rate-limit/flags | REQ-009 | BU-5 | ADR-004 |
| **BU-7** | Composite tools `analyze_ticker`, `screen_market` | REQ-005 | BU-4, BU-6 | ADR-007 |
| **BU-8** | Packaging (npx/uvx + Docker) + dual transport | REQ-006, REQ-007 | BU-4 | ADR-005 |
| **BU-9** | CI on PR (compile, fixture tests, spec validate, server build) | REQ-010 | BU-1 | ADR-006 |
| **BU-10** | Supply-chain hardening (secret + code scanning) | REQ-012 | BU-1 | ADR-006 |
| **BU-11** | Release automation on tag (npm/PyPI, Docker, GH release, SBOM) | REQ-011 | BU-2, BU-8, BU-9 | ADR-006 |
| **BU-12** | Discoverability/docs + scope notice + sample data | REQ-013, REQ-014 | BU-2, BU-8 | ADR-001 |
| **BU-13** | Versioning/maintenance policy + CHANGELOG | REQ-015 | BU-2 | ADR-006 |
| **BU-14** | Periodic spec/host re-validation (scheduled) | REQ-016 | BU-12 | ADR-006 |

**Critical path:** BU-1 → BU-4 → (BU-6 →) BU-7 → BU-8 → BU-11.
**Parallelisable after BU-1:** BU-3, BU-5, BU-9, BU-10.
**Fast wins first:** BU-1, BU-2, BU-3 (Door 1 live), then BU-4–BU-8 (Door 2).

---

## 4. Coverage check

All 16 requirements are covered by ≥1 user story; all 16 user stories carry ≥2 acceptance
criteria (44 ACs total); every requirement maps to at least one Build Unit and one ADR. No
orphan requirements, stories, or ACs.
