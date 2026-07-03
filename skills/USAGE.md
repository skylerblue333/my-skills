# Using these skills from an MCP client

This repository is a library of **Agent Skills** — self-contained capability folders that any
MCP client, agent runtime, or plain script can consume. This guide explains the three ways a
client uses them, the contract they all share, and a worked end-to-end example.

Nothing here is specific to one vendor: a skill is just a `SKILL.md` (instructions + metadata)
plus optional `scripts/`, `references/`, and `assets/`. A client decides *when* to use a skill
from its description and *how* to run it from its body.

## 1. Discovery — how a client finds the right skill

Every skill folder contains a `SKILL.md` whose YAML frontmatter carries a `name` and a
trigger-rich `description`:

```yaml
---
name: technical-analysis
description: Runs a DSE Technical Analysis Committee over a stock's OHLCV history and
  returns a weighted technical score, rating, and reasoning. Use when the user asks for
  technical analysis, RSI/MACD/ADX read, "is this stock bullish/bearish" ...
---
```

A client indexes these descriptions (the `name` + `description` are the only thing it needs to
load eagerly — the body and scripts load on demand). When a user request matches a description,
the client loads that skill's `SKILL.md` body for instructions, then runs the bundled script.
This is "progressive disclosure": metadata is cheap, full content loads only when relevant.

## 2. Integration — ways to run a skill

**Quickest path — `gh skill` (GitHub CLI v2.90.0+).** As of April 2026 the GitHub CLI can
discover and install Agent Skills directly from a repository, following the open
[agentskills.io](https://agentskills.io) spec these skills already conform to. A client
developer installs one skill — or browses the whole repo interactively — into the right
directory for their agent host automatically:

```sh
# browse this repo and install interactively
gh skill install skylerblue333/my-skills

# install a specific skill for a given host
gh skill install skylerblue333/my-skills technical-analysis --agent claude-code
gh skill install skylerblue333/my-skills risk-manager --agent cursor

# pin to a release tag or commit for reproducibility
gh skill install skylerblue333/my-skills signal-synthesizer --pin v1.0.0

# inspect before installing (skills are executable instructions — review them)
gh skill preview skylerblue333/my-skills momentum-screen

# keep installed skills current
gh skill update --all
```

Supported hosts include GitHub Copilot, Claude Code, Cursor, Codex, Gemini CLI, and Antigravity
(select with `--agent`). `gh skill` writes provenance metadata (repo, ref, tree SHA) into each
skill's `SKILL.md` frontmatter, so version tracking travels with the file. For maintainers,
`gh skill publish` validates the suite against the spec and can enable immutable releases and
tag pinning for supply-chain integrity — see [§8](#8-publishing-this-repo-maintainer).

The methods below are for hosts or pipelines that don't use `gh skill`.

**A. Agent Skills–aware host (zero glue).** Hosts that natively support Agent Skills (e.g.
Claude with the skills capability, or any runtime that scans skill folders) point at this repo,
read the frontmatter, and invoke skills automatically. Drop the repo into the host's skills
directory and the skills become available — no per-skill wiring.

**B. Wrap as an MCP server (recommended for shared infra).** Expose each skill (or the whole
suite) as MCP tools so multiple clients reach them over the MCP protocol. A thin server maps one
MCP tool per skill; each tool's input schema is the data contract below, and the handler shells
out to the skill's script. Sketch:

```python
# pseudo-MCP-server: one tool per skill
@tool("technical_analysis", input_schema=STOCK_INPUT_SCHEMA)
def technical_analysis(payload: dict) -> dict:
    proc = subprocess.run(
        ["python3", "skills/technical-analysis/scripts/analyze.py"],
        input=json.dumps(payload), capture_output=True, text=True)
    return json.loads(proc.stdout)
```

Clients (Claude Desktop, Cursor, custom agents) then call `technical_analysis` like any MCP
tool. Because every script speaks the same JSON in/out, the server is mostly a loop over folders.

**C. Direct CLI (no agent in the loop).** Each script is a stdlib-only Python 3.8+ CLI, so any
program or cron job can call it:

```bash
python3 skills/technical-analysis/scripts/analyze.py --input gp.json --pretty
cat gp.json | python3 skills/momentum-screen/scripts/screen.py
```

## 3. The shared data contract

Every analysis script reads **one JSON document** and writes **one JSON document**. The full
input shape (OHLCV bars, fundamentals, shareholding, news, macro, microstructure, account) is in
[README.md](README.md#shared-data-contract). The client's job is to assemble that JSON from
whatever data source it has (a DSE scraper, a database, an API) and to read back the structured
**Thinking Card**:

```json
{
  "skill": "technical-analysis", "ticker": "GP", "mode": "momentum",
  "score": 0.38, "confidence": 0.78, "rating": "bullish",
  "key_metrics": { "rsi_14": 58.3, "adx_14": 27.1 },
  "reasoning": ["RSI 58 — healthy", "ADX 27 — strong trend"],
  "flags": ["limited_history_<200_bars"],
  "disclaimer": "Educational analysis only. Not financial advice."
}
```

Same input → same output (deterministic), no network calls inside scripts, no third-party
packages. That portability is what lets a client treat the suite as a set of pure functions.

## 4. Composition — chaining skills into a pipeline

The skills are designed to compose. Leaf skills each emit a score; two skills combine them:

```
                technical-analysis ┐
                fundamental-analysis│
   per-ticker → smart-money-flow    ├─→ signal-synthesizer ─→ risk-manager ─→ ticker-dossier
                sentiment-news      │   (dual-mode signal,     (BDT sizing,    (one Markdown
                macro-regime       ┘    1–10 composite,        stop/target,     report)
                                        confluence rule)        risk gates)
```

A typical client flow for one ticker:

1. Run the leaf skills; collect their `score`/`confidence`.
2. Pass those into `signal-synthesizer` → Investment + Momentum signals with a 1–10 DSE
   Composite Score and confluence/stand-aside logic.
3. Feed the chosen signal + price data into `risk-manager` → buy zone, stop, target, position
   size in BDT, and pass/fail risk gates.
4. Optionally `ticker-dossier` to bundle all cards into one report.

Discovery-first skills run earlier: `stock-screener` scans the market for candidates;
`daily-briefing` runs on a schedule over a user's positions/watchlist;
`financial-terms-educator` explains any metric the others surface.

## 5. Worked example

```bash
# 1. leaf analyses (client supplies gp.json built from its data source)
tech=$(python3 skills/technical-analysis/scripts/analyze.py --input gp.json)
fund=$(python3 skills/fundamental-analysis/scripts/analyze.py --input gp.json)
flow=$(python3 skills/smart-money-flow/scripts/analyze.py --input gp.json)

# 2. fuse into a final call
echo "{\"ticker\":\"GP\",\"agents\":{
  \"technical\":$(echo $tech | jq '{score,confidence}'),
  \"fundamental\":$(echo $fund | jq '{score,confidence}'),
  \"smart_money\":$(echo $flow | jq '{score,confidence}')}}" \
  | python3 skills/signal-synthesizer/scripts/synthesize.py --pretty

# 3. size the trade
python3 skills/risk-manager/scripts/analyze.py --input gp.json --pretty
```

## 6. Requirements & guarantees

- **Runtime:** Python 3.8+ standard library only. No pip install, no network inside scripts.
- **Inputs:** the client provides market data — these skills *analyse*, they do not *fetch*.
- **Outputs:** structured JSON Thinking Cards; `flags` carry confidence penalties, never silent
  drops; every card ends with the educational-only disclaimer.
- **Scope:** educational analysis and signals only — never order execution or individualised
  advice; institutional-flow skills use public disclosure data only.

## 7. Per-skill reference

See [README.md](README.md#skill-index) for the full skill index, and each skill's own `SKILL.md`
(when to use, inputs read, output fields) and `references/` (formulas, criteria, methodology).

## 8. Publishing this repo (maintainer)

To make the suite installable via `gh skill install skylerblue333/my-skills`, the repo owner runs:

```sh
gh skill publish            # validate every SKILL.md against the agentskills.io spec
gh skill publish --fix      # auto-correct metadata issues in frontmatter
```

`publish` also checks recommended supply-chain settings (tag protection, secret scanning, code
scanning) and can enable **immutable releases**, so a published version can't be altered after
the fact — clients that pin with `--pin <tag>` are then fully protected. Cut a release tag
(e.g. `v1.0.0`) so clients can install and pin specific versions:

```sh
git tag v1.0.0 && git push origin v1.0.0
```

Note (from GitHub's announcement): skills are executable instructions and are **not** verified by
GitHub. Consumers should `gh skill preview` before installing; maintainers should keep releases
immutable and tags protected.
