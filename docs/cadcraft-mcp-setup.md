# CADCraft MCP Setup Guide

This guide explains how to connect CADCraft CLI as an MCP (Model Context Protocol) server to Google Antigravity so the `sketch-to-cad` skill can generate and inspect CAD drawings.

---

## 1. Prerequisites

1. **CADCraft**:
   - CADCraft is proprietary CAD software developed by CADCraft.
   - It is **not bundled** with this skill and must be installed separately from the official CADCraft provider.
   - Ensure the CADCraft CLI binary (`cadcraft-cli.exe` on Windows) is present on your system.
2. **Google Antigravity**:
   - Antigravity IDE / Agent runtime supporting MCP servers over standard I/O (stdio).

---

## 2. Configuration Template

Antigravity discovers MCP servers from either:
- **Workspace-level configuration**: `<your-workspace>/.agents/mcp_config.json` (Recommended for isolating projects)
- **Global configuration**: `%USERPROFILE%\.gemini\config\mcp_config.json`

### `mcp_config.json` Template

Create or update your `.agents/mcp_config.json` with the following configuration:

```json
{
  "mcpServers": {
    "cadcraft": {
      "command": "C:\\Path\\To\\CADCraft\\cadcraft-cli.exe",
      "args": ["mcp"]
    }
  }
}
```

> [!IMPORTANT]
> Replace `"C:\\Path\\To\\CADCraft\\cadcraft-cli.exe"` with the actual absolute path to `cadcraft-cli.exe` on your machine.
> On Windows, remember to escape backslashes (`\\`) in JSON strings.

---

## 3. Supported Connection Modes

CADCraft CLI supports two operational modes:

### Mode A: Headless Mode (Recommended)
```json
"args": ["mcp"]
```
- Launches an in-memory CADCraft drafting engine over stdio.
- Fastest, isolated, and ideal for automated agent workflows, batch generation, and tests.

### Mode B: Connected-App Mode (Interactive)
```json
"args": ["mcp", "--connect", "127.0.0.1:7979"]
```
- Connects to an already-running CADCraft desktop GUI application launched with:
  ```powershell
  cadcraft.exe --control 7979
  ```
- Allows you to see lines, arcs, and text being drafted live in the desktop CAD window.

---

## 4. Verification

To verify that Antigravity recognizes the CADCraft MCP server:
1. Restart your Antigravity IDE or refresh tools.
2. In the agent prompt, ask:
   > "List available CADCraft tools."
3. You should see discovered tools: `new_drawing`, `open`, `save`, `execute`, `command_line`, `script`, `inspect_drawing`, `query_entities`, `find_text`, `render`, `list_commands`, `cancel`.
