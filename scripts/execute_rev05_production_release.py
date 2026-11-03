#!/usr/bin/env python3
"""
Production Release Pipeline Forwarder for Sketch-to-CAD Test 01.
Delegates to tests/real_world/Test-01/scripts/execute_rev06_production_release.py.
"""
import runpy
from pathlib import Path

target = Path(__file__).resolve().parent.parent / "tests" / "real_world" / "Test-01" / "scripts" / "execute_rev06_production_release.py"

if __name__ == "__main__":
    runpy.run_path(str(target), run_name="__main__")
