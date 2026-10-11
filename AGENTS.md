# AGENTS.md

Guidance for Codex / AI coding agents working on this build123d repository.

## Architecture

- `src/racegow/config.py`: all user-editable dimensions plus derived dimensions.
- `src/racegow/connectors.py`: reusable build123d geometry only.
- `src/racegow/track.py`: assemblies / set preview.
- `src/racegow/manufacturing.py`: BOM, cut plan, manifests; deliberately CAD-backend independent.
- `src/racegow/exporting.py`: build123d validation + STL/STEP export.
- `parts/`: tiny viewer wrappers, not geometry implementations.
- `scripts/build.py`: production entry point.
- `scripts/live_view.py`: save-triggered OCP CAD Viewer development loop.
- `scripts/setup_env.py`: reproducible project-local `.venv` bootstrap.

## Design rules

1. `gate_ctc` is canonical and always means **Center-to-Center**.
2. Never hard-code PVC cut length. It is `gate_ctc - 2 * pipe_stop_offset`.
3. Keep shared/user-editable parameters in `TrackConfig`.
4. Keep connector topology data in `CONNECTOR_PORTS`.
5. Port names are `xp`, `xn`, `yp`, `yn`, `zp`, `zn`.
6. `4way` = three horizontal ports + one `zp` port.
7. `5way` = four horizontal ports + one `zp` port.
8. `cross` = four horizontal ports; optional and not part of the default RaceGOW BOM.
9. Do not change the RaceGOW BOM unless source/rules are intentionally updated.
10. Prefer build123d Algebra mode and explicit transforms unless a feature is substantially clearer in Builder mode.
11. Preserve printable intent: pipe stop, lead-in taper, wall thickness, and bed flat are functional features.
12. STEP is the canonical editable CAD export; STL is the slicer export.

## Required validation after geometry changes

```bash
python scripts/build.py --check
python -m pytest
```

For production exports:

```bash
python scripts/build.py --preview
```

## Manufacturing intent

Default configuration optimizes the gate size for three equal PVC segments from a 2000 mm stock pipe while accounting for kerf. Minimum permitted gate size is 24 in / 609.6 mm CTC.

Before producing the complete set, print `build/fit_tests.stl`, validate the real pipe fit, and update `diametral_clearance` if necessary.

## Development loop

For geometry iteration, prefer the live viewer task or:

```bash
.venv/bin/python scripts/live_view.py 5way
```

Do not duplicate geometry in `parts/` or viewer scripts. Change shared CAD code
under `src/racegow/`, save, inspect the live result, then run the required
validation commands before considering the change complete.
