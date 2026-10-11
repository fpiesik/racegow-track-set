from __future__ import annotations

import pytest

pytest.importorskip("build123d")

from racegow.config import CONFIG
from racegow.connectors import CONNECTOR_PORTS, connector_by_name, fit_array


@pytest.mark.parametrize("name", list(CONNECTOR_PORTS))
def test_connector_geometry_is_valid(name: str) -> None:
    part = connector_by_name(name, CONFIG)
    assert part.is_valid
    assert len(part.solids()) >= 1
    assert all(solid.volume > 0 for solid in part.solids())


def test_fit_array_is_valid() -> None:
    model = fit_array(CONFIG)
    assert model.is_valid
    assert len(model.solids()) == len(CONFIG.fit_clearances)
