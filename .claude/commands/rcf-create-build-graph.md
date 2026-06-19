---
name: rcf-create-build-graph
description: Generate the WAIF Build Sequence dependency graph infographic from current RCF Build Sequence data. Produces an interactive HTML file driven by embedded JSON.
---

# Create Build Sequence Graph

Generate the WAIF Build Sequence dependency graph infographic from the current RCF project data. The output is a self-contained interactive HTML file with embedded JSON that can be updated separately via `/rcf-update-build-graph`.

## Prerequisites

You must have MCP access to the `rcf-tools` toolset connected to the `wsd-team-dev/wsd-ai-services-waif-components` repository.

## Step 1: Connect and gather data

1. Connect to the RCF project on `main` branch:
   - repo: `wsd-team-dev/wsd-ai-services-waif-components`
   - branch: `main`

2. Query the Build Sequence for **parallel opportunities** (`rcf_build_sequence_query` with `type: parallel-opportunities`). This returns the tier groupings.

3. Query the **critical path** (`rcf_build_sequence_query` with `type: critical-path`). This returns the ordered list of FBS IDs on the longest dependency chain.

4. View **all Build Sequence parts** (`rcf_build_sequence_view` for each `bsId` from BS-001 through BS-011, plus any additional parts). From each part extract:
   - FBS ID
   - Title
   - Domain
   - Dependencies (the "Builds On" column)
   - Status

## Step 2: Build the JSON data structures

From the gathered data, construct three JavaScript data structures:

### FBS array

```javascript
const FBS = [
  { id: 'FBS-106', t: 'Project Scaffolding', d: 'Core Framework', deps: [], s: 'not-started' },
  {
    id: 'FBS-001',
    t: 'Core LitElement Foundation',
    d: 'Core Framework',
    deps: ['FBS-106'],
    s: 'not-started',
  },
  // ... one entry per FBS, ordered by ID
];
```

Fields:

- `id`: FBS ID string (e.g. `"FBS-001"`)
- `t`: Short title (keep under ~30 chars, abbreviate if needed)
- `d`: Domain string exactly as returned by RCF (e.g. `"Core Framework"`, `"API Controllers"`)
- `deps`: Array of FBS ID strings this entry depends on
- `s`: Status string, one of `"not-started"`, `"in-progress"`, `"complete"`

### CRIT set

```javascript
const CRIT = new Set(['FBS-106', 'FBS-003' /* ...all critical path IDs */]);
```

### TIERS array

```javascript
const TIERS = [
  ['FBS-106'], // T0
  ['FBS-001', 'FBS-002', 'FBS-003', 'FBS-091'], // T1
  // ... one sub-array per tier from parallel-opportunities
];
```

## Step 3: Generate the HTML file

Read the HTML template from `.claude/commands/build-sequence-template.html` in this repository (or from the project files).

In the template, find the three placeholder markers and replace them with the generated data:

- `/*__FBS_DATA__*/` -- replace with the full `FBS` array contents (the array items only, not the `const FBS =` wrapper)
- `/*__CRIT_DATA__*/` -- replace with the comma-separated list of critical path ID strings
- `/*__TIERS_DATA__*/` -- replace with the full `TIERS` array contents (the sub-arrays only, not the `const TIERS =` wrapper)

## Step 4: Write output

Save the generated HTML to `docs/build-sequence-graph.html` in the repository working directory.

Report a summary:

- Total FBS count
- Number of tiers
- Critical path length and IDs
- Number currently buildable (status not-started with all deps complete)
- Completion percentage

## Domain to CSS class mapping

The template uses these domain-to-class mappings. If new domains appear in the RCF data, add them to the `DC` object in the template following the same pattern:

| Domain                  | CSS Class |
| ----------------------- | --------- |
| Core Framework          | d-core    |
| Component Standards     | d-std     |
| Configuration System    | d-cfg     |
| Theming System          | d-thm     |
| Event System            | d-evt     |
| Package & Distribution  | d-pkg     |
| Testing Framework       | d-tst     |
| Internationalization    | d-i18     |
| CI/CD Pipeline          | d-ci      |
| API Controllers         | d-api     |
| Real-time Communication | d-rt      |
| Security & CORS         | d-sec     |
| Error Handling          | d-err     |
| Observability           | d-obs     |
| Documentation           | d-doc     |
| Performance             | d-prf     |

## Edge drawing logic

The template draws edges using a **primary dependency only** approach for the default view:

- Each node shows ONE arrow from its nearest-tier dependency (the dep with the highest tier index below its own tier)
- This produces a clean tree-like flow, not a wire diagram
- Clicking a node reveals ALL its actual dependencies (green) and dependents (purple)
- The critical path toggle shows only edges between critical path nodes (orange glow)

Do not change this logic. It is intentional.
