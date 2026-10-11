"""Manufacturing plan generation independent of the CAD backend."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from .config import CONFIG, RACEGOW_MIN_CTC, TRACK_BOM, TrackConfig


def plan_dict(cfg: TrackConfig = CONFIG) -> dict[str, object]:
    cfg.validate()
    return {
        "gate": {
            "ctc_mm": cfg.gate_ctc,
            "racegow_min_ctc_mm": RACEGOW_MIN_CTC,
            "scale_vs_24in": cfg.track_scale,
        },
        "pvc": {
            "pipe_od_mm": cfg.pipe_od,
            "pipe_cut_length_mm": cfg.pipe_cut_length,
            "stock_length_mm": cfg.stock_length,
            "cut_kerf_mm": cfg.cut_kerf,
            "pieces_per_stock": cfg.pieces_per_stock,
            "stock_pipes_required": cfg.stocks_required,
            "segments_required": cfg.track_sections_required,
            "segments_if_full_stock_cut": cfg.sections_if_full_stock_cut,
            "spare_segments": cfg.spares_if_full_stock_cut,
            "offcut_per_full_stock_mm": cfg.offcut_per_full_stock,
        },
        "connector": {
            "socket_id_mm": cfg.socket_id,
            "socket_od_mm": cfg.socket_od,
            "socket_depth_mm": cfg.socket_depth,
            "diametral_clearance_mm": cfg.diametral_clearance,
            "wall_thickness_mm": cfg.wall_thickness,
        },
        "bom": TRACK_BOM,
    }


def manufacturing_markdown(cfg: TrackConfig = CONFIG) -> str:
    p = plan_dict(cfg)
    gate = p["gate"]
    pvc = p["pvc"]
    connector = p["connector"]

    lines = [
        "# RaceGOW Manufacturing Plan",
        "",
        "## Gate / PVC",
        "",
        f"- Gate size (Center-to-Center): **{gate['ctc_mm']:.2f} mm**",
        f"- RaceGOW minimum: **{gate['racegow_min_ctc_mm']:.1f} mm / 24 in CTC**",
        f"- Scale vs. 24 in minimum: **{gate['scale_vs_24in']:.4f}×**",
        f"- PVC cut length: **{pvc['pipe_cut_length_mm']:.2f} mm**",
        f"- Stock pipe: **{pvc['stock_length_mm']:.0f} mm**",
        f"- Cutter kerf: **{pvc['cut_kerf_mm']:.2f} mm**",
        f"- Segments per stock pipe: **{pvc['pieces_per_stock']}**",
        f"- Stock pipes required: **{pvc['stock_pipes_required']}**",
        f"- Segments produced when fully cut: **{pvc['segments_if_full_stock_cut']}**",
        f"- Segments required: **{pvc['segments_required']}**",
        f"- Spare segments: **{pvc['spare_segments']}**",
        f"- Offcut per fully used stock pipe: **{pvc['offcut_per_full_stock_mm']:.2f} mm**",
        "",
        "## Connector fit",
        "",
        f"- PVC OD: **{cfg.pipe_od:.2f} mm**",
        f"- Socket ID: **{connector['socket_id_mm']:.2f} mm**",
        f"- Socket OD: **{connector['socket_od_mm']:.2f} mm**",
        f"- Socket depth: **{connector['socket_depth_mm']:.2f} mm**",
        f"- Diametral clearance: **{connector['diametral_clearance_mm']:.2f} mm**",
        "",
        "## Connector BOM",
        "",
        "| Part | Quantity | STL/STEP export |",
        "|---|---:|---|",
    ]
    for name, count in TRACK_BOM.items():
        lines.append(f"| {name} | {count} | `build/{name}.stl`, `build/{name}.step` |")

    lines += [
        "",
        "## Recommended production order",
        "",
        "1. Print `fit_tests.stl` and choose the best real-world PVC clearance.",
        "2. Update `diametral_clearance` in `src/racegow/config.py` if necessary.",
        "3. Run `python scripts/build.py --check`.",
        "4. Run `python scripts/build.py` to export production STL + STEP files.",
        "5. Import each STL once into Bambu Studio and set its quantity from the BOM.",
        "6. Cut the PVC using `CUT_LIST.csv`; keep the spare segment as replacement stock.",
        "",
    ]
    return "\n".join(lines)


def write_manufacturing_files(build_dir: Path, cfg: TrackConfig = CONFIG) -> None:
    build_dir.mkdir(parents=True, exist_ok=True)
    plan = plan_dict(cfg)

    (build_dir / "MANUFACTURING.md").write_text(
        manufacturing_markdown(cfg), encoding="utf-8"
    )
    (build_dir / "plan.json").write_text(
        json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    with (build_dir / "BOM.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["part", "quantity", "stl", "step"])
        for name, count in TRACK_BOM.items():
            writer.writerow([name, count, f"{name}.stl", f"{name}.step"])

    with (build_dir / "CUT_LIST.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "stock_pipe",
                "stock_length_mm",
                "pieces",
                "piece_length_mm",
                "kerf_mm",
                "offcut_mm",
            ]
        )
        for index in range(1, cfg.stocks_required + 1):
            writer.writerow(
                [
                    index,
                    f"{cfg.stock_length:.2f}",
                    cfg.pieces_per_stock,
                    f"{cfg.pipe_cut_length:.2f}",
                    f"{cfg.cut_kerf:.2f}",
                    f"{cfg.offcut_per_full_stock:.2f}",
                ]
            )

    # Useful for AI tooling and external scripts that want all raw user config.
    (build_dir / "config_snapshot.json").write_text(
        json.dumps(asdict(cfg), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
