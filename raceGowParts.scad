// ============================================================
// RaceGOW / Whoop Track Connector System
// Parametric connector system for PVC pipes
// ============================================================


// ------------------------------------------------------------
// OUTPUT
// ------------------------------------------------------------

// "single"      = one part
// "all_parts"   = one part of each connector type
// "set_preview" = complete track set overview
// "fit_array"   = multiple fit test pieces

mode = "set_preview";

// "elbow"
// "tee"
// "cross"   -> four horizontal ports
// "4way"    -> three horizontal ports + one upward
// "5way"    -> four horizontal ports + one upward

part = "5way";


// ============================================================
// RACEGOW / TRACK GEOMETRY
// ============================================================

inch = 25.4;

racegow_min_ctc = 24 * inch;   // 609.6 mm


// Desired gate size CENTER TO CENTER.
//
// This is the key track dimension.
// All track dimensions are based on this value.

gate_ctc_manual = 620;


// Optional:
// Automatically choose the gate size to use your 2 m pipes
// as efficiently as possible.

optimize_gate_for_stock = false;


// ============================================================
// PVC
// ============================================================

// Measured outside diameter
pipe_od = 25;

// Clearance between pipe and socket, configurable by bore direction
diametral_clearanceXY = 0.40;
diametral_clearanceZ = 0.20;

// Insertion depth
socket_depth = 26;

// Wall thickness
wall_thickness = 2;


// Distance from the connector's geometric center
// to the PVC pipe stop.
//
// At pipe_od / 2, the pipe stop is one pipe radius
// from the center.

pipe_stop_offset = pipe_od / 2;


// ============================================================
// PRINTING / FIT
// ============================================================

// Small lead-in chamfer on each pipe socket

lead_in_depth = 2.0;

lead_in_extra_diameter = 1.0;


// Small flat on the bottom.
// Improves contact with the print bed.

bed_flat = 0.8;


// Roundness quality

resolution = 96;

eps = 0.20;


// ============================================================
// PIPE STOCK / CUTTING
// ============================================================

// Available pipes

stock_length = 2000;


// Saw or cutting tool kerf.
// Adjust to match the actual tool.

cut_kerf = 2.0;


// We try to get three equal-length track sections
// from one 2 m pipe.

stock_target_pieces = 3;


// RaceGOW requires 20 pipe sections.

track_sections_required = 20;


// ============================================================
// RACEGOW TRACK-SET
// ============================================================
//
// This is the central bill of materials.
// If the requirements change, only this list needs to be updated.
//

track_set = [

    ["elbow", 4],

    ["tee",   6],

    ["4way",  6],

    ["5way",  2]

];


// ============================================================
// FIT TESTS
// ============================================================

fit_clearances = [

    0.20,
    0.30,
    0.40,
    0.50,
    0.60

];

fit_test_depth = 15;

fit_base_thickness = 3;

fit_spacing = 40;


// ============================================================
// SET PREVIEW
// ============================================================

preview_spacing = 115;


// ============================================================
// DERIVED VALUES
// ============================================================

socket_idXY =
    pipe_od + diametral_clearanceXY;

socket_idZ =
    pipe_od + diametral_clearanceZ;

socket_od =
    max(socket_idXY, socket_idZ) + 2 * wall_thickness;


connector_arm_length =
    pipe_stop_offset + socket_depth;


// ------------------------------------------------------------
// Material-optimized gate size
// ------------------------------------------------------------
//
// Example:
//
// Three pipe sections should be cut from a 2000 mm pipe.
//
// Saw kerf is taken into account.
//

gate_ctc_stock_opt =

    (
        stock_length
        - (stock_target_pieces - 1) * cut_kerf
    )

    / stock_target_pieces

    + 2 * pipe_stop_offset;


// Gate size actually used

gate_ctc =

    optimize_gate_for_stock

    ? gate_ctc_stock_opt

    : gate_ctc_manual;


// ------------------------------------------------------------
// PIPE CUT LENGTH
// ------------------------------------------------------------
//
// CTC is the distance between two connector centers.
//
// Each PVC pipe ends pipe_stop_offset before the center.
//
// Therefore:
//
// pipe_cut_length = CTC - 2 * pipe_stop_offset
//

pipe_cut_length =

    gate_ctc

    - 2 * pipe_stop_offset;


// ============================================================
// STOCK OPTIMIZATION
// ============================================================

pieces_per_stock = floor(

    (stock_length + cut_kerf)

    /

    (pipe_cut_length + cut_kerf)

);


stocks_required = ceil(

    track_sections_required

    / pieces_per_stock

);


sections_if_full_stock_cut =

    stocks_required

    * pieces_per_stock;


spares_if_full_stock_cut =

    sections_if_full_stock_cut

    - track_sections_required;


offcut_per_full_stock =

    stock_length

    - pieces_per_stock * pipe_cut_length

    - (pieces_per_stock - 1) * cut_kerf;


// ============================================================
// REPORT
// ============================================================

echo("========================================");

echo("RaceGOW Track Set");

echo("========================================");

echo(
    "Gate size CTC [mm]:",
    gate_ctc
);

echo(
    "RaceGOW minimum CTC [mm]:",
    racegow_min_ctc
);

echo(
    "PVC OD [mm]:",
    pipe_od
);

echo(
    "PVC cut length [mm]:",
    pipe_cut_length
);

echo(
    "Socket ID XY [mm]:",
    socket_idXY
);

echo(
    "Socket ID Z [mm]:",
    socket_idZ
);

echo(
    "Socket depth [mm]:",
    socket_depth
);

echo(
    "Stock-optimized gate CTC [mm]:",
    gate_ctc_stock_opt
);

echo(
    "Pieces per stock pipe:",
    pieces_per_stock
);

echo(
    "Stock pipes required:",
    stocks_required
);

echo(
    "Sections if fully cut:",
    sections_if_full_stock_cut
);

echo(
    "Spare sections:",
    spares_if_full_stock_cut
);

echo(
    "Offcut per fully used stock pipe [mm]:",
    offcut_per_full_stock
);

echo(
    "Connector BOM:",
    track_set
);

echo("========================================");


// ============================================================
// DIRECTIONS
// ============================================================
//
// Each port is first created along +Z.
// It is then rotated into the desired direction.
//
// xp = +X
// xn = -X
// yp = +Y
// yn = -Y
// zp = upward
// zn = downward
//

module orient(dir) {

    if (dir == "xp")

        rotate([0, 90, 0])
            children();


    else if (dir == "xn")

        rotate([0, -90, 0])
            children();


    else if (dir == "yp")

        rotate([-90, 0, 0])
            children();


    else if (dir == "yn")

        rotate([90, 0, 0])
            children();


    else if (dir == "zp")

        children();


    else if (dir == "zn")

        rotate([180, 0, 0])
            children();
}


// ============================================================
// SINGLE ARM
// ============================================================

module outer_arm(dir) {

    orient(dir)

        cylinder(

            h = connector_arm_length,

            d = socket_od,

            $fn = resolution

        );
}


// ============================================================
// PIPE SOCKET
// ============================================================

module socket_bore(dir) {

    bore_id =
        dir == "zp" || dir == "zn"
        ? socket_idZ
        : socket_idXY;

    orient(dir) {


        // Main socket

        translate([
            0,
            0,
            pipe_stop_offset
        ])

            cylinder(

                h = socket_depth + eps,

                d = bore_id,

                $fn = resolution

            );


        // Small lead-in chamfer

        translate([
            0,
            0,
            connector_arm_length - lead_in_depth
        ])

            cylinder(

                h = lead_in_depth + eps,

                d1 = bore_id,

                d2 =
                    bore_id
                    + lead_in_extra_diameter,

                $fn = resolution

            );
    }
}


// ============================================================
// CENTER BODY
// ============================================================

module center_reinforcement() {

    sphere(

        d = socket_od,

        $fn = resolution

    );
}


// ============================================================
// GENERIC CONNECTOR
// ============================================================

module connector_raw(ports) {

    difference() {

        union() {


            // Outer arms

            for (dir = ports)

                outer_arm(dir);


            // Center reinforcement

            center_reinforcement();

        }


        // Pipe sockets

        for (dir = ports)

            socket_bore(dir);

    }
}


// ============================================================
// PRINT-READY CONNECTOR
// ============================================================
//
// The bottom is slightly flattened.
// This helps the part sit more securely on the print bed.
//

module connector_print_ready(ports) {

    difference() {


        translate([
            0,
            0,
            socket_od / 2 - bed_flat
        ])

            connector_raw(ports);


        // Remove everything below Z=0

        translate([
            -500,
            -500,
            -500
        ])

            cube([
                1000,
                1000,
                500
            ]);

    }
}


// ============================================================
// CONNECTOR LIBRARY
// ============================================================

module connector_by_name(name) {


    // --------------------------------------------------------
    // ELBOW
    //
    //     |
    //     |
    //     +----
    //
    // --------------------------------------------------------

    if (name == "elbow")

        connector_print_ready([

            "xp",
            "yp"

        ]);


    // --------------------------------------------------------
    // TEE
    //
    //     |
    // ----+----
    //
    // --------------------------------------------------------

    else if (name == "tee")

        connector_print_ready([

            "xn",
            "xp",
            "yp"

        ]);


    // --------------------------------------------------------
    // CROSS
    //
    //     |
    // ----+----
    //     |
    //
    // All four ports are horizontal.
    //
    // --------------------------------------------------------

    else if (name == "cross")

        connector_print_ready([

            "xp",
            "xn",
            "yp",
            "yn"

        ]);


    // --------------------------------------------------------
    // 4-WAY
    //
    // Three horizontal ports
    // +
    // One port points straight up.
    //
    // This corresponds to the previous "cross_up".
    //
    // --------------------------------------------------------

    else if (name == "4way")

        connector_print_ready([

            "xp",
            "xn",
            "yp",
            "zp"

        ]);


    // --------------------------------------------------------
    // 5-WAY
    //
    // Four horizontal ports
    // +
    // One port points straight up.
    //
    // --------------------------------------------------------

    else if (name == "5way")

        connector_print_ready([

            "xp",
            "xn",
            "yp",
            "yn",
            "zp"

        ]);


    else

        echo(
            str(
                "ERROR: unknown connector: ",
                name
            )
        );
}


// ============================================================
// FIT TEST PIECE
// ============================================================

module fit_test(clearance) {

    test_id =

        pipe_od

        + clearance;


    test_od =

        test_id

        + 2 * wall_thickness;


    difference() {


        cylinder(

            h =
                fit_test_depth
                + fit_base_thickness,

            d = test_od,

            $fn = resolution

        );


        translate([
            0,
            0,
            fit_base_thickness
        ])

            cylinder(

                h =
                    fit_test_depth
                    + eps,

                d = test_id,

                $fn = resolution

            );


        // Lead-in chamfer

        translate([
            0,
            0,
            fit_base_thickness
            + fit_test_depth
            - lead_in_depth
        ])

            cylinder(

                h =
                    lead_in_depth
                    + eps,

                d1 = test_id,

                d2 =
                    test_id
                    + lead_in_extra_diameter,

                $fn = resolution

            );
    }
}


// ============================================================
// FIT TEST ARRAY
// ============================================================

module fit_array() {

    for (
        i = [
            0 :
            len(fit_clearances) - 1
        ]
    ) {

        echo(

            str(
                "Fit test ",
                i + 1,
                ": clearance = ",
                fit_clearances[i],
                " mm"
            )

        );


        translate([

            i * fit_spacing,

            0,

            0

        ])

            fit_test(
                fit_clearances[i]
            );
    }
}


// ============================================================
// ONE OF EACH CONNECTOR TYPE
// ============================================================

module all_parts() {

    names = ["elbow", "tee", "cross", "4way", "5way"];

    for (i = [0 : len(names) - 1])

        translate([
            i * preview_spacing,
            0,
            0
        ])

            connector_by_name(names[i]);
}


// ============================================================
// COMPLETE TRACK SET
// ============================================================
//
// For checking quantities only.
//
// For printing, export ONE STL per connector type
// and set the quantity in Bambu Studio.
//

module track_set_preview() {

    for (
        row = [
            0 :
            len(track_set) - 1
        ]
    ) {

        name =
            track_set[row][0];

        count =
            track_set[row][1];


        for (
            i = [
                0 :
                count - 1
            ]
        )

            translate([

                i * preview_spacing,

                row * preview_spacing,

                0

            ])

                connector_by_name(name);
    }
}


// ============================================================
// VALIDATION + OUTPUT
// ============================================================

module output_model() {

    assert(

        gate_ctc >= racegow_min_ctc,

        str(
            "RaceGOW gate_ctc must be at least ",
            racegow_min_ctc,
            " mm (24 inch center-to-center)."
        )

    )

    assert(

        socket_depth > 0
        && wall_thickness > 0,

        "Socket depth and wall thickness must be positive."

    )


    if (mode == "single")

        connector_by_name(part);


    else if (mode == "all_parts")

        all_parts();


    else if (mode == "set_preview")

        track_set_preview();


    else if (mode == "fit_array")

        fit_array();


    else

        echo(
            str(
                "ERROR: unknown mode: ",
                mode
            )
        );
}


output_model();
