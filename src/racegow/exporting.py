"""Geometry validation and production export helpers."""

from __future__ import annotations

from pathlib import Path

from build123d import Compound, Part, export_step, export_stl

from .config import CONFIG, TrackConfig
from .connectors import connector_by_name, fit_array
from .track import track_set_preview


def validate_shape(name: str, shape: Part | Compound) -> None:
    if not shape.is_valid:
        raise RuntimeError(f"build123d/OCCT reports invalid geometry for {name}")
    solids = shape.solids()
    if not solids:
        raise RuntimeError(f"{name} contains no solids")
    for index, solid in enumerate(solids, start=1):
        if solid.volume <= 0:
            raise RuntimeError(f"{name} solid #{index} has non-positive volume")


def export_shape(
    shape: Part | Compound,
    stem: Path,
    cfg: TrackConfig = CONFIG,
    *,
    stl: bool = True,
    step: bool = True,
) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    validate_shape(stem.name, shape)

    if stl:
        export_stl(
            shape,
            stem.with_suffix(".stl"),
            tolerance=cfg.stl_tolerance,
            angular_tolerance=cfg.stl_angular_tolerance,
        )
    if step:
        export_step(shape, stem.with_suffix(".step"))


def export_connector(
    name: str,
    build_dir: Path,
    cfg: TrackConfig = CONFIG,
    *,
    stl: bool = True,
    step: bool = True,
) -> None:
    export_shape(
        connector_by_name(name, cfg),
        build_dir / name,
        cfg,
        stl=stl,
        step=step,
    )


def export_fit_tests(
    build_dir: Path,
    cfg: TrackConfig = CONFIG,
    *,
    stl: bool = True,
    step: bool = True,
) -> None:
    export_shape(
        fit_array(cfg),
        build_dir / "fit_tests",
        cfg,
        stl=stl,
        step=step,
    )


def export_preview(
    build_dir: Path,
    cfg: TrackConfig = CONFIG,
    *,
    step: bool = True,
) -> None:
    # Preview is an assembly/inspection aid and intentionally not an STL print plate.
    export_shape(
        track_set_preview(cfg),
        build_dir / "track_set_preview",
        cfg,
        stl=False,
        step=step,
    )
