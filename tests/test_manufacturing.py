from __future__ import annotations

import csv
import json
from dataclasses import replace
from pathlib import Path

from racegow.config import CONFIG
from racegow.manufacturing import plan_dict, manufacturing_markdown, write_manufacturing_files


def test_manufacturing_reports_both_clearances() -> None:
    cfg = replace(CONFIG, diametral_clearanceXY=0.2, diametral_clearanceZ=0.8)
    connector = plan_dict(cfg)["connector"]
    assert connector["diametral_clearance_xy_mm"] == 0.2
    assert connector["diametral_clearance_z_mm"] == 0.8
    assert connector["socket_id_xy_mm"] == 25.2
    assert connector["socket_id_z_mm"] == 25.8
    markdown = manufacturing_markdown(cfg)
    assert "Diametral clearance XY: **0.20 mm**" in markdown
    assert "Diametral clearance Z: **0.80 mm**" in markdown


def test_manufacturing_outputs(tmp_path: Path) -> None:
    write_manufacturing_files(tmp_path, CONFIG)

    for name in [
        "MANUFACTURING.md",
        "BOM.csv",
        "CUT_LIST.csv",
        "plan.json",
        "config_snapshot.json",
    ]:
        assert (tmp_path / name).exists()

    plan = json.loads((tmp_path / "plan.json").read_text(encoding="utf-8"))
    assert plan["pvc"]["segments_required"] == 20
    assert plan["pvc"]["spare_segments"] == 1

    with (tmp_path / "BOM.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert {row["part"] for row in rows} == {"elbow", "tee", "4way", "5way"}
