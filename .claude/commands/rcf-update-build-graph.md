---
name: rcf-update-build-graph
description: Update the FBS status data and structure in the existing Build Sequence dependency graph. Syncs the HTML infographic with current RCF Build Sequence state.
---

# Update Build Sequence Graph

Update the existing Build Sequence dependency graph HTML file (`docs/build-sequence-graph.html`) to reflect the current state of the RCF Build Sequence. This command updates FBS statuses, and also detects any structural changes (new FBS entries, changed dependencies, tier reordering).

## Prerequisites

- The file `docs/build-sequence-graph.html` must already exist (created via `/rcf-create-build-graph`)
- You must have MCP access to the `rcf-tools` toolset connected to the `wsd-team-dev/wsd-ai-services-waif-components` repository

## Step 1: Connect and gather current state

1. Connect to the RCF project on `main` branch:
   - repo: `wsd-team-dev/wsd-ai-services-waif-components`
   - branch: `main`

2. Run `rcf_sync` with `force: true` to ensure the cache is fresh.

3. Query `rcf_build_sequence_query` with `type: parallel-opportunities` to get current tier groupings.

4. Query `rcf_build_sequence_query` with `type: critical-path` to get the current critical path.

5. View all Build Sequence parts to get current FBS statuses, titles, domains, and dependencies.

## Step 2: Read the existing HTML file

Read `docs/build-sequence-graph.html` and locate the three data sections by their markers:

```javascript
const FBS = [
  /*__FBS_DATA__*/
];

const CRIT = new Set([
  /*__CRIT_DATA__*/
]);

const TIERS = [
  /*__TIERS_DATA__*/
];
```

Note: After initial creation, the placeholder comments will have been replaced with actual data. The data sections are identified by `const FBS = [`, `const CRIT = new Set([`, and `const TIERS = [` respectively. Replace everything between the opening `[` and closing `]` (or `])` for CRIT).

## Step 3: Detect and apply changes

Compare the RCF data against the existing HTML data. Report what changed:

### Status changes

For each FBS where the RCF status differs from the HTML status, update the `s` field:

- `"not-started"` | `"in-progress"` | `"complete"`

### Structural changes

If any of these have changed, update the corresponding data:

- **New FBS entries added**: Add to the `FBS` array
- **FBS entries removed**: Remove from the `FBS` array
- **Dependencies changed**: Update `deps` arrays
- **Titles or domains changed**: Update `t` and `d` fields
- **Tier groupings changed**: Replace the `TIERS` array
- **Critical path changed**: Replace the `CRIT` set contents

## Step 4: Write the updated file

Write the modified HTML back to `docs/build-sequence-graph.html`.

## Step 5: Report summary

Report a change summary in this format:

```
Build Sequence Graph Updated
-----------------------------
Total FBS: {n}
Tiers: {n}
Critical path: {n} nodes

Status changes:
  - FBS-001: not-started -> in-progress
  - FBS-002: not-started -> complete
  (etc.)

Structural changes:
  - (list any added/removed FBS, dep changes, tier changes, or "None")

Progress: {complete}/{total} ({pct}%)
Buildable now: {n} FBS entries
```

## FBS data format reference

Each entry in the `FBS` array:

```javascript
{ id:"FBS-001", t:"Core LitElement Foundation", d:"Core Framework", deps:["FBS-106"], s:"not-started" }
```

| Field  | Type     | Description                                            |
| ------ | -------- | ------------------------------------------------------ |
| `id`   | string   | FBS identifier (e.g. `"FBS-001"`)                      |
| `t`    | string   | Short title, under ~30 chars                           |
| `d`    | string   | Domain, must match a key in the `DC` mapping object    |
| `deps` | string[] | Array of FBS IDs this entry depends on                 |
| `s`    | string   | One of: `"not-started"`, `"in-progress"`, `"complete"` |

## Important notes

- Do NOT modify the HTML template, CSS, or JavaScript logic. Only update the three data sections.
- Do NOT change edge drawing logic, layout constants, or interaction behaviour.
- If new domains appear that are not in the `DC` mapping object, add a new entry following the existing colour pattern and report it.
- The graph dynamically computes stats (completion %, buildable count) from the JSON data, so updating the data is sufficient.
