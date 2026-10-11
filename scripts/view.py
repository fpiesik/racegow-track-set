#!/usr/bin/env python3
"""Open a connector in the optional OCP VS Code viewer."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from racegow.config import CONFIG  # noqa: E402
from racegow.connectors import CONNECTOR_PORTS, connector_by_name, fit_array  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("part", choices=[*CONNECTOR_PORTS, "fit_tests"])
    args = parser.parse_args()

    try:
        from ocp_vscode import show
    except ImportError as exc:
        raise SystemExit(
            "ocp_vscode is not installed. Install viewer extras with:\n"
            "  python -m pip install -e .[viewer]"
        ) from exc

    model = fit_array(CONFIG) if args.part == "fit_tests" else connector_by_name(args.part, CONFIG)
    show(model, names=[args.part])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
