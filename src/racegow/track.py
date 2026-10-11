"""Track-set assembly helpers."""

from __future__ import annotations

from build123d import Compound, Pos

from .config import CONFIG, TRACK_BOM, TrackConfig
from .connectors import connector_by_name


def track_set_preview(cfg: TrackConfig = CONFIG) -> Compound:
    """Create the complete connector BOM in rows for visual inspection.

    This is intentionally a preview/inspection assembly, not a printer-bed
    layout. Production exports remain one file per connector type so Bambu
    Studio can duplicate each object using the BOM quantities.
    """

    children = []
    for row, (name, count) in enumerate(TRACK_BOM.items()):
        for index in range(count):
            part = Pos(
                index * cfg.preview_spacing_x,
                row * cfg.preview_spacing_y,
                0,
            ) * connector_by_name(name, cfg)
            part.label = f"{name}_{index + 1:02d}"
            children.append(part)

    return Compound(label="RaceGOW_track_set", children=children)
