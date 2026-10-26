# Installation Guide

This guide walks you through setting up the `sketch-to-cad` skill in your Antigravity workspace.

---

## 1. Prerequisites

Before installing, ensure you have:
1. **Operating System**: Windows 10/11 (verified environment).
2. **AI Agent Platform**: Google Antigravity IDE / Agent runtime.
3. **CAD Backend**: CADCraft CLI v0.8+ installed separately.
4. **Shell**: PowerShell 5.1+ or PowerShell 7+.

---

## 2. Download the Repository

Clone or download the `sketch-to-cad` repository to your local computer:

```bash
git clone https://github.com/hasnizihar/sketch-to-cad.git
cd sketch-to-cad
```

---

## 3. Automated Installation (Recommended)

Run the included PowerShell installer. It will automatically detect your workspace or let you specify one:

```powershell
# Preview what will be installed without making changes:
.\scripts\install.ps1 -DryRun

# Install into a specific workspace:
.\scripts\install.ps1 -WorkspacePath "C:\Projects\MyArchitectureWorkspace"
```

The installer:
- Copies the skill files into `<workspace>/.agents/skills/sketch-to-cad/`.
- Detects if an existing installation exists and asks before overwriting.
- Leaves your existing workspace files and personal settings untouched.

---

## 4. Manual Installation (Alternative)

If you prefer to install manually:
1. Open your project workspace directory in File Explorer or terminal.
2. Ensure the directory `.agents/skills/` exists inside your workspace.
3. Copy the folder `skills/sketch-to-cad/` from this repository into:
   ```
   <your-workspace>/.agents/skills/sketch-to-cad/
   ```
4. Verify that `<your-workspace>/.agents/skills/sketch-to-cad/SKILL.md` is present.

---

## 5. Configure the CADCraft MCP Server

In your target workspace, open or create `.agents/mcp_config.json`:

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

Replace the command path with the location of `cadcraft-cli.exe` on your system.
For detailed instructions, refer to [`cadcraft-mcp-setup.md`](cadcraft-mcp-setup.md).

---

## 6. Restart & Verify

1. Restart your Antigravity session or reload customizations.
2. Verify that the skill is recognized by asking Antigravity:
   > "What skills do you have available?"
3. Antigravity will list `sketch-to-cad`. You are now ready to upload your first floor plan sketch!
