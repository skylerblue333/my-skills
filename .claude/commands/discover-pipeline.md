---
description: Discover pipeline API contract from source code and/or running container, generate a Pipeline Descriptor JSON
argument-hint: <pipeline-id> [--url http://localhost:4444] [--source /path/to/pipeline/repo]
---

# Discover Pipeline: $ARGUMENTS

You are discovering a pipeline's API contract by analyzing its source code and/or inspecting a running container instance. The goal is to auto-generate a Pipeline Descriptor JSON file that can be fed to `/generate-pipeline`.

---

## Parse Arguments

Parse `$ARGUMENTS` for:
- `pipeline-id` (required) — the pipeline identifier (e.g., `text-summarizer`, `translation`)
- `--url <url>` (optional) — URL of the running container (e.g., `http://localhost:4444`)
- `--source <path>` (optional) — local filesystem path to the pipeline source code

At least one of `--url` or `--source` must be provided.

---

## CRITICAL: Known WAIF Pipeline Server Architecture

The primary pipeline server lives at `/Users/kuntal/Developer/wsd-ai-services-waif`. If `--source` points there (or is omitted and the pipeline ID matches a known pipeline), use this knowledge:

### Server Architecture
- **Stack**: Node.js 24+, Express 5, TypeScript
- **Port**: 4444 (default)
- **API Version**: v1.0 (via `X-API-Version` header)
- **Base Path**: `/api/`

### API Endpoint Pattern
```
GET  /api/pipelines                                    — List all pipelines
GET  /api/pipelines/{pipelineId}                       — Pipeline versions
POST /api/pipelines/{id}/versions/{ver}/graphs/{graphId}/actions/execute        — Execute (multipart)
POST /api/pipelines/{id}/versions/{ver}/graphs/{graphId}/actions/execute/stream — Execute (SSE)
POST /api/pipelines/{id}/versions/{ver}/graphs/{graphId}/actions/execute/packets/{packetId} — Single packet
```

### SSE Event Types
```
connected, graph:start, node:start, stage:start, stage:end,
packet:added, packet:added:data, node:end, edge:decision,
graph:end, graph:error, service:history
```

### Pipeline Source Location
Each pipeline lives at: `src/api/v1.0/pipelines/{pipeline-id}/{version}/index.ts`

### Key Source Files
- Routes: `src/api/v1.0/routes/pipeline-graphs.router.ts`
- Pipeline class: `src/api/v1.0/pipelines/pipeline.ts`
- SSE utility: `src/utils/sse.response.ts`
- Registry: `src/api/v1.0/pipelines/registry.ts`
- Invocation context: `src/api/v1.0/pipelines/invocation-context.ts`

---

## Phase A: Source Code Analysis

If `--source` is provided:

### Step A1: Identify Pipeline Definition

Search the source for the pipeline's entry point:
```
Grep for: "pipeline-id" or the pipeline name in pipeline definition files
Look in: src/api/v1.0/pipelines/{pipeline-id}/ (for WAIF server)
         or scan for route definitions, pipeline configs, etc.
```

Read the pipeline's main file to understand:
- What **graphs** it defines (graph IDs, node structure)
- What **packets** it defines (input/output packet IDs and their media types)
- What **stages** it defines (stage handlers and their logic)

### Step A2: Extract Packet Definitions (→ API request/response shapes)

For each packet:
```
Grep for: packet definitions, media type configs, serializers/parsers
Extract: packet ID, accepted media types, data shape (from parsers/validators)
```

Map to descriptor format:
- Input packets → `api[].requestBody` fields
- Output packets → `api[].response` fields
- Media types → request Content-Type headers

### Step A3: Extract Graph Structure (→ API endpoints)

For each graph:
```
Read: graph node definitions, edges, conditions
Extract: graph ID, node order, stage sequence
```

Map to descriptor format:
- Each graph becomes an API execute endpoint: `POST /api/pipelines/{id}/versions/{ver}/graphs/{graphId}/actions/execute`
- Add streaming variant: `POST .../execute/stream`
- Add per-packet variants for output packets

### Step A4: Extract Stage Logic (→ State machine)

```
Read: stage handler functions
Look for: state transitions, status updates, metadata changes
Extract: execution phases (validate → prepare → execute → postprocess etc.)
```

Map to descriptor:
- Stage IDs → state values (or map to standard idle/running/completed/failed)
- Stage completion events → state transitions

### Step A5: Infer Data Models

```
Read: TypeScript interfaces, Zod schemas, type definitions in pipeline code
Look for: request validation, packet data types, response structures
Extract: field names, types, optional markers, descriptions
```

### Step A6: Detect SSE Events

```
Read: src/utils/sse.response.ts or equivalent
Look for: context.emit(), EventEmitter patterns, SSE event names
Extract: event type names, data payload shapes
```

---

## Phase B: Runtime Discovery

If `--url` is provided:

### Step B1: Fetch Pipeline Manifest

Use Bash to call the API:
```bash
curl -s {url}/api/pipelines/{pipeline-id} -H "X-API-Version: v1.0"
```

This returns available versions and metadata.

### Step B2: Fetch OpenAPI Spec (if available)

```bash
curl -s {url}/api/docs/openapi.json -H "X-API-Version: v1.0"
```

Parse the OpenAPI spec for:
- Endpoint paths, methods, parameters
- Request/response schemas
- Available operations

### Step B3: Interactive Network Capture (with MCP tools)

If Playwright or Chrome DevTools MCP is available, offer interactive discovery:

1. Navigate to the application UI (if it has one):
   ```
   mcp__playwright__browser_navigate({ url: "{url}" })
   ```
   or
   ```
   mcp__chrome-devtools__navigate_page({ url: "{url}" })
   ```

2. Capture network traffic while user interacts:
   ```
   mcp__chrome-devtools__list_network_requests({ resourceTypes: ["fetch", "xhr", "eventsource"] })
   ```

3. For each captured request, get details:
   ```
   mcp__chrome-devtools__get_network_request({ requestId: "..." })
   ```

4. Extract:
   - Request method, URL, headers, body
   - Response status, headers, body
   - SSE event streams (event types and data)

### Step B4: Test Endpoint Availability

For each discovered endpoint, verify it responds:
```bash
curl -s -o /dev/null -w "%{http_code}" {url}{endpoint} -H "X-API-Version: v1.0"
```

### Step B5: Capture SSE Events (if streaming endpoint exists)

```bash
timeout 5 curl -s -N -X POST {url}/api/pipelines/{id}/versions/default/graphs/{graphId}/actions/execute/stream \
  -H "Content-Type: multipart/form-data" \
  -H "X-API-Version: v1.0" \
  -F "input=@/dev/null;type=text/plain" 2>&1 | head -50
```

Parse the SSE output for event types and data shapes.

---

## Phase C: Merge & Generate

### Step C1: Cross-Reference Sources

If both source code and runtime data are available:
- Source code provides: complete type definitions, all endpoints (including unused), full state machine
- Runtime provides: actual data examples, response formats, which endpoints are active, real SSE event shapes
- **Prefer source code types** for model definitions (they're complete)
- **Prefer runtime data** for validating which endpoints are actually in use

### Step C2: Determine Component Configuration

Based on discovered pipeline characteristics, determine:

| Discovery | Maps To |
|-----------|---------|
| Has SSE streaming endpoint | `controllers: ["sse"]` or `["mode-switch"]` |
| Has REST-only endpoints | `controllers: ["api"]` |
| Has repeated polling patterns | `controllers: ["polling"]` |
| Multiple input packets | `ui.layout: "split-panel"` or `"tabbed"` |
| Single input/output | `ui.layout: "single-panel"` |
| Multiple graphs | `ui.layout: "tabbed"` (one tab per graph) |
| Batch/multi-job operations | `ui.layout: "dashboard-grid"` |

### Step C3: Generate Tag Name

Derive from pipeline ID:
```
{pipeline-id} → wsd-pipeline-{pipeline-id}
```

For multi-word IDs, keep kebab-case:
```
text-summarizer → wsd-pipeline-text-summarizer
doc-2-ibt → wsd-pipeline-doc-2-ibt
```

### Step C4: Build Draft Descriptor

Assemble the complete Pipeline Descriptor JSON following the schema at `schemas/pipeline-descriptor.schema.json`.

Mark fields by confidence:
- **High confidence** (confirmed by both sources or unambiguous from one): use directly
- **Medium confidence** (inferred from one source): include with a `"__NOTE__"` comment nearby
- **Needs manual input** (`__TODO__`): `tagName` customization, CSS parts, CSS custom properties, slot names

### Step C5: Write Descriptor File

Save to: `schemas/examples/{pipeline-id}.pipeline.json`

### Step C6: Present to User

Show the generated descriptor and ask for confirmation:

```
Pipeline Descriptor Generated: {pipeline.name}

Discovered:
  - {N} API endpoints ({methods})
  - {N} SSE event types
  - {N} data models
  - {N} state values
  - Suggested layout: {layout}
  - Suggested controllers: {controllers}

File saved to: schemas/examples/{pipeline-id}.pipeline.json

Items needing review:
  - [ ] Tag name: wsd-pipeline-{id} — adjust if needed
  - [ ] CSS parts — add component-specific part names
  - [ ] CSS custom properties — add overridable properties
  - [ ] Slot names — define content projection points
  - [ ] State transitions — verify correctness

Ready to generate component? Run:
  /generate-pipeline schemas/examples/{pipeline-id}.pipeline.json
```

---

## Error Handling

- If `--source` path doesn't exist, skip Phase A and rely on runtime only
- If `--url` is unreachable, skip Phase B and rely on source only
- If neither is available, stop and explain what's needed
- If the pipeline ID doesn't match any known pipeline in the source, list available pipelines and ask user to choose
- If OpenAPI spec isn't available, fall back to source code analysis or interactive capture
