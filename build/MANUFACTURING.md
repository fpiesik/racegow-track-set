# RaceGOW Manufacturing Plan

## Gate / PVC

- Gate size (Center-to-Center): **625.00 mm**
- RaceGOW minimum: **609.6 mm / 24 in CTC**
- Scale vs. 24 in minimum: **1.0253×**
- PVC cut length: **600.00 mm**
- Stock pipe: **2000 mm**
- Cutter kerf: **2.00 mm**
- Segments per stock pipe: **3**
- Stock pipes required: **7**
- Segments produced when fully cut: **21**
- Segments required: **20**
- Spare segments: **1**
- Offcut per fully used stock pipe: **196.00 mm**

## Connector fit

- PVC OD: **25.00 mm**
- Socket ID: **25.40 mm**
- Socket OD: **29.40 mm**
- Socket depth: **26.00 mm**
- Diametral clearance: **0.40 mm**

## Connector BOM

| Part | Quantity | STL/STEP export |
|---|---:|---|
| elbow | 4 | `build/elbow.stl`, `build/elbow.step` |
| tee | 6 | `build/tee.stl`, `build/tee.step` |
| 4way | 6 | `build/4way.stl`, `build/4way.step` |
| 5way | 2 | `build/5way.stl`, `build/5way.step` |

## Recommended production order

1. Print `fit_tests.stl` and choose the best real-world PVC clearance.
2. Update `diametral_clearance` in `src/racegow/config.py` if necessary.
3. Run `python scripts/build.py --check`.
4. Run `python scripts/build.py` to export production STL + STEP files.
5. Import each STL once into Bambu Studio and set its quantity from the BOM.
6. Cut the PVC using `CUT_LIST.csv`; keep the spare segment as replacement stock.
