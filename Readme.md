# RaceGOW / Whoop Track Connector System

Parametric OpenSCAD models for connecting PVC pipes into a Whoop track. The
connector library contains elbows, tees, horizontal crosses, and connectors with
an additional upward-facing socket.

All dimensions are in millimeters. The model generates connectors and fit test
pieces; it reports pipe cutting quantities in the OpenSCAD console.

## Getting started

1. Open [raceGowParts.scad](raceGowParts.scad) in OpenSCAD.
2. In the `// OUTPUT` section, select a `mode` and, for single-part output, a `part`.
3. Adjust `pipe_od` to your measured pipe outside diameter and configure the
   socket clearances.
4. Preview the model, then render it before exporting an STL.
5. Import the STL into your slicer to prepare it for printing.

The SCAD file is self-contained and requires no external OpenSCAD libraries.

## Output modes

| `mode` | Output |
| --- | --- |
| `"single"` | One connector selected by `part`. |
| `"all_parts"` | One of each of the five connector types, including `cross`. |
| `"set_preview"` | All connectors in `track_set`, arranged by type and quantity. This is the default. |
| `"fit_array"` | A row of socket fit test pieces with different clearances. |

To render one of every connector type:

```scad
mode = "all_parts";
```

To export an individual connector:

```scad
mode = "single";
part = "5way";
```

`part` only affects `single` mode. `preview_spacing` controls the spacing in
`all_parts` and `set_preview`; `fit_spacing` controls the fit test spacing.

## Connector types and track set

| `part` | Socket arrangement | Default track set quantity |
| --- | --- | --- |
| `"elbow"` | Two horizontal sockets at 90 degrees. | 4 |
| `"tee"` | Three horizontal sockets forming a T. | 6 |
| `"cross"` | Four horizontal sockets. | 0 |
| `"4way"` | Three horizontal sockets and one upward socket. | 6 |
| `"5way"` | Four horizontal sockets and one upward socket. | 2 |

The default `track_set` contains 18 connectors. Edit that list to change the
quantities shown in `set_preview`. `all_parts` always includes all five library
types, independently of the track set.

For printing the track set, export each required connector type in `single` mode
and set its quantity in the slicer. The overview modes use fixed spacing, so
arrange the parts for your printer's build plate in the slicer.

## Pipe and socket parameters

| Parameter | Default | Meaning |
| --- | --- | --- |
| `pipe_od` | `25` | Measured outside diameter of the PVC pipe. |
| `diametral_clearanceXY` | `0.40` | Added diameter for horizontal sockets. |
| `diametral_clearanceZ` | `0.20` | Added diameter for vertical sockets. |
| `socket_depth` | `26` | Pipe insertion depth. |
| `wall_thickness` | `2` | Wall thickness used to size the socket exterior. |
| `pipe_stop_offset` | `pipe_od / 2` | Distance from the connector center to the pipe stop. |
| `lead_in_depth` | `2.0` | Length of the socket entrance chamfer. |
| `lead_in_extra_diameter` | `1.0` | Extra diameter at the socket entrance. |
| `bed_flat` | `0.8` | Amount flattened from the bottom for print bed contact. |
| `resolution` | `96` | Number of segments used for round geometry. |

Clearances are **diametral**, not radial. With the defaults, the socket bores are
25.40 mm horizontally and 25.20 mm vertically.

### Fit tests

Set `mode = "fit_array";` to generate upright test sockets for the values in
`fit_clearances`: `0.20`, `0.30`, `0.40`, `0.50`, and `0.60` mm by default. The
clearance increases along the X axis and is also printed in the console.

Each test bore is `pipe_od + clearance`, with a default test depth of 15 mm and
a 3 mm base. These pieces test vertical bores; check horizontal socket fit with
a connector printed in its intended orientation when tuning
`diametral_clearanceXY`.

## Gate dimensions and pipe cutting

`gate_ctc_manual` sets the distance between connector centers and defaults to
620 mm. The model enforces the configured `racegow_min_ctc` of 609.6 mm
(24 inches), as well as positive socket depth and wall thickness.

The pipe cut length is calculated as:

```text
pipe_cut_length = gate_ctc - 2 * pipe_stop_offset
```

With the defaults, each pipe section is **595 mm** long. The stock calculation
uses these settings:

| Parameter | Default | Meaning |
| --- | --- | --- |
| `stock_length` | `2000` | Length of one stock pipe. |
| `cut_kerf` | `2.0` | Saw kerf used in the cutting calculation. |
| `stock_target_pieces` | `3` | Target sections per stock pipe for automatic gate sizing. |
| `track_sections_required` | `20` | Number of pipe sections required. |
| `optimize_gate_for_stock` | `false` | Use the calculated stock-efficient gate size instead of `gate_ctc_manual`. |

The default calculation yields three sections per stock pipe and requires seven
stock pipes for 20 sections. Cutting all seven into three sections produces 21
sections, including one spare, with a calculated offcut of 211 mm per stock pipe.

With `optimize_gate_for_stock = true`, the gate center spacing becomes approximately
690.33 mm and the pipe cut length approximately 665.33 mm for the default stock
settings. This changes the cutting dimensions; the connector geometry remains
controlled by the pipe and socket parameters.

The console report includes the selected gate size, socket dimensions, pipe cut
length, stock quantities, spare sections, offcuts, and connector bill of materials.

## Command-line export

Run these examples from the project directory with `openscad` available on your
PATH. `-D` overrides the corresponding setting without editing the source file.

```sh
# Export one connector.
openscad -o elbow.stl -D 'mode="single"' -D 'part="elbow"' raceGowParts.scad

# Export one of each connector type.
openscad -o all_parts.stl -D 'mode="all_parts"' raceGowParts.scad

# Export the fit test pieces.
openscad -o fit_tests.stl -D 'mode="fit_array"' raceGowParts.scad
```
