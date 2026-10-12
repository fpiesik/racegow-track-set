from __future__ import annotations

import math

import pytest

from racegow.config import CONFIG, RACEGOW_MIN_CTC, TRACK_BOM, TrackConfig


def test_default_config_valid() -> None:
    CONFIG.validate()


def test_separate_clearances_and_minimum_wall() -> None:
    cfg = TrackConfig(diametral_clearanceXY=0.2, diametral_clearanceZ=0.8)
    cfg.validate()
    assert cfg.socket_id_xy == pytest.approx(25.2)
    assert cfg.socket_id_z == pytest.approx(25.8)
    assert (cfg.socket_od - cfg.socket_id_xy) / 2 >= cfg.wall_thickness
    assert (cfg.socket_od - cfg.socket_id_z) / 2 >= cfg.wall_thickness


@pytest.mark.parametrize("name", ["diametral_clearanceXY", "diametral_clearanceZ"])
@pytest.mark.parametrize("value", [-0.1, math.nan, math.inf])
def test_invalid_clearances_are_rejected(name: str, value: float) -> None:
    with pytest.raises(ValueError, match=name):
        TrackConfig(**{name: value}).validate()


@pytest.mark.parametrize("radius", [-1.0, 100.0, math.nan])
def test_invalid_junction_fillet_radius_is_rejected(radius: float) -> None:
    with pytest.raises(ValueError, match="junction_fillet_radius"):
        TrackConfig(junction_fillet_radius=radius).validate()


def test_racegow_minimum_is_24_inch_ctc() -> None:
    assert math.isclose(RACEGOW_MIN_CTC, 609.6)


def test_stock_optimized_configuration() -> None:
    cfg = TrackConfig(optimize_gate_for_stock=True)
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
