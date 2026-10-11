#!/usr/bin/env python3
"""Live-reload a RaceGOW model into OCP CAD Viewer on Python file saves.

The watcher stays running while a fresh child process rebuilds the model after
changes. Rebuilding in a new process avoids stale Python modules during CAD
iteration and keeps the OCP viewer camera stable between show() calls.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Keeping this import in the file also matches OCP CAD Viewer's default
# autostart trigger when the file is opened in VS Code.
from ocp_vscode import Camera, show  # noqa: E402
from watchfiles import PythonFilter, run_process  # noqa: E402

from racegow.connectors import CONNECTOR_PORTS  # noqa: E402


PART_CHOICES = [*CONNECTOR_PORTS, "fit_tests"]


def render(part: str) -> None:
    """Build one model in a fresh process and send it to OCP CAD Viewer."""

    # Imports happen here deliberately. run_process starts render() in a fresh
    # child process after every save, so modified CAD modules are re-imported
    # from disk rather than relying on fragile importlib.reload chains.
    from racegow.config import CONFIG
    from racegow.connectors import connector_by_name, fit_array

    model = fit_array(CONFIG) if part == "fit_tests" else connector_by_name(part, CONFIG)
    show(model, names=[part], reset_camera=Camera.KEEP)
    print(f"[RaceGOW live] rendered {part}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild a RaceGOW connector automatically when Python files are saved."
    )
    parser.add_argument("part", choices=PART_CHOICES)
    parser.add_argument(
        "--debounce",
        type=int,
        default=300,
        help="Milliseconds to group rapid file-save events (default: 300).",
    )
    args = parser.parse_args()

    watch_paths = [SRC, ROOT / "scripts"]
    print(
        "[RaceGOW live] watching src/ and scripts/; "
        f"part={args.part}. Stop with Ctrl+C.",
        flush=True,
    )

    run_process(
        *watch_paths,
        target=render,
        args=(args.part,),
        watch_filter=PythonFilter(),
        debounce=args.debounce,
        grace_period=0,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
