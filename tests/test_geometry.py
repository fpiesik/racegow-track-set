from __future__ import annotations

from dataclasses import replace

import pytest

pytest.importorskip("build123d")

from racegow.config import CONFIG
from racegow.connectors import CONNECTOR_PORTS, connector_by_name, connector_raw, fit_array


@pytest.fixture(scope="module", params=[
    *((name, CONFIG) for name in CONNECTOR_PORTS),
    *((name, replace(CONFIG, diametral_clearanceXY=0.2, diametral_clearanceZ=0.8))
      for name in CONNECTOR_PORTS),
    ("5way", replace(CONFIG, diametral_clearanceXY=0.8, diametral_clearanceZ=0.2)),
])
def connector(request):
    name, cfg = request.param
    return name, connector_by_name(name, cfg), cfg


def test_connector_geometry_is_valid(connector) -> None:
    _, part, _ = connector
    assert part.is_valid
    assert len(part.solids()) == 1
    assert part.volume > 0
    assert part.bounding_box().min.Z == pytest.approx(0, abs=1e-6)
    assert any(face.geom_type.name == "PLANE" and abs(face.center().Z) < 1e-6
               for face in part.faces())


def test_socket_fit_stop_wall_and_lead_in_are_preserved(connector) -> None:
    name, part, cfg = connector
    z_shift = cfg.socket_od / 2 - cfg.bed_flat
    for port in CONNECTOR_PORTS[name]:
        socket_id = cfg.socket_id_z if port[0] == "z" else cfg.socket_id_xy
        axis = "xyz".index(port[0])
        sign = 1 if port[1] == "p" else -1
        radial_axis = (axis + 1) % 3

        def point(distance, radial=0):
            values = [0.0, 0.0, z_shift]
            values[axis] += sign * distance
            values[radial_axis] += radial
            return tuple(values)

        assert part.is_inside(point(cfg.pipe_stop_offset - 0.1))
        assert not part.is_inside(point(cfg.pipe_stop_offset + 0.1))
        socket_end = cfg.connector_arm_length - cfg.lead_in_depth - 1
        assert not part.is_inside(point(socket_end, socket_id / 2 - 0.1))
        assert part.is_inside(point(socket_end, socket_id / 2 + 0.1))
        assert part.is_inside(point(socket_end, cfg.socket_od / 2 - 0.1))
        assert not part.is_inside(point(socket_end, cfg.socket_od / 2 + 0.1))
        mouth = cfg.connector_arm_length - 0.1
        assert not part.is_inside(point(mouth, socket_id / 2 + 0.2))


@pytest.mark.parametrize("radius", [0.0, 1.0, 3.0])
def test_junction_radius_is_configurable(radius: float) -> None:
    cfg = replace(CONFIG, junction_fillet_radius=radius)
    cfg.validate()
    part = connector_by_name("5way", cfg)
    assert part.is_valid
    assert len(part.solids()) == 1


def test_junction_is_filleted_without_spherical_reinforcement() -> None:
    part = connector_raw(CONNECTOR_PORTS["tee"], CONFIG)
    sharp = connector_raw(
        CONNECTOR_PORTS["tee"], replace(CONFIG, junction_fillet_radius=0)
    )
    assert part.volume > sharp.volume + 1
    assert not any(face.geom_type.name == "SPHERE" for face in part.faces())


def test_port_order_and_duplicates_do_not_change_geometry() -> None:
    ports = CONNECTOR_PORTS["elbow"]
    expected = connector_raw(ports)
    reordered = connector_raw((*reversed(ports), ports[0]))
    assert reordered.is_valid
    assert reordered.volume == pytest.approx(expected.volume)


def test_fit_array_is_valid() -> None:
    model = fit_array(CONFIG)
    assert model.is_valid
    assert len(model.solids()) == len(CONFIG.fit_clearances)
