from __future__ import annotations

import csv
import json
from pathlib import Path

from racegow.config import CONFIG
from racegow.manufacturing import write_manufacturing_files


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
