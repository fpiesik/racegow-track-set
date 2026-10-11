"""Central configuration and all derived RaceGOW/manufacturing dimensions."""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, floor

INCH = 25.4
RACEGOW_MIN_CTC = 24 * INCH

# RaceGOW basic connector BOM supplied for the track set.
TRACK_BOM: dict[str, int] = {
    "elbow": 4,
    "tee": 6,
    "4way": 6,
    "5way": 2,
}
OPTIONAL_PARTS: tuple[str, ...] = ("cross",)


@dataclass(frozen=True, slots=True)
class TrackConfig:
    """User-editable parameters.

    `gate_ctc` is the canonical track dimension and always means connector
    center-to-center. PVC cut length is derived from it and must never be
    hard-coded elsewhere.
    """

    # RaceGOW / track sizing
    optimize_gate_for_stock: bool = False
    gate_ctc_manual: float = 625.0

    # PVC / connector fit
    pipe_od: float = 25.0
    diametral_clearance: float = 0.40
    socket_depth: float = 26.0
    wall_thickness: float = 2
    pipe_stop_offset_override: float | None = None

    # Printable details
    lead_in_depth: float = 2.0
    lead_in_extra_diameter: float = 1.0
    bed_flat: float = 0.8
    boolean_overlap: float = 0.20

    # PVC stock / cutting
    stock_length: float = 2000.0
    cut_kerf: float = 2.0
    stock_target_pieces: int = 3
    track_sections_required: int = 20

    # Fit-test series
    fit_clearances: tuple[float, ...] = (0.20, 0.30, 0.40, 0.50, 0.60)
    fit_test_depth: float = 15.0
    fit_base_thickness: float = 3.0
    fit_spacing: float = 40.0

    # Preview/export settings
    preview_spacing_x: float = 115.0
    preview_spacing_y: float = 115.0
    stl_tolerance: float = 0.03
    stl_angular_tolerance: float = 0.10

    @property
    def pipe_stop_offset(self) -> float:
        return (
            self.pipe_od / 2
            if self.pipe_stop_offset_override is None
            else self.pipe_stop_offset_override
        )

    @property
    def socket_id(self) -> float:
        return self.pipe_od + self.diametral_clearance

    @property
    def socket_od(self) -> float:
        return self.socket_id + 2 * self.wall_thickness

    @property
    def connector_arm_length(self) -> float:
        return self.pipe_stop_offset + self.socket_depth

    @property
    def stock_optimized_pipe_length(self) -> float:
        return (
            self.stock_length - (self.stock_target_pieces - 1) * self.cut_kerf
        ) / self.stock_target_pieces

    @property
    def stock_optimized_gate_ctc(self) -> float:
        return self.stock_optimized_pipe_length + 2 * self.pipe_stop_offset

    @property
    def gate_ctc(self) -> float:
        return (
            self.stock_optimized_gate_ctc
            if self.optimize_gate_for_stock
            else self.gate_ctc_manual
        )

    @property
    def pipe_cut_length(self) -> float:
        return self.gate_ctc - 2 * self.pipe_stop_offset

    @property
    def pieces_per_stock(self) -> int:
        return floor(
            (self.stock_length + self.cut_kerf)
            / (self.pipe_cut_length + self.cut_kerf)
        )

    @property
    def stocks_required(self) -> int:
        return ceil(self.track_sections_required / self.pieces_per_stock)

    @property
    def sections_if_full_stock_cut(self) -> int:
        return self.stocks_required * self.pieces_per_stock

    @property
    def spares_if_full_stock_cut(self) -> int:
        return self.sections_if_full_stock_cut - self.track_sections_required

    @property
    def offcut_per_full_stock(self) -> float:
        return (
            self.stock_length
            - self.pieces_per_stock * self.pipe_cut_length
            - (self.pieces_per_stock - 1) * self.cut_kerf
        )

    @property
    def track_scale(self) -> float:
        return self.gate_ctc / RACEGOW_MIN_CTC

    def validate(self) -> None:
        if self.gate_ctc < RACEGOW_MIN_CTC:
            raise ValueError(
                f"gate_ctc must be >= {RACEGOW_MIN_CTC:.1f} mm (24 in CTC), "
                f"got {self.gate_ctc:.2f} mm"
            )
        if self.pipe_od <= 0:
            raise ValueError("pipe_od must be positive")
        if self.socket_depth <= 0 or self.wall_thickness <= 0:
            raise ValueError("socket_depth and wall_thickness must be positive")
        if self.diametral_clearance < 0:
            raise ValueError("diametral_clearance must not be negative")
        if self.lead_in_depth <= 0 or self.lead_in_depth > self.socket_depth:
            raise ValueError("lead_in_depth must be > 0 and <= socket_depth")
        if self.bed_flat < 0 or self.bed_flat >= self.socket_od / 2:
            raise ValueError("bed_flat must be >= 0 and smaller than socket radius")
        if self.stock_target_pieces < 1:
            raise ValueError("stock_target_pieces must be >= 1")
        if self.pieces_per_stock < 1:
            raise ValueError("configured gate is too large for the stock pipe")


CONFIG = TrackConfig()
