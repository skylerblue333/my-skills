# stock-buddy-mcp

An MCP server that exposes the [Stock Buddy DSE analysis skills](../skills/README.md) as MCP
**tools**, so MCP clients (Claude Desktop, Cursor, IDE integrations, custom agents) can call them
without understanding the Agent Skills format. This is "Door 2" from the
[access plan](../skills/ACCESS_PLAN.md); coding agents can also consume the skills directly via
`gh skill` ("Door 1").

The server is a thin dispatcher: it shells out to each skill's stdlib-only Python CLI (JSON in /
JSON out) and returns the result. No analysis logic is duplicated. The skills need only the Python
standard library; the **server** needs the `mcp` package.

## Tools

- **14 skill tools** — `technical_analysis`, `momentum_screen`, `fundamental_analysis`,
  `value_investment_checklist`, `smart_money_flow`, `sentiment_news`, `macro_regime`,
  `signal_synthesizer`, `risk_manager`, `stock_screener`, `pattern_miner`, `daily_briefing`,
  `ticker_dossier`, `financial_terms_educator`.
- **2 composite tools** —
  - `analyze_ticker`: runs the leaf analyses → `signal_synthesizer` → `risk_manager` in one call.
  - `screen_market`: scans a universe for Investment/Momentum candidates.

Each tool accepts the [shared data-contract](../skills/README.md#shared-data-contract) object and
returns a Thinking Card (or, for composites, a bundle). Every output carries the
"Educational analysis only. Not financial advice." disclaimer.

## Install & run

```bash
# zero-install (recommended), from a checkout of the repo:
uvx --from ./mcp-server stock-buddy-mcp        # stdio transport

# or install into an environment:
pip install ./mcp-server
stock-buddy-mcp
```

The server locates the skills via `../skills` relative to the package, or the
`STOCK_BUDDY_SKILLS_DIR` env var if you install it elsewhere.

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "stock-buddy": {
      "command": "uvx",
      "args": ["--from", "/ABSOLUTE/PATH/TO/my-skills/mcp-server", "stock-buddy-mcp"],
      "env": { "STOCK_BUDDY_SKILLS_DIR": "/ABSOLUTE/PATH/TO/my-skills/skills" }
    }
  }
}
```

### Cursor / other stdio MCP clients

Same idea — command `uvx`, args `["--from", "<path>/mcp-server", "stock-buddy-mcp"]`,
env `STOCK_BUDDY_SKILLS_DIR`.

### HTTP transport (hosted/shared)

```bash
STOCK_BUDDY_HTTP=1 STOCK_BUDDY_PORT=8080 stock-buddy-mcp     # needs the [http] extra
# or via Docker (build from repo root so skills/ is in context):
docker build -f mcp-server/Dockerfile -t stock-buddy-mcp .
docker run -p 8080:8080 stock-buddy-mcp                       # serves MCP at /mcp
```

## Example tool calls

`technical_analysis` — pass the data-contract object:

```json
{ "ticker": "GP", "mode": "momentum", "ohlcv": [ {"date":"...","open":...,"high":...,"low":...,"close":...,"volume":...}, ... ] }
```

`analyze_ticker` — pass the full payload (ohlcv + fundamentals + shareholding + news + macro +
microstructure + account); the server runs the whole pipeline and returns `synthesis`, `risk`,
`agent_cards`, and per-stage status.

## Notes

- Skills are executable instructions; review them before use. Outputs are educational only.
- The server does **not** fetch market data — supply it in the payload (a future `get_ticker_data`
  tool / data adapter will close this gap; see the access plan).
