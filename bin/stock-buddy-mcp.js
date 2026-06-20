#!/usr/bin/env node
/**
 * Stock Buddy MCP Server Runner
 *
 * Starts the Python-based MCP server for Stock Buddy skills.
 * Can be run via: npx @stock-buddy/mcp-server
 */

const { spawn } = require('child_process');
const path = require('path');

// Parse arguments
const args = process.argv.slice(2);
const httpMode = args.includes('--http') || process.env.STOCK_BUDDY_HTTP === '1';
const port = process.env.STOCK_BUDDY_PORT || '8080';

console.log('Starting Stock Buddy MCP Server...');
if (httpMode) {
  console.log(`HTTP mode enabled on port ${port}`);
  process.env.STOCK_BUDDY_HTTP = '1';
  process.env.STOCK_BUDDY_PORT = port;
}

// Find the Python server
const serverPath = path.join(__dirname, '..', 'mcp-server');

// Start Python server
const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
const server = spawn(pythonCmd, ['-m', 'stock_buddy_mcp.server'], {
  cwd: serverPath,
  stdio: 'inherit',
  env: process.env
});

server.on('error', (err) => {
  console.error('Failed to start server:', err);
  console.error('Make sure Python 3.8+ is installed and dependencies are met.');
  console.error('Run: pip install -e mcp-server/');
  process.exit(1);
});

server.on('exit', (code) => {
  if (code !== 0) {
    console.error(`Server exited with code ${code}`);
  }
  process.exit(code);
});

// Handle signals
process.on('SIGINT', () => {
  server.kill('SIGINT');
});

process.on('SIGTERM', () => {
  server.kill('SIGTERM');
});