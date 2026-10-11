from __future__ import annotations

import math

from racegow.config import CONFIG, RACEGOW_MIN_CTC, TRACK_BOM, TrackConfig


def test_default_config_valid() -> None:
    CONFIG.validate()


def test_racegow_minimum_is_24_inch_ctc() -> None:
    assert math.isclose(RACEGOW_MIN_CTC, 609.6)


def test_stock_optimized_default() -> None:
    cfg = TrackConfig()
    assert math.isclose(cfg.gate_ctc, 690.3333333333334)
    assert math.isclose(cfg.pipe_cut_length, 665.3333333333334)
    assert cfg.pieces_per_stock == 3
    assert cfg.stocks_required == 7
    assert cfg.sections_if_full_stock_cut == 21
    assert cfg.spares_if_full_stock_cut == 1
    assert math.isclose(cfg.offcut_per_full_stock, 0.0, abs_tol=1e-9)


def test_manual_ctc_changes_cut_length_not_rule_semantics() -> None:
    cfg = TrackConfig(optimize_gate_for_stock=False, gate_ctc_manual=660)
    assert cfg.gate_ctc == 660
    assert cfg.pipe_cut_length == 635
    assert cfg.gate_ctc >= RACEGOW_MIN_CTC


def test_bom_matches_supplied_track_set() -> None:
    assert TRACK_BOM == {"elbow": 4, "tee": 6, "4way": 6, "5way": 2}
    assert sum(TRACK_BOM.values()) == 18
