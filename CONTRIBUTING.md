# Contributing to Sketch-to-CAD

Thank you for your interest in contributing to `sketch-to-cad`!

This project aims to make sketch-to-CAD transcription robust, transparent, and user-approved.

---

## Core Contribution Guidelines

1. **Preserve the User Approval Gate**:
   - Any modification to the workflow or skill must maintain the mandatory human approval gate before CAD drafting.
   - Never introduce automated drafting behaviors that bypass user confirmation of dimensional uncertainties.
2. **Preserve the Visual QA Phase**:
   - Vector geometry validation alone is insufficient. Visual preview inspection against the source sketch must remain a mandatory quality gate.
3. **No Machine-Specific Paths**:
   - Never commit files containing absolute file paths, local drive letters, or personal user directories.
4. **Adhere to Verified CADCraft Tool Schemas**:
   - Tools and commands must strictly conform to discovered CADCraft MCP capabilities as documented in `references/mcp-capabilities.md`.

---

## Development Workflow

1. Fork and clone the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature/my-feature-name
   ```
3. Make your changes in `skills/sketch-to-cad/`, `docs/`, or `tests/`.
4. Run the automated skill validator:
   ```powershell
   .\scripts\validate-skill.ps1
   ```
   Ensure all checks report `[PASSED]` with 0 failures.
5. Commit your changes with a descriptive message:
   ```bash
   git commit -m "feat(skill): improve door swing angle parameterization"
   ```
6. Push to your branch and open a Pull Request.
