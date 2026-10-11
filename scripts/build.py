#!/usr/bin/env python3
"""Build/check RaceGOW build123d parts and manufacturing files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
BUILD = ROOT / "build"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from racegow.config import CONFIG, OPTIONAL_PARTS, TRACK_BOM  # noqa: E402
from racegow.manufacturing import write_manufacturing_files  # noqa: E402


def require_build123d() -> None:
    try:
        import build123d  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "build123d is not installed. From the repository root run:\n"
            "  python -m venv .venv\n"
            "  .venv/bin/python -m pip install -e .[dev]\n"
            "On Windows use .venv\\Scripts\\python instead."
        ) from exc


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Build all geometry in memory and validate it; do not export CAD files.",
    )
    parser.add_argument(
        "--manufacturing-only",
        action="store_true",
        help="Write BOM/cut-list/manifest without importing build123d.",
    )
    parser.add_argument(
        "--with-cross",
        action="store_true",
        help="Also validate/export the optional horizontal cross connector.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Also export build/track_set_preview.step.",
    )
    parser.add_argument(
        "--no-step",
        action="store_true",
        help="Skip STEP exports and build STL only.",
    )
    parser.add_argument(
        "--no-stl",
        action="store_true",
        help="Skip STL exports and build STEP only.",
    )
    args = parser.parse_args()

    CONFIG.validate()
    write_manufacturing_files(BUILD, CONFIG)

    print(f"Gate CTC:       {CONFIG.gate_ctc:.2f} mm")
    print(f"PVC cut length: {CONFIG.pipe_cut_length:.2f} mm")
    print(f"Stock pipes:    {CONFIG.stocks_required}")
    print(f"Spare segments: {CONFIG.spares_if_full_stock_cut}")

    if args.manufacturing_only:
        print(f"Manufacturing files written to {BUILD}")
        return 0

    require_build123d()
    from racegow.connectors import connector_by_name, fit_array
    from racegow.exporting import (
        export_connector,
        export_fit_tests,
        export_preview,
        validate_shape,
    )

    names = list(TRACK_BOM)
    if args.with_cross:
        names.extend(OPTIONAL_PARTS)

    if args.check:
        for name in names:
            print(f"Checking {name} ...")
            validate_shape(name, connector_by_name(name, CONFIG))
        print("Checking fit_tests ...")
        validate_shape("fit_tests", fit_array(CONFIG))
        print("OK: all requested build123d geometries are valid.")
        return 0

    if args.no_step and args.no_stl:
        parser.error("--no-step and --no-stl together would export no CAD files")

    for name in names:
        print(f"Exporting {name} ...")
        export_connector(
            name,
            BUILD,
            CONFIG,
            stl=not args.no_stl,
            step=not args.no_step,
        )

    print("Exporting fit tests ...")
    export_fit_tests(
        BUILD,
        CONFIG,
        stl=not args.no_stl,
        step=not args.no_step,
    )

    if args.preview and not args.no_step:
        print("Exporting track-set preview STEP ...")
        export_preview(BUILD, CONFIG)

    print(f"Done. See {BUILD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
