# Access Plan — making the Stock Buddy skills consumable by MCP clients & coding agents

**Goal.** Take the 14 Agent Skills in this repo from "files on disk" to "installable, discoverable,
end-to-end usable" by (a) coding agents / skill-aware hosts and (b) MCP clients that speak tools
rather than skills.

**Key insight — two doors, not one.**

| Consumer | What it understands | Door |
|----------|--------------------|------|
| Coding agents / skill-aware hosts (Claude Code, Copilot, Cursor, Codex, Gemini, Antigravity) | Agent Skills (`SKILL.md` folders) | **Door 1:** `gh skill install` + Agent Skills spec |
| MCP clients (Claude Desktop, IDE MCP integrations, custom agents) | MCP servers exposing **tools** | **Door 2:** an MCP server wrapping each skill as a tool |
| Scripts / cron / backends | CLIs | **Door 3:** direct `python3 …` (already works) |

A third cross-cutting need sits under all of them: **the skills analyse but don't fetch** DSE data,
so anything end-to-end needs a **data adapter**.

Current state: 14 spec-shaped skills (`name` + `description` frontmatter, stdlib-only Python,
shared JSON contract), `README.md`, `USAGE.md`. Not yet on the remote default branch; no releases;
no MCP server; no data adapter; no CI.

---

## Phase 0 — Land & conform (prerequisite)

**Objective.** Get the suite onto `skylerblue333/my-skills` and passing the agentskills.io spec.

- Push `skills/` to the repo (PR via `push-skills.sh`) and merge to the default branch.
- Run `gh skill publish` (and `--fix`) to validate every `SKILL.md` against the spec; resolve any
  metadata nits it reports.
- Confirm each skill folder is self-contained (scripts + references; no cross-skill imports beyond
  the copied `indicators.py`).

**Deliverables:** skills on default branch; clean `gh skill publish` run.
**Acceptance:** `gh skill publish` reports 14 valid skills, 0 errors.

---

## Phase 1 — Door 1: publish for `gh skill` & skill-aware hosts

**Objective.** Anyone can `gh skill install skylerblue333/my-skills <skill> --agent <host>`.

- Cut a semver release tag (`v1.0.0`) and push it so versions are pinnable.
- Enable **immutable releases** + tag protection (offered by `gh skill publish`) for supply-chain
  integrity, so `--pin v1.0.0` is tamper-proof.
- Verify install on the priority hosts (at least Claude Code + one of Copilot/Cursor): install,
  confirm the skill triggers, run it.
- README: add an "Install" section with the `gh skill` one-liners (already drafted in `USAGE.md`).

**Deliverables:** `v1.0.0` release; verified installs on ≥2 hosts.
**Acceptance:** fresh machine installs a skill via `gh skill` and runs it against the fixture.

---

## Phase 2 — Door 2: the MCP server (the core new build)

**Objective.** MCP clients that don't understand Agent Skills can call the skills as MCP **tools**.

**Design.**
- One MCP server (`stock-buddy-mcp`) exposing **one tool per skill** (14 tools), names matching
  skill names (`technical_analysis`, `momentum_screen`, …).
- Each tool's `inputSchema` is the shared data contract subset that skill reads (documented per
  skill); the handler shells out to the skill's script (`subprocess`, JSON in/out) and returns the
  Thinking Card. Because every script already speaks the same JSON, the server is largely a loop
  over skill folders + a registry of which input fields each needs.
- Add 2 convenience composite tools: `analyze_ticker` (runs the leaf→synthesizer→risk pipeline in
  one call) and `screen_market` (wraps `stock-screener`), so clients get value without
  orchestrating 6 calls.
- Transport: stdio (for desktop/IDE clients) **and** streamable HTTP (for hosted/shared use).

**Packaging & distribution.**
- Ship as runnable with **no install** via `npx stock-buddy-mcp` (Node wrapper) or `uvx`
  (Python) — the lowest-friction path for MCP client config.
- Provide a `Dockerfile` for hosted deployment.
- Provide copy-paste client config blocks for Claude Desktop (`claude_desktop_config.json`),
  Cursor, and generic MCP clients (command + args + env).

**Repo layout (proposed):**
```
my-skills/
  skills/                 # the 14 Agent Skills (Door 1)
  mcp-server/             # the MCP wrapper (Door 2)
    src/ … , package.json / pyproject.toml, Dockerfile, README
```

**Deliverables:** published MCP server (npx/uvx + Docker), client config snippets, 16 tools.
**Acceptance:** Claude Desktop (or MCP Inspector) lists the tools, and `analyze_ticker` returns a
valid dual-mode signal for the fixture.

---

## Phase 3 — Close the data gap: the DSE data adapter

**Objective.** Make the skills usable end-to-end without the caller hand-building JSON.

- Add a `data-adapter` component that produces the shared input contract (OHLCV, fundamentals,
  shareholding, news, macro, microstructure) for a ticker, from a configurable source.
- v1: pluggable provider interface + a CSV/JSON file provider and a thin DSE source (per the PRD's
  polite, throttled scraping of dsebd.org/dse.com.bd, robots-aware, cached). Keep the network code
  **out of the skills** — the adapter is a separate layer the MCP server / agents call first.
- Expose as: an MCP tool `get_ticker_data(ticker)` and a CLI, so both doors can fetch then analyse.
- Respect PRD constraints: public data only, caching, rate limiting, data-quality flags rather than
  silent drops.

**Deliverables:** `data-adapter` with ≥1 working provider; `get_ticker_data` tool + CLI.
**Acceptance:** `get_ticker_data("GP") | analyze_ticker` runs with no hand-authored JSON.

> Decision needed: real DSE scraping now, or ship the file/DB provider first and add scraping
> later? (Scraping has legal/ToS and reliability considerations.)

---

## Phase 4 — CI/CD & supply-chain hardening

**Objective.** Every change is validated and releases are trustworthy.

- GitHub Actions on PR: (1) lint/`py_compile` all scripts, (2) run each script against
  `_fixtures/sample_input.json` and assert valid JSON + required Thinking-Card fields,
  (3) `gh skill publish` spec validation, (4) build the MCP server.
- Release workflow on tag: build/publish the MCP package (npm/PyPI) + Docker image; create the
  GitHub release (immutable); attach provenance/SBOM.
- Enable secret scanning + code scanning (also nudged by `gh skill publish`).

**Deliverables:** `ci.yml`, `release.yml`, green checks on PRs.
**Acceptance:** a PR that breaks a script's JSON output fails CI; tagging `vX.Y.Z` publishes
artifacts automatically.

---

## Phase 5 — Discoverability & documentation

**Objective.** People (and agents) can find and adopt the suite.

- Top-level README: what it is, install (both doors), the pipeline diagram, links to `USAGE.md`.
- Per-skill quickstart snippets and a sample `gp.json` users can copy.
- List the repo where skills are discovered: agentskills.io / `gh skill search`, and (optionally)
  an MCP registry listing for the server so MCP clients surface it.
- A short "security & scope" note (educational only; public data; review before install).

**Deliverables:** polished README, sample data, registry/listing entries.
**Acceptance:** `gh skill search` surfaces the repo; MCP registry shows the server (if listed).

---

## Phase 6 — Versioning & maintenance (ongoing)

- Semver per release; keep skill `metadata.version` in step with `gh skill` provenance (repo, ref,
  tree SHA written to frontmatter).
- Changelog; deprecation policy; pin-friendly tags so consumers upgrade deliberately.
- Periodic re-validation against the evolving agentskills.io spec and host `--agent` targets.

---

## Distribution matrix (target end state)

| Consumer | How they get the skills |
|----------|-------------------------|
| Claude Code / Copilot / Cursor / Codex / Gemini / Antigravity | `gh skill install skylerblue333/my-skills <skill> --agent <host>` |
| Claude Desktop & MCP-tool clients | Add `stock-buddy-mcp` server (npx/uvx/Docker) → tools appear |
| Custom agents / LangChain-style runtimes | Call the MCP server, or shell the CLIs |
| Backends / cron / notebooks | Direct `python3 skills/<skill>/scripts/*.py` |

## Sequencing & effort (rough)

1. **Phase 0–1** (push, publish, release) — small, do first; unlocks Door 1 immediately.
2. **Phase 2** (MCP server) — medium; unlocks Door 2, highest leverage for "MCP clients".
3. **Phase 4** (CI) — small/medium; run in parallel with Phase 2.
4. **Phase 3** (data adapter) — medium/large; makes everything end-to-end.
5. **Phase 5–6** — ongoing.

## Open decisions for you

1. **MCP server language** — Node (`npx`, broadest MCP-client familiarity) or Python (`uvx`,
   matches the skills' runtime so no second toolchain)?
2. **Same repo or separate** — keep `mcp-server/` and `data-adapter/` inside `my-skills`, or split
   the server into its own repo?
3. **Data source for Phase 3** — file/DB provider first, or invest in DSE scraping now?
4. **Composite tools** — include `analyze_ticker` / `screen_market` conveniences (recommended), or
   expose only the raw 14?

Tell me your picks on 1–4 and I'll start executing (Phase 0–2 are the fast wins). I can scaffold
the MCP server and CI next.
