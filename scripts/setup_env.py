#!/usr/bin/env python3
"""Create the project-local .venv and install development/viewer dependencies."""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"


def venv_python() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def run(*args: str) -> None:
    print("+", " ".join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    python = venv_python()

    if not python.exists():
        print(f"Creating virtual environment: {VENV_DIR}")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)
    else:
        print(f"Using existing virtual environment: {VENV_DIR}")

    run(str(python), "-m", "pip", "install", "--upgrade", "pip")
    run(str(python), "-m", "pip", "install", "-e", ".[dev,viewer]")

    print("\nEnvironment ready.")
    print(f"Python: {python}")
    print("In VS Code select .venv/bin/python if it is not selected automatically.")
    print("Then run task: RaceGOW: Live view (choose part)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
