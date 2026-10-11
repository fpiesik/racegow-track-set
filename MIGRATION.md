# OpenSCAD → build123d migration map

This port preserves the original design intent while making the CAD backend a Python/BREP model.

| OpenSCAD project | build123d project | Notes |
|---|---|---|
| `config.scad` | `src/racegow/config.py` | `TrackConfig` plus derived properties; CTC remains canonical. |
| `connectors.scad` | `src/racegow/connectors.py` | Generic port-driven connector generator in algebra mode. |
| `track_set.scad` | `src/racegow/track.py` | Complete BOM preview as a labeled `Compound`. |
| `fit_tests.scad` | `fit_array()` | Same 0.20–0.60 mm clearance series. |
| `parts/*.scad` | `parts/*.py` | Thin viewer wrappers; geometry stays centralized. |
| `scripts/build.py` | `scripts/build.py` | No SCAD parsing; configuration is imported directly as Python. |
| STL only | STL + STEP | STEP is now generated for editable BREP interchange. |

## Geometry equivalence

The connector construction is deliberately the same at the feature level:

1. Start with a spherical center reinforcement of diameter `socket_od`.
2. Add one cylindrical outer arm for every port.
3. Subtract a cylindrical socket bore beginning at `pipe_stop_offset`.
4. Subtract a short conical lead-in at the outer socket opening.
5. Translate the connector upward and cut below Z=0 to create `bed_flat`.

The port sets are unchanged:

```text
elbow : xp yp
tee   : xn xp yp
cross : xp xn yp yn
4way  : xp xn yp zp
5way  : xp xn yp yn zp
```

## Intentional improvements

- Derived dimensions are Python properties instead of duplicated expressions.
- Manufacturing logic is CAD-backend independent and directly testable.
- `BOM.csv`, `CUT_LIST.csv`, `plan.json`, and `config_snapshot.json` are generated automatically.
- Production exports include STEP as well as STL.
- Geometry validation uses build123d/OpenCascade `is_valid` once build123d is installed.
- Tests lock down CTC, cut lengths, stock utilization, BOM, and manufacturing outputs.

## First comparison to make after installing dependencies

Run:

```bash
python scripts/build.py --check
python scripts/build.py --with-cross --preview
```

Then compare the resulting build123d STL against the former OpenSCAD STL in your slicer. The most important functional comparison is the real PVC fit; print the new `fit_tests.stl` before the complete connector set.
