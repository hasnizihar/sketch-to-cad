# Troubleshooting Guide

This guide covers common issues, root causes, and recovery steps when running `sketch-to-cad`.

---

## 1. CADCraft MCP Server Issues

### Issue: "Tool 'new_drawing' failed or not found"
* **Cause**: Antigravity has not connected to the CADCraft MCP server.
* **Resolution**:
  1. Check `.agents/mcp_config.json` in your workspace.
  2. Verify that the command points to the exact path of `cadcraft-cli.exe`.
  3. Ensure backslashes are properly escaped (`C:\\Program Files\\...`).
  4. Test running `cadcraft-cli.exe mcp` directly in PowerShell to confirm it launches without errors.
  5. Restart Antigravity to reload MCP servers.

### Issue: "Connection refused: 127.0.0.1:7979"
* **Cause**: You configured CADCraft in connected-app mode (`--connect 127.0.0.1:7979`), but the CADCraft desktop application is not running with `--control 7979`.
* **Resolution**:
  - Launch CADCraft GUI with: `cadcraft.exe --control 7979` before invoking Antigravity.
  - Alternatively, switch to **Headless Mode** in `mcp_config.json` (`"args": ["mcp"]`).

---

## 2. Drawing & CAD Generation Issues

### Issue: "Dimension text is invisible or microscopic"
* **Cause**: The CAD dimension style used default imperial or millimeter text height (e.g. 2.5mm) on a large building envelope (e.g. 8000mm).
* **Resolution**:
  - Ensure the architectural dimension style `Arch` is active with `textHeight >= 150` and `arrowSize >= 120`.
  - Pass explicit text parameters to `dimlinear` calls.

### Issue: "Wall cavity appears open at door openings"
* **Cause**: Wall cutouts were drafted as interrupted parallel lines without transverse jamb end-caps.
* **Resolution**:
  - Insert perpendicular line segments across the wall thickness at each jamb on the host wall layer (`A-WALL-EXTR` or `A-WALL-INTR`).

### Issue: "Room name overlaps corridor walls"
* **Cause**: Single-line text string width exceeds narrow corridor clearance.
* **Resolution**:
  - Break long text strings into multiple lines (e.g., stacked centered lines with `height: 140`) to maintain clear margins.

---

## 3. Sketch Interpretation Issues

### Issue: "Conflicting handwritten dimensions"
* **Cause**: Rough sketches often contain arithmetic discrepancies (e.g. sum of interior rooms does not match overall exterior dimension).
* **Resolution**:
  - Review the agent's **Uncertainty Log** presented during Phase 3.
  - Explicitly instruct the agent which dimension to prioritize (e.g., "Option A: Lock overall building depth at 8700mm and adjust middle room to 3700mm").

### Issue: "Agent draws CAD geometry before I approved the plan"
* **Cause**: The prompt may have instructed the agent to skip interpretation.
* **Resolution**:
  - Reiterate the approval gate rule: *"Stop after Phase 1 / Phase 3. Wait for my explicit approval before generating any CAD."*
