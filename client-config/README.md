# Client Configuration Templates

This directory contains configuration templates for various MCP clients.

## Claude Desktop

Copy the configuration to your Claude Desktop config directory:

```bash
# macOS
cp claude-desktop.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
# Copy to %APPDATA%\Claude\claude_desktop_config.json

# Linux
cp claude-desktop.json ~/.config/Claude/claude_desktop_config.json
```

Then update the `cwd` path to point to your local installation.

## Docker Deployment

For Docker deployment, clients can connect to the HTTP endpoint:

```json
{
  "mcpServers": {
    "stock-buddy": {
      "url": "http://localhost:8080/mcp"
    }
  }
}
```

## Environment Variables

- `STOCK_BUDDY_HTTP=1` - Enable HTTP transport (default for Docker)
- `STOCK_BUDDY_PORT=8080` - HTTP port (default: 8080)
- `STOCK_BUDDY_SKILLS_DIR` - Path to skills directory