"""build123d geometry for the RaceGOW connector family.

The model intentionally mirrors the earlier OpenSCAD design:
- cylindrical socket arms,
- a spherical center reinforcement,
- socket bores with a short lead-in taper,
- a small flat on the build-plate side.

Algebra mode keeps all transforms explicit, which makes the port topology easy
for both humans and coding agents to reason about.
"""

from __future__ import annotations

from collections.abc import Iterable

from build123d import Align, Box, Compound, Cone, Cylinder, Part, Pos, Rot, Sphere

from .config import CONFIG, TrackConfig

Direction = str

# A primitive is created along +Z and then rotated into the requested port.
_ROTATIONS: dict[Direction, tuple[float, float, float]] = {
    "xp": (0.0, 90.0, 0.0),
    "xn": (0.0, -90.0, 0.0),
    "yp": (-90.0, 0.0, 0.0),
    "yn": (90.0, 0.0, 0.0),
    "zp": (0.0, 0.0, 0.0),
    "zn": (180.0, 0.0, 0.0),
}

CONNECTOR_PORTS: dict[str, tuple[Direction, ...]] = {
    "elbow": ("xp", "yp"),
    "tee": ("xn", "xp", "yp"),
    "cross": ("xp", "xn", "yp", "yn"),
    # RaceGOW higher-direction connector: 3 horizontal + 1 vertical up.
    "4way": ("xp", "xn", "yp", "zp"),
    # 4 horizontal + 1 vertical up.
    "5way": ("xp", "xn", "yp", "yn", "zp"),
}

_ALIGN_Z_MIN = (Align.CENTER, Align.CENTER, Align.MIN)


def _orient(shape: Part, direction: Direction) -> Part:
    try:
        rotation = _ROTATIONS[direction]
    except KeyError as exc:
        raise ValueError(f"Unknown port direction: {direction!r}") from exc
    return Rot(*rotation) * shape


def _z_cylinder(radius: float, height: float, z0: float = 0.0) -> Part:
    return Pos(0, 0, z0) * Cylinder(
        radius=radius,
        height=height,
        align=_ALIGN_Z_MIN,
    )


def _outer_arm(direction: Direction, cfg: TrackConfig) -> Part:
    arm = _z_cylinder(cfg.socket_od / 2, cfg.connector_arm_length)
    return _orient(arm, direction)


def _socket_bore(direction: Direction, cfg: TrackConfig) -> Part:
    # Main cylindrical socket. The small overlap avoids coincident Boolean faces.
    main = _z_cylinder(
        cfg.socket_id / 2,
        cfg.socket_depth + cfg.boolean_overlap,
        cfg.pipe_stop_offset,
    )

    # The OpenSCAD lead-in used d1=socket_id and d2=socket_id+extra at the
    # outer opening. Cone reproduces that frustum exactly.
    lead_in = Pos(0, 0, cfg.connector_arm_length - cfg.lead_in_depth) * Cone(
        bottom_radius=cfg.socket_id / 2,
        top_radius=(cfg.socket_id + cfg.lead_in_extra_diameter) / 2,
        height=cfg.lead_in_depth + cfg.boolean_overlap,
        align=_ALIGN_Z_MIN,
    )

    return _orient(main + lead_in, direction)


def connector_raw(
    ports: Iterable[Direction],
    cfg: TrackConfig = CONFIG,
) -> Part:
    """Create an unshifted connector centered at the global origin."""

    ports = tuple(ports)
    if not ports:
        raise ValueError("A connector requires at least one port")

    for direction in ports:
        if direction not in _ROTATIONS:
            raise ValueError(f"Unknown port direction: {direction!r}")

    body: Part = Sphere(radius=cfg.socket_od / 2)
    for direction in ports:
        body = body + _outer_arm(direction, cfg)

    for direction in ports:
        body = body - _socket_bore(direction, cfg)

    return body


def connector_print_ready(
    ports: Iterable[Direction],
    cfg: TrackConfig = CONFIG,
) -> Part:
    """Move the connector above Z=0 and create the same small bed flat as SCAD."""

    body = Pos(0, 0, cfg.socket_od / 2 - cfg.bed_flat) * connector_raw(ports, cfg)

    # Remove all geometry below Z=0. Oversized cutter is deliberate and keeps
    # this operation independent from future connector arm lengths.
    cutter_size = max(2000.0, 20 * cfg.connector_arm_length)
    below_bed = Pos(0, 0, -cutter_size) * Box(
        cutter_size,
        cutter_size,
        cutter_size,
        align=_ALIGN_Z_MIN,
    )
    return body - below_bed


def connector_by_name(name: str, cfg: TrackConfig = CONFIG) -> Part:
    """Build one named connector."""

    try:
        ports = CONNECTOR_PORTS[name]
    except KeyError as exc:
        choices = ", ".join(CONNECTOR_PORTS)
        raise ValueError(f"Unknown connector {name!r}; choose one of: {choices}") from exc
    return connector_print_ready(ports, cfg)


def fit_test(clearance: float, cfg: TrackConfig = CONFIG) -> Part:
    """Small socket coupon for calibrating real PVC fit before the full set."""

    test_id = cfg.pipe_od + clearance
    test_od = test_id + 2 * cfg.wall_thickness
    total_height = cfg.fit_test_depth + cfg.fit_base_thickness

    outer = _z_cylinder(test_od / 2, total_height)
    bore = _z_cylinder(
        test_id / 2,
        cfg.fit_test_depth + cfg.boolean_overlap,
        cfg.fit_base_thickness,
    )
    lead_in = Pos(
        0,
        0,
        cfg.fit_base_thickness + cfg.fit_test_depth - cfg.lead_in_depth,
    ) * Cone(
        bottom_radius=test_id / 2,
        top_radius=(test_id + cfg.lead_in_extra_diameter) / 2,
        height=cfg.lead_in_depth + cfg.boolean_overlap,
        align=_ALIGN_Z_MIN,
    )
    result = outer - (bore + lead_in)
    result.label = f"fit_{clearance:.2f}mm"
    return result


def fit_array(cfg: TrackConfig = CONFIG) -> Compound:
    """All fit coupons in one spaced preview/export compound."""

    children = []
    for index, clearance in enumerate(cfg.fit_clearances):
        coupon = Pos(index * cfg.fit_spacing, 0, 0) * fit_test(clearance, cfg)
        coupon.label = f"fit_{clearance:.2f}mm"
        children.append(coupon)
    return Compound(label="fit_tests", children=children)
