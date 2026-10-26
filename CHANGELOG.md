# Changelog

All notable changes to the `sketch-to-cad` project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-10-26

### Added
- **Initial Public Preview Release** of the reusable `sketch-to-cad` skill for Google Antigravity.
- **7-Stage Quality Gate Workflow**:
  - `Sketch → Interpretation → User Approval → CAD Generation → Geometric Validation → Visual QA & Source Comparison → Final Deliverables`.
- **Mandatory User Approval Gate**:
  - Halts drafting until dimensional conflicts, room classifications, and layout assumptions are reviewed and approved by the user.
- **Structured Intermediate Model**:
  - JSON schema (`schemas/floor-plan-model.json`) defining the coordinate-based representation bridging sketch interpretation and CAD drafting.
- **CADCraft MCP Integration**:
  - Reference documentation and workflow guides for CADCraft CLI MCP server operations.
  - Layer assignment following AIA CAD standards (`A-WALL-EXTR`, `A-WALL-INTR`, `A-DOOR`, `A-GLAZ`, `A-ANNO-TEXT`, `A-ANNO-DIMS`).
  - Transverse jamb end-caps sealing double-wall cavities at door and window openings.
  - Readable architectural dimension styling with vertical dimension rotation.
- **Automated Tooling**:
  - `scripts/install.ps1`: Beginner-friendly PowerShell installer with workspace path resolution, existing installation detection, and dry-run mode.
  - `scripts/validate-skill.ps1`: Automated test validator for JSON schemas, relative links, and path safety checks.
- **Documentation**:
  - Comprehensive `README.md`, `installation.md`, `cadcraft-mcp-setup.md`, `workflow.md`, `troubleshooting.md`, and `limitations.md`.
  - Canonical studio apartment sample project in `examples/sample-project.md`.
