---
description: Generate a WAIF web component from a Pipeline Descriptor JSON file
argument-hint: <path-to-descriptor.pipeline.json>
---

# Generate Pipeline Component: $ARGUMENTS

You are generating a complete WAIF web component from a Pipeline Descriptor JSON file. The descriptor defines a containerized AI pipeline's API contract, SSE events, data models, state machine, UI layout, and component configuration.

---

## CRITICAL: Pattern Compliance

Every generated component MUST follow the exact patterns established in the WAIF codebase. Before generating any code, read these reference files:

1. `src/components/wsd-hello-world/wsd-hello-world.ts` — Canonical component pattern
2. `src/components/wsd-hello-world/index.ts` — Barrel export pattern
3. `src/components/wsd-element/wsd-element.ts` — Base class
4. `src/events/event-types.ts` — Event detail interface pattern
5. `src/events/dispatch.ts` — Event dispatch pattern
6. `src/controllers/index.ts` — Available controllers

---

## Phase 1: Parse & Validate

1. Read the descriptor file at `$ARGUMENTS`
2. Validate required fields:
   - `pipeline.id` and `pipeline.name` — REQUIRED
   - `component.tagName` — REQUIRED, must match `^wsd-pipeline-[a-z][a-z0-9-]*$`
   - At least one of: `api[]`, `sse`, or `polling` — REQUIRED (component must connect to something)
3. Derive `className` from `tagName` if not provided:
   - `wsd-pipeline-summarizer` → `WsdPipelineSummarizer`
   - Strip `wsd-`, split on `-`, PascalCase each segment, prefix with `Wsd`
4. Validate controller constraints:
   - If `mode-switch` is in `controllers[]`, remove standalone `sse` and `polling` (mode-switch manages both internally)
   - If `sse` is defined but `sse` or `mode-switch` not in controllers, warn

---

## Phase 2: Generate Data Models

Create `src/components/{tagName}/types.ts`:

```typescript
/**
 * Type definitions for {pipeline.name} pipeline component.
 *
 * Auto-generated from pipeline descriptor: {pipeline.id} v{pipeline.version}
 * @module
 */

// For each model in descriptor.models[]:
export interface {model.name} {
  // For each field:
  /** {field.description} */
  {field.name}{field.optional ? '?' : ''}: {field.type};
}

// For each event in descriptor.component.events[]:
export interface {EventDetailName} {
  // Fields from the referenced detailType model
  // Plus: timestamp: number
}
```

Rules:
- Interface names are PascalCase from `model.name`
- Event detail interfaces get a `timestamp: number` field appended
- Event detail interface name = event name without `wsd:` prefix, PascalCase + `Detail` suffix
  - `wsd:pipeline-summarizer-submit` → `PipelineSummarizerSubmitDetail`
- If `detailType` references a model name, the event detail interface extends or mirrors that model with added `timestamp`

---

## Phase 3: Scaffold Component

Create `src/components/{tagName}/{tagName}.ts`:

### 3a. Imports

```typescript
import { html, css, nothing, type PropertyDeclarations } from 'lit';
import { WsdElement } from '../wsd-element/index.js';
import { dispatchWsdEvent } from '../../events/dispatch.js';

// Import controllers based on component.controllers[]:
// "api"                  → import { ApiController } from '../../controllers/api-controller.js';
// "sse"                  → import { SseController } from '../../controllers/sse-controller.js';
// "polling"              → import { PollingController } from '../../controllers/polling-controller.js';
// "mode-switch"          → import { ModeSwitchController } from '../../controllers/mode-switch-controller.js';
// "inline-error"         → import { InlineErrorController } from '../../controllers/inline-error-controller.js';
// "request-state"        → import { RequestStateController } from '../../controllers/request-state-controller.js';
// "debounced-interaction" → import { DebouncedInteractionController } from '../../controllers/debounced-interaction-controller.js';
// "lazy-loading"         → import { LazyLoadingController } from '../../controllers/lazy-loading-controller.js';

// Import types from local types.ts
import type { ...models, ...eventDetails } from './types.js';
```

### 3b. Class Declaration

```typescript
export class {className} extends WsdElement {
```

### 3c. Static Properties

```typescript
  static override properties: PropertyDeclarations = {
    // Pipeline state tracking
    pipelineStatus: { type: String },

    // From models: input data fields for forms
    // For each ui.section where type="input-form", add the section's fields as properties
    // e.g., if fields: ["text", "maxLength"], add:
    // _inputText: { type: String, attribute: false },
    // _inputMaxLength: { type: Number, attribute: false },

    // UI state
    _loading: { type: Boolean, attribute: false },
    _error: { type: String, attribute: false },

    // For tabbed layout:
    // _activeTab: { type: String, attribute: false },

    // Output data
    _result: { type: Object, attribute: false },

    // For SSE streaming:
    // _streamContent: { type: String, attribute: false },

    // For log-stream sections:
    // _logEntries: { type: Array, attribute: false },
  };
```

### 3d. Property Declarations and Constructor

```typescript
  // Declare all properties with types
  declare pipelineStatus: string;
  declare _loading: boolean;
  declare _error: string;
  // ... etc

  // Controller instances
  private _api!: ApiController;  // if "api" in controllers
  // ... etc

  constructor() {
    super();
    this.pipelineStatus = '{states.initial || "idle"}';
    this._loading = false;
    this._error = '';
    // Default values for all declared properties
  }
```

### 3e. Lifecycle — connectedCallback

```typescript
  override connectedCallback(): void {
    super.connectedCallback();

    // Instantiate controllers
    // For "api":
    this._api = new ApiController(this);

    // For "sse":
    this._sse = new SseController(this);

    // For "mode-switch":
    this._modeSwitch = new ModeSwitchController(this, {
      sseEndpoint: '{sse.endpoint}',
      pollingEndpoint: '{polling.endpoint}',
    });

    // For "request-state":
    this._requestState = new RequestStateController(this);

    // For "inline-error":
    this._inlineError = new InlineErrorController(this);
  }
```

### 3f. Styles — Layout-Specific CSS

Select the CSS template based on `ui.layout`:

**single-panel:**
```css
.container {
  display: flex;
  flex-direction: column;
  gap: var(--{tagName}-gap, var(--wsd-spacing-md, 16px));
}
```

**split-panel:**
```css
.container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto 1fr auto;
  gap: var(--{tagName}-gap, var(--wsd-spacing-md, 16px));
}
.section-top { grid-column: 1 / -1; }
.section-bottom { grid-column: 1 / -1; }
```

**tabbed:**
```css
.container {
  display: flex;
  flex-direction: column;
}
.tab-bar {
  display: flex;
  gap: var(--wsd-spacing-xs, 4px);
  border-bottom: 1px solid var(--wsd-border-color, #e0e0e0);
  padding: 0 var(--wsd-spacing-sm, 8px);
}
.tab-button {
  padding: var(--wsd-spacing-sm, 8px) var(--wsd-spacing-md, 16px);
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  font-family: inherit;
  font-size: var(--wsd-font-size-sm, 0.875rem);
  color: var(--wsd-color-text-muted, #6b7280);
}
.tab-button[active] {
  color: var(--wsd-color-primary, #3b82f6);
  border-bottom-color: var(--wsd-color-primary, #3b82f6);
}
.tab-content {
  display: none;
  padding: var(--wsd-spacing-md, 16px);
}
.tab-content[active] {
  display: block;
}
```

**dashboard-grid:**
```css
.container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "top top"
    "left right"
    "bottom bottom";
  gap: var(--{tagName}-grid-gap, var(--wsd-spacing-md, 16px));
}
.section-top { grid-area: top; }
.section-left { grid-area: left; }
.section-right { grid-area: right; }
.section-bottom { grid-area: bottom; }
```

**Common styles (all layouts):**
```css
:host {
  display: block;
  box-sizing: border-box;
}
.status-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--wsd-spacing-sm, 8px) var(--wsd-spacing-md, 16px);
  background: var(--wsd-color-surface-elevated, #f9fafb);
  border-radius: var(--wsd-radius-md, 8px);
}
.status-badge {
  display: inline-flex;
  padding: var(--wsd-spacing-2xs, 2px) var(--wsd-spacing-sm, 8px);
  border-radius: var(--wsd-radius-sm, 4px);
  font-size: var(--wsd-font-size-xs, 0.75rem);
  font-weight: var(--wsd-font-weight-medium, 500);
  text-transform: uppercase;
}
.status-badge[data-status="idle"] { background: var(--wsd-color-neutral-300, #d1d5db); color: var(--wsd-color-text, #1a1a1a); }
.status-badge[data-status="running"] { background: var(--wsd-color-info, #3b82f6); color: white; }
.status-badge[data-status="completed"] { background: var(--wsd-color-success, #22c55e); color: white; }
.status-badge[data-status="failed"] { background: var(--wsd-color-error, #ef4444); color: white; }
.progress-bar {
  width: 100%;
  height: 4px;
  background: var(--wsd-color-neutral-300, #d1d5db);
  border-radius: 2px;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  background: var(--wsd-color-primary, #3b82f6);
  transition: width 0.3s ease;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--wsd-spacing-xs, 4px);
}
.form-group label {
  font-size: var(--wsd-font-size-sm, 0.875rem);
  font-weight: var(--wsd-font-weight-medium, 500);
  color: var(--wsd-color-text, #1a1a1a);
}
.form-group input,
.form-group textarea,
.form-group select {
  padding: var(--wsd-spacing-sm, 8px);
  border: 1px solid var(--wsd-border-color, #e0e0e0);
  border-radius: var(--wsd-radius-sm, 4px);
  font-family: inherit;
  font-size: var(--wsd-font-size-md, 1rem);
}
.btn {
  padding: var(--wsd-spacing-sm, 8px) var(--wsd-spacing-md, 16px);
  background: var(--wsd-color-primary, #3b82f6);
  color: var(--wsd-color-on-primary, #ffffff);
  border: none;
  border-radius: var(--wsd-radius-sm, 4px);
  cursor: pointer;
  font-family: inherit;
  font-size: var(--wsd-font-size-md, 1rem);
}
.btn:hover { opacity: 0.9; }
.btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-danger {
  background: var(--wsd-color-error, #ef4444);
}
.output-area {
  padding: var(--wsd-spacing-md, 16px);
  background: var(--wsd-color-surface, #ffffff);
  border: 1px solid var(--wsd-border-color, #e0e0e0);
  border-radius: var(--wsd-radius-md, 8px);
  min-height: 100px;
  white-space: pre-wrap;
  font-family: var(--wsd-font-mono, monospace);
  font-size: var(--wsd-font-size-sm, 0.875rem);
}
.log-stream {
  max-height: 300px;
  overflow-y: auto;
  padding: var(--wsd-spacing-sm, 8px);
  background: var(--wsd-color-neutral-900, #111827);
  color: var(--wsd-color-neutral-100, #f3f4f6);
  border-radius: var(--wsd-radius-md, 8px);
  font-family: var(--wsd-font-mono, monospace);
  font-size: var(--wsd-font-size-xs, 0.75rem);
  line-height: var(--wsd-line-height-relaxed, 1.75);
}
.hidden { display: none !important; }
```

### 3g. Render Method

Build the `render()` method from `ui.sections[]`:

```typescript
  render() {
    return html`
      <div class="container" part="container">
        ${this._renderStatusHeader()}      <!-- if status-header section exists -->
        ${this._renderProgressBar()}       <!-- if progress section exists -->
        ${this._renderInputForm()}         <!-- if input-form section exists -->
        ${this._renderOutputDisplay()}     <!-- if output-display section exists -->
        ${this._renderLogStream()}         <!-- if log-stream section exists -->
        ${this._renderControls()}          <!-- if controls section exists -->
        <!-- slots from component.slots[] -->
        <slot name="footer"></slot>
      </div>
    `;
  }
```

For each section, create a private render method. Handle `visibleWhen` conditions:
- `"running"` → `this.pipelineStatus === 'running'`
- `"!idle"` → `this.pipelineStatus !== 'idle'`
- `"completed|failed"` → `['completed', 'failed'].includes(this.pipelineStatus)`

Use `nothing` from lit for conditional rendering:
```typescript
  private _renderProgressBar() {
    if (this.pipelineStatus !== 'running') return nothing;
    return html`<div class="progress-bar" part="progress-bar">...</div>`;
  }
```

### 3h. Section Render Templates

**status-header:**
```typescript
  private _renderStatusHeader() {
    return html`
      <div class="status-header section-top" part="header">
        <h3>${'{pipeline.name}'}</h3>
        <span class="status-badge" data-status=${this.pipelineStatus}>
          ${this.pipelineStatus}
        </span>
        <slot name="header-actions"></slot>
      </div>
    `;
  }
```

**input-form:**
```typescript
  private _renderInputForm() {
    return html`
      <form class="section-{placement}" part="{section.id}" @submit=${this._onFormSubmit}>
        <!-- For each field in section.fields[]: -->
        <div class="form-group">
          <label for="{field}">{field label}</label>
          <!-- string → <input type="text"> -->
          <!-- number → <input type="number"> -->
          <!-- File → <input type="file"> -->
          <!-- long text → <textarea> -->
          <input type="text" id="{field}" .value=${this._inputField} @input=${this._onFieldChange} />
        </div>
        <button class="btn" type="submit" ?disabled=${this._loading}>
          ${this._loading ? 'Processing...' : 'Submit'}
        </button>
      </form>
    `;
  }
```

**output-display:**
```typescript
  private _renderOutputDisplay() {
    if (/* visibleWhen check */) return nothing;
    return html`
      <div class="output-area section-{placement}" part="{section.id}">
        ${this._streamContent || this._result || 'No output yet.'}
      </div>
    `;
  }
```

**log-stream:**
```typescript
  private _renderLogStream() {
    return html`
      <div class="log-stream section-{placement}" part="{section.id}">
        ${this._logEntries.map(entry => html`
          <div class="log-entry">
            <span class="log-time">${new Date(entry.timestamp).toISOString()}</span>
            <span class="log-msg">${entry.message}</span>
          </div>
        `)}
      </div>
    `;
  }
```

**controls:**
```typescript
  private _renderControls() {
    if (/* visibleWhen check */) return nothing;
    return html`
      <div class="controls section-{placement}" part="controls">
        <!-- Buttons derived from api[] endpoints that aren't form triggers -->
        <button class="btn btn-danger" @click=${this._onCancel} ?disabled=${this.pipelineStatus !== 'running'}>
          Cancel
        </button>
      </div>
    `;
  }
```

**progress:**
```typescript
  private _renderProgressBar() {
    if (this.pipelineStatus !== 'running') return nothing;
    return html`
      <div class="progress-bar section-top" part="progress-bar">
        <div class="progress-bar-fill" style="width: ${this._progress}%"></div>
      </div>
    `;
  }
```

### 3i. API Methods

For each endpoint in `api[]`:
```typescript
  /** {endpoint.description} */
  private async _{endpoint.id}({params}): Promise<void> {
    try {
      this._loading = true;
      this._error = '';
      const response = await this._api.fetchJson('{endpoint.path}', {
        method: '{endpoint.method}',
        body: JSON.stringify({/* request body if POST/PUT/PATCH */}),
      });
      // Handle response based on endpoint type
      // Update pipelineStatus based on states.transitions
      // Dispatch success event if applicable
    } catch (err) {
      this._error = err instanceof Error ? err.message : 'Unknown error';
      dispatchWsdEvent(this, 'wsd:error', {
        detail: {
          message: this._error,
          code: 'API_ERROR',
          timestamp: Date.now(),
          source: '{tagName}',
        },
      });
    } finally {
      this._loading = false;
    }
  }
```

### 3j. SSE Event Handlers

If SSE is configured:
```typescript
  /** Connect to SSE stream */
  private _connectStream(): void {
    this._sse.connect('{sse.endpoint}');

    // For each event in sse.events[]:
    this._sse.subscribe('{event.type}', (data) => {
      // If isPipelineStatus: update pipelineStatus
      // If streaming content: append to _streamContent
      // If log event: push to _logEntries
      this.requestUpdate();
    });
  }

  override disconnectedCallback(): void {
    super.disconnectedCallback();
    this._sse?.disconnect();
  }
```

### 3k. Form Handlers

```typescript
  private _onFormSubmit(e: Event): void {
    e.preventDefault();
    // Collect form data from properties
    // Call the API method matching section.submitAction
    // Dispatch submit event
    const detail = { /* form data */, timestamp: Date.now() };
    dispatchWsdEvent(this, '{submit event name}', { detail });
  }
```

---

## Phase 4: Create Barrel Export

Create `src/components/{tagName}/index.ts`:

```typescript
/**
 * Barrel export for {className} pipeline component.
 *
 * Registers the `{tagName}` custom element and re-exports the
 * component class and types for typed usage.
 *
 * Auto-generated from pipeline descriptor: {pipeline.id} v{pipeline.version}
 * @module
 */

import { {className} } from './{tagName}.js';

customElements.define('{tagName}', {className});

export { {className} };
export type * from './types.js';
```

---

## Phase 5: Update Event Types

Edit `src/events/event-types.ts`:

1. **Append new detail interfaces** BEFORE the `WsdEventMap` interface:

```typescript
/**
 * Detail payload for `{event.name}` events.
 * Auto-generated from pipeline descriptor: {pipeline.id}
 */
export interface {EventDetailName} {
  // Fields from the referenced model
  timestamp: number;
}
```

2. **Add entries to `WsdEventMap`**:

```typescript
  '{event.name}': CustomEvent<{EventDetailName}>;
```

---

## Phase 6: Update Root Barrel

Edit `src/index.ts` — add after the last component export line:

```typescript
export { {className} } from './components/{tagName}/index.js';
```

---

## Phase 7: Update Dev Harness

Edit `dev/index.html` — append a new section BEFORE the closing `</body>` tag:

```html
    <!-- Pipeline: {pipeline.name} -->
    <h2>Pipeline: {pipeline.name}</h2>
    <div class="verification-steps">
      <h3>Manual Verification Steps</h3>
      <ol>
        <li>Verify component renders with {ui.layout} layout</li>
        <!-- For each section: -->
        <li>Verify {section.type} section "{section.label || section.id}" renders in {section.placement} position</li>
        <!-- For each API endpoint: -->
        <li>Verify {api.id} endpoint ({api.method} {api.path}) is callable</li>
        <!-- For SSE: -->
        <li>Verify SSE connection to {sse.endpoint} establishes and receives events</li>
        <!-- For each event: -->
        <li>Verify {event.name} event dispatches with correct detail type</li>
      </ol>
    </div>
    <{tagName}></{tagName}>
    <script type="module">
      import '../src/components/{tagName}/index.js';
    </script>
```

---

## Phase 8: Validate

1. Run `pnpm typecheck` to verify no TypeScript errors
2. Print a summary:

```
✓ Pipeline component generated: {pipeline.name}

Files created:
  - src/components/{tagName}/types.ts
  - src/components/{tagName}/{tagName}.ts
  - src/components/{tagName}/index.ts

Files modified:
  - src/events/event-types.ts (added {N} event detail interfaces + WsdEventMap entries)
  - src/index.ts (added barrel export)
  - dev/index.html (added harness section)

Component: <{tagName}>
Class: {className}
Controllers: {controllers.join(', ')}
Layout: {ui.layout}
Events: {events.map(e => e.name).join(', ')}
```

---

## Error Handling

- If the descriptor file doesn't exist, stop and report the error
- If `tagName` doesn't match the pattern, stop and explain the naming convention
- If a component directory already exists at `src/components/{tagName}/`, ask the user whether to overwrite
- If `pnpm typecheck` fails, attempt to fix the TypeScript errors and re-run (max 3 attempts)
