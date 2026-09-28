"""
SMET rev3 simple-machines marble tower -- parametric CadQuery rebuild.

Rebuilt from SMET_rev3_assembly.stl (the original mesh had no CAD source).
Two redesigns, both on by default:
  WINCH_RELEASE  -- marble 2 stays in a cup on the paddle wheel; the wheel's
                    axle winds a string that tips the seesaw, which rolls
                    marble 3 onto the lever.
  VERTICAL_WEDGE -- the wedge hangs from the pulley string and is jammed into
                    the top ramp; the trap door pulls it up to free marble 2.
Set both to False to get the original design back.
Every dimension is in millimetres.  Edit the variables in the PARAMETERS
section below and re-run:

    python smet_rev3_assembly.py

Outputs (written to ./output/):
    smet_rev3_assembly.step   named parts, for importing into Onshape
    smet_rev3_assembly.stl    single mesh, for 3D printing / slicing

Coordinate system (same as the original STL):
    X = left -> right across the base
    Y = front -> back (the two tall posts are at the back, high Y)
    Z = up, Z = 0 is the underside of the base board
"""

import math
import os

import cadquery as cq

# =============================================================================
# PARAMETERS  (millimetres / degrees)
# =============================================================================

# ---- Frame ------------------------------------------------------------------
BASE_W = 304.8          # base board width  (X) -- 12 in
BASE_D = 304.8          # base board depth  (Y) -- 12 in
BASE_T = 19.05          # base board thickness  -- 3/4 in
POST_SIZE = 19.05       # square section of the two back posts and top beam
FRAME_H = 757.001       # overall height, floor to top of the top beam

# Backing boards on the front face of each post (ramps mount to these)
BACKING_T = 11.05               # thickness in Y
BACKING_L_X0 = 2.8              # left backing board: X start
BACKING_L_Z = (341.998, 592.538)
BACKING_R_X1 = 302.0            # right backing board: X end
BACKING_R_Z = (357.343, 563.193)

# Thin backstop plates at the ends of the zig-zag ramps
BACKSTOP_T = 3.2
BACKSTOP_L_X0 = 2.8
BACKSTOP_L_Z = (317.151, 596.538)
BACKSTOP_R_X0 = 298.8
BACKSTOP_R_Z = (357.143, 567.193)
LOWER_BACKSTOP_X = (0.0, 6.0)       # stop at the end of the feed ramp
LOWER_BACKSTOP_Z = (257.725, 316.651)

# ---- Common U-channel ramp profile (used by every straight ramp) --------------
CH_W = 25.4             # outside width -- 1 in
CH_WALL = 2.0           # side wall thickness
CH_FLOOR = 3.2          # floor thickness
CH_WALL_H = 10.0        # side wall height above the floor surface
END_WALL_T = 2.0        # thickness of closed end walls
END_WALL_H = 14.0       # standard closed end wall height above the floor

# Y position of the main ramp line (back ramps run against the backing boards)
RAMP_Y0 = BASE_D - POST_SIZE - BACKING_T - CH_W   # = 249.3 front edge of channel

# ---- Zig-zag inclined planes (6 ramps) --------------------------------------
ZIG_COUNT = 6
ZIG_TILT = 3.0          # degrees
ZIG_LEN = 290.8         # length along the slope
ZIG_DROP_HOLE = 20.8    # floor opening at the low end where the marble drops
ZIG_X_INSET = 7.366     # base edge -> bottom corner of the low end
ZIG_Z0 = 344.865        # bottom corner (low end) of the lowest ramp
ZIG_PITCH = 39.039      # vertical spacing between ramps

# ---- Spiral ("screw") -------------------------------------------------------
SPIRAL_CX, SPIRAL_CY = 140.0, 125.0   # helix axis
SPIRAL_R_MID = 80.0     # centre radius of the channel
SPIRAL_W = 25.4         # channel width (radial)
SPIRAL_PITCH = 35.0     # drop per full turn
SPIRAL_INNER_WALL_H = 8.0    # inner wall height above floor
SPIRAL_OUTER_WALL_H = 18.0   # outer (banked) wall height above floor
SPIRAL_TOP_ANGLE = 90.0      # angle where the marble enters (deg, CCW from +X)
SPIRAL_TOP_Z = 657.3         # floor underside at the entry
SPIRAL_UPPER_SWEEP = 350.0   # first printed section
SPIRAL_LOWER_SWEEP = 340.0   # second printed section
# Mounting tabs (3 per section) that slide over the dowels
TAB_ANGLES = (210.0, 270.0, 330.0)
TAB_W = 12.0
TAB_R_IN = 92.2
TAB_R_OUT = 108.5
TAB_HOLE_D = 6.7
# Dowels holding up the spiral
DOWEL_D = 6.35          # 1/4 in
DOWEL_R = 102.0         # radius of the dowel circle about the helix axis
DOWEL_ABOVE_TAB = 4.0   # dowel sticks up this far above the top tab

# ---- Pins and pivots --------------------------------------------------------
PIN_D = 3.0             # axle / pin diameter
PIVOT_HOLE_D = 3.5      # clearance hole for pins
FORK_T = 8.0            # thickness (X) of the pivot fork uprights
FORK_PRONG = 8.0        # prong depth (Y) for the back-row forks
FORK_PIN_DROP = 4.0     # pin centre below fork top

# ---- Wheel & axle (paddle wheel) --------------------------------------------
WHEEL_CX, WHEEL_CZ = 42.0, 311.151
WHEEL_Y = (248.0, 276.0)       # hub length along Y
WHEEL_HUB_D = 16.0
WHEEL_R = 32.0                 # paddle tip radius
WHEEL_PADDLE_T = 2.4
WHEEL_PADDLE_Y = (252.0, 272.0)
WHEEL_PADDLES = 4

# ---- Wheel & axle winch (redesign) --------------------------------------------
# True  = marble 2 drops into a cup on the wheel and stays there.  Its weight
#         turns the wheel; the drum on the same axle winds a string that lifts
#         the left end of the seesaw, so marble 3 (waiting on the seesaw) rolls
#         off onto the lever.  The feed ramp is no longer needed.
# False = the original passive paddle wheel (loose on a fixed pin).
WINCH_RELEASE = True
WHEEL_LIP_H = 7.0               # cup lip on each paddle tip (holds marble 2)
AXLE_Y = (224.0, 286.0)         # rotating axle (PIN_D bamboo skewer or rod)
DRUM_Y0 = 224.0                 # front face of the string drum
DRUM_D = 8.0                    # winding diameter -- the "axle" of the wheel & axle
DRUM_FLANGE_D = 16.0
DRUM_FLANGE_T = 2.0
DRUM_L = 8.0                    # winding length between the flanges
STRING_D = 1.0
SEESAW_END_WALL_H = 14.0        # new end wall at the seesaw's left end (marble 3 rests on it)
SEESAW_TAB_U = (-45.0, -39.0)   # string tab position along the seesaw (from its pivot)
SEESAW_TAB_Y0 = 226.0           # the tab reaches forward to here, under the drum

# ---- Feed ramp (5 deg) between wheel and seesaw ------------------------------
FEED_TILT = 5.0
FEED_LEN = 95.965
FEED_ANCHOR = (6.121, RAMP_Y0, 258.702)     # bottom corner at high (left) end

# ---- Seesaw (lever on pivot) -------------------------------------------------
SEESAW_PIVOT = (150.0, 248.312)     # (x, z) of the pin
SEESAW_TILT = 1.0
SEESAW_LEN = 90.0
SEESAW_BLOCK_W = 8.0
SEESAW_BLOCK_BELOW = 3.5            # pivot block extends this far below pin
SEESAW_FLOOR_ABOVE = 2.0            # floor underside above pin centre
SEESAW_WEIGHT_D = 19.0
SEESAW_WEIGHT_T = 1.52
SEESAW_WEIGHT_U = -23.0             # weight position along the seesaw

# ---- Counter-weighted lever -------------------------------------------------
LEVER_X0 = 151.0
LEVER_LEN = 137.0
LEVER_Z0 = 221.549                  # underside of lever floor
LEVER_PIVOT_X = 185.0
LEVER_BLOCK_BELOW = 3.5             # pivot block extends this far below pin
LEVER_BOX = (152.0, 251.0, 174.0, 273.0)   # counterweight box x0,y0,x1,y1
LEVER_BOX_H = 13.0
LEVER_BOX_WALL = 1.0
LEVER_WEIGHT_D = 19.0
LEVER_WEIGHT_H = 10.64
LEVER_TAB_X = (280.0, 302.0)
LEVER_TAB_Y = (226.3, 240.3)

# ---- Tipping cradle + rocker ------------------------------------------------
CRADLE_ANCHOR = (289.935, RAMP_Y0, 200.301)
CRADLE_LEN = 14.5
CRADLE_TILT = -1.146
CRADLE_PIN_Y, CRADLE_PIN_Z = 246.0, 214.898
CRADLE_EAR_X = ((290.0, 292.0), (300.0, 302.0))
CRADLE_EAR_Y0 = 242.7
CRADLE_EAR_H = 10.0
ROCKER_X = (293.0, 299.0)
ROCKER_Y = (222.0, 278.0)
ROCKER_T = 3.0
ROCKER_HUB_D = 6.4
CRADLE_PIN_X = (289.0, 303.0)

# ---- Trap-door lever (hinged channel) ----------------------------------------
TRAP_X0 = 180.0
TRAP_LEN = 114.0
TRAP_Y0 = 162.3
TRAP_Z0 = 190.276
TRAP_KNUCKLE_R = 3.5
TRAP_HINGE_Z = 188.276
TRAP_GATE_X = 284.0
TRAP_GATE_T = 3.0
TRAP_LATCH_TAB = (286.0, 187.7, 296.0, 195.5)
TRAP_STRING_TAB = (230.0, 152.5, 240.0, 162.3)
TRAP_STRING_HOLE_D = 1.8

# ---- Entry ramp (marble 1 arrives here from the previous group) ----------------
ENTRY_TILT = -3.0
ENTRY_LEN = 175.941
ENTRY_ANCHOR = (0.133, TRAP_Y0, 199.989)

# ---- Top ramp, wedge and pulley ---------------------------------------------
TOP_TILT = 3.0
TOP_LEN = 159.218
TOP_ANCHOR = (141.167, 192.3, 657.355)
TOP_CHUTE_X = (223.0, 249.0)
TOP_CHUTE_TOP = 709.001
WEDGE = (227.0, 195.0, 245.0, 215.0)   # x0, y0, x1, y1
WEDGE_Z0 = 667.001
WEDGE_H_LOW, WEDGE_H_HIGH = 6.0, 18.0
WEDGE_DISC_D, WEDGE_DISC_T = 19.0, 3.04
WEDGE_DISC_C = (235.4, 205.0, 677.801)

# Wedge redesign: True = a wooden wedge hangs straight down from the pulley
# string and is jammed (wedged) into the top ramp between its side walls,
# holding marble 2.  When the trap door pulls the string, the wedge is pulled
# up out of the ramp.  False = the original block wedge on the ramp floor.
VERTICAL_WEDGE = True
WEDGE_T = 12.0              # thickness along the ramp, centred under the pulley
WEDGE_HEIGHT = 20.0
WEDGE_HALF_ANGLE = 15.0     # taper of each side face
WEDGE_GAP = 1.0             # clearance under the wedge while it is jammed
PULLEY_STRING_D = 1.0
# Washers stacked on the wedge's string.  The wedge's weight is what holds the
# trap door level, so add or remove washers until the trap door just stays up
# by itself and tips when marble 1 rolls onto it.
WEDGE_WEIGHT_D, WEDGE_WEIGHT_T, WEDGE_WEIGHT_HOLE = 19.0, 3.04, 3.0

PULLEY_Y, PULLEY_Z = 195.0, 727.001
PULLEY_X0 = 228.5
PULLEY_FLANGE_D, PULLEY_FLANGE_T = 28.0, 1.5
PULLEY_HUB_D, PULLEY_HUB_L = 20.0, 10.0
PULLEY_AXLE_X = (226.0, 294.0)
PULLEY_ARM = (286.0, 180.0, 294.0, 721.001)    # x0, y0, x1, z0
PULLEY_ARM_H = 12.0

# ---- Transfer chute (spiral exit -> top zig-zag ramp) -------------------------
TRANSFER_ANCHOR = (42.744, 258.862, 576.978)   # bottom corner at low end
TRANSFER_YAW = -30.0
TRANSFER_TILT = 5.0
TRANSFER_LEN = 151.413
TRANSFER_END_WALL_H = 16.0
TRANSFER_DROP_HOLE = 20.0

# ---- Marbles ----------------------------------------------------------------
MARBLE_D = 15.875       # 5/8 in
MARBLE_1 = (0.716, 175.0, 211.111)     # arriving from the previous group
MARBLE_2 = (252.938, 205.0, 674.366)   # waiting behind the wedge at the top

# ---- Simple support posts: name -> (x0, y0, x1, y1, z_top) ------------------
POSTS = {
    "post_top_ramp": (297.0, 199.0, 303.0, 211.0, 665.484),
    "post_lever_box": (159.0, 256.0, 167.0, 268.0, 208.499),
    "post_lever_rest": (266.402, 256.0, 274.402, 268.0, 203.908),
    "post_entry_ramp_1": (36.0, 169.0, 44.0, 181.0, 197.694),
    "post_entry_ramp_2": (121.0, 169.0, 129.0, 181.0, 193.239),
    "post_feed_ramp": (94.0, 256.0, 100.0, 268.0, 250.501),
    "post_cradle": (294.0, 256.0, 300.0, 268.0, 199.8),
    "post_trap_stop": (279.602, 188.7, 287.049, 195.5, 147.703),
}
# Posts with a flat stop plate on top: name -> (x0, x1, post_y0, plate_y0, y1, z_top, plate_t)
STOP_POSTS = {
    "seesaw_stop_left": (105.006, 111.006, 278.0, 267.0, 286.0, 246.535, 2.95),
    "seesaw_stop_right": (171.757, 177.757, 278.0, 267.0, 286.0, 243.395, 2.95),
}
TRAP_LATCH_POST = (286.0, 296.0, 196.5, 188.7, 203.0, 193.476, 6.0)

# Pivot forks: name -> (x0, [(y0, y1), ...], z_top, pin_z, pin_y_range)
FORKS = {
    "fork_wheel": (38.0, [(238.0, 246.0), (278.0, 286.0)], 315.151, None, None),
    "fork_seesaw": (146.0, [(238.0, 246.0), (278.0, 286.0)], 252.312, None, None),
    "fork_lever": (181.0, [(238.0, 246.0), (278.0, 286.0)], 223.549, None, None),
    "fork_trapdoor": (176.0, [(155.0, 160.8), (189.2, 195.0)], 191.276, 188.276, None),
    "wheel_stop_pin": (65.0, [(278.0, 286.0)], 308.451, 308.451, (254.0, 286.0)),
}
WHEEL_STOP_T = 6.0      # the wheel-stop post is 6 mm wide instead of FORK_T


# =============================================================================
# HELPERS
# =============================================================================

def box(x0, y0, z0, x1, y1, z1):
    """Axis-aligned box between two corners."""
    return (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))


def cyl(d, p0, axis, length):
    """Cylinder of diameter d starting at p0 running `length` along `axis`."""
    return cq.Workplane("XY").add(
        cq.Solid.makeCylinder(d / 2.0, length, cq.Vector(*p0), cq.Vector(*axis)))


def place(wp, anchor, pitch=0.0, yaw=0.0):
    """Tilt a part built in local coordinates (+X along its length) up by
    `pitch` degrees, turn it `yaw` degrees about Z, and move its origin to
    `anchor`."""
    if pitch:
        wp = wp.rotate((0, 0, 0), (0, 1, 0), -pitch)
    if yaw:
        wp = wp.rotate((0, 0, 0), (0, 0, 1), yaw)
    return wp.translate(anchor)


def channel(length, *, end_wall_start=None, end_wall_end=None,
            hole_start=None, hole_end=None, width=CH_W):
    """Straight U-channel in local coordinates.

    Origin at the bottom corner of the start end; +X along the channel,
    +Y across it, +Z up.  end_wall_* is the end wall height above the floor
    surface (None = open end).  hole_* = (offset, length) of a drop hole cut
    through the floor between the walls, measured from that end."""
    h = CH_FLOOR + CH_WALL_H
    ch = box(0, 0, 0, length, width, h).cut(
        box(-1, CH_WALL, CH_FLOOR, length + 1, width - CH_WALL, h + 1))
    if end_wall_start is not None:
        ch = ch.union(box(0, 0, 0, END_WALL_T, width, CH_FLOOR + end_wall_start))
    if end_wall_end is not None:
        ch = ch.union(box(length - END_WALL_T, 0, 0, length, width,
                          CH_FLOOR + end_wall_end))
    if hole_start is not None:
        off, ln = hole_start
        ch = ch.cut(box(off, CH_WALL, -1, off + ln, width - CH_WALL, CH_FLOOR + 1))
    if hole_end is not None:
        off, ln = hole_end
        ch = ch.cut(box(length - off - ln, CH_WALL, -1, length - off,
                        width - CH_WALL, CH_FLOOR + 1))
    return ch


def helical_channel(sweep_deg, top_angle, top_z):
    """One section of the spiral: a U-channel swept along a descending helix.

    Starts (high end) at `top_angle` with the floor underside at `top_z`
    and descends counter-clockwise (seen from above) by SPIRAL_PITCH/turn."""
    r0 = SPIRAL_R_MID - SPIRAL_W / 2
    r1 = SPIRAL_R_MID + SPIRAL_W / 2
    pts = [
        (r0, 0), (r1, 0),
        (r1, CH_FLOOR + SPIRAL_OUTER_WALL_H), (r1 - CH_WALL, CH_FLOOR + SPIRAL_OUTER_WALL_H),
        (r1 - CH_WALL, CH_FLOOR), (r0 + CH_WALL, CH_FLOOR),
        (r0 + CH_WALL, CH_FLOOR + SPIRAL_INNER_WALL_H), (r0, CH_FLOOR + SPIRAL_INNER_WALL_H),
    ]
    height = SPIRAL_PITCH * sweep_deg / 360.0
    # A left-handed helix climbs clockwise, i.e. it descends counter-clockwise.
    helix = cq.Wire.makeHelix(SPIRAL_PITCH, height, SPIRAL_R_MID, lefthand=True)
    solid = (cq.Workplane("XZ").polyline(pts).close()
             .sweep(cq.Workplane().add(helix), isFrenet=True))
    low_angle = top_angle + sweep_deg        # where the section ends (low end)
    low_z = top_z - height
    return (solid.rotate((0, 0, 0), (0, 0, 1), low_angle)
            .translate((SPIRAL_CX, SPIRAL_CY, low_z)))


def spiral_floor_z(angle_from_top):
    """Floor underside height of the spiral `angle_from_top` deg after entry."""
    return SPIRAL_TOP_Z - SPIRAL_PITCH * angle_from_top / 360.0


def spiral_tab(angle, z):
    tab = box(TAB_R_IN, -TAB_W / 2, 0, TAB_R_OUT, TAB_W / 2, CH_FLOOR).cut(
        cyl(TAB_HOLE_D, (DOWEL_R, 0, -1), (0, 0, 1), CH_FLOOR + 2))
    return (tab.rotate((0, 0, 0), (0, 0, 1), angle)
            .translate((SPIRAL_CX, SPIRAL_CY, z)))


def angle_after(start, a):
    """Degrees travelled (CCW) from `start` to angle `a`, in [0, 360)."""
    return (a - start) % 360.0


# =============================================================================
# BUILD
# =============================================================================

def build(winch_release=None, vertical_wedge=None):
    """Build every part.  winch_release / vertical_wedge override
    WINCH_RELEASE / VERTICAL_WEDGE; passing False for both rebuilds the
    original design exactly, as used by compare.py."""
    if winch_release is None:
        winch_release = WINCH_RELEASE
    if vertical_wedge is None:
        vertical_wedge = VERTICAL_WEDGE
    parts = {}   # name -> (Workplane, colour)
    WOOD = (0.80, 0.62, 0.40)
    RAMP = (0.25, 0.55, 0.85)
    MECH = (0.90, 0.45, 0.15)
    SUPPORT = (0.55, 0.55, 0.60)
    METAL = (0.75, 0.75, 0.78)
    MARBLE = (0.15, 0.75, 0.35)
    z_deck = BASE_T
    post_y0 = BASE_D - POST_SIZE

    # ---- Frame ----
    parts["base"] = (box(0, 0, 0, BASE_W, BASE_D, BASE_T), WOOD)
    parts["post_left"] = (box(0, post_y0, z_deck, POST_SIZE, BASE_D, FRAME_H), WOOD)
    parts["post_right"] = (box(BASE_W - POST_SIZE, post_y0, z_deck, BASE_W, BASE_D, FRAME_H), WOOD)
    parts["top_beam"] = (box(POST_SIZE, post_y0, FRAME_H - POST_SIZE,
                             BASE_W - POST_SIZE, BASE_D, FRAME_H), WOOD)
    by0 = post_y0 - BACKING_T
    parts["backing_left"] = (box(BACKING_L_X0, by0, BACKING_L_Z[0], POST_SIZE, post_y0, BACKING_L_Z[1]), WOOD)
    parts["backing_right"] = (box(BASE_W - POST_SIZE, by0, BACKING_R_Z[0], BACKING_R_X1, post_y0, BACKING_R_Z[1]), WOOD)
    parts["backstop_left"] = (box(BACKSTOP_L_X0, RAMP_Y0, BACKSTOP_L_Z[0],
                                  BACKSTOP_L_X0 + BACKSTOP_T, RAMP_Y0 + CH_W, BACKSTOP_L_Z[1]), SUPPORT)
    parts["backstop_right"] = (box(BACKSTOP_R_X0, RAMP_Y0, BACKSTOP_R_Z[0],
                                   BACKSTOP_R_X0 + BACKSTOP_T, RAMP_Y0 + CH_W, BACKSTOP_R_Z[1]), SUPPORT)
    parts["backstop_feed"] = (box(LOWER_BACKSTOP_X[0], RAMP_Y0, LOWER_BACKSTOP_Z[0],
                                  LOWER_BACKSTOP_X[1], RAMP_Y0 + CH_W, LOWER_BACKSTOP_Z[1]), SUPPORT)

    # ---- Zig-zag inclined planes ----
    for k in range(ZIG_COUNT):
        ramp = channel(ZIG_LEN, hole_start=(0.0, ZIG_DROP_HOLE))
        ramp = place(ramp, (ZIG_X_INSET, RAMP_Y0, ZIG_Z0 + k * ZIG_PITCH), pitch=ZIG_TILT)
        if k % 2:   # every other ramp runs the opposite way
            ramp = ramp.mirror("YZ", basePointVector=(BASE_W / 2, 0, 0))
        parts[f"zigzag_ramp_{k + 1}"] = (ramp, RAMP)

    # ---- Spiral (screw) + dowels ----
    sections = [("spiral_upper", 0.0, SPIRAL_UPPER_SWEEP),
                ("spiral_lower", SPIRAL_UPPER_SWEEP, SPIRAL_LOWER_SWEEP)]
    top_tab_z = {}
    for name, start, sweep in sections:
        top_angle = (SPIRAL_TOP_ANGLE + start) % 360.0
        sp = helical_channel(sweep, top_angle, spiral_floor_z(start))
        for a in TAB_ANGLES:
            travelled = start + angle_after(top_angle, a)
            z = spiral_floor_z(travelled)
            top_tab_z.setdefault(a, z + CH_FLOOR)
            sp = sp.union(spiral_tab(a, z))
        parts[name] = (sp, RAMP)
    for i, a in enumerate(TAB_ANGLES):
        x = SPIRAL_CX + DOWEL_R * math.cos(math.radians(a))
        y = SPIRAL_CY + DOWEL_R * math.sin(math.radians(a))
        h = top_tab_z[a] + DOWEL_ABOVE_TAB - z_deck
        parts[f"dowel_{i + 1}"] = (cyl(DOWEL_D, (x, y, z_deck), (0, 0, 1), h), WOOD)

    # ---- Transfer chute: spiral exit -> top zig-zag ramp ----
    tr = channel(TRANSFER_LEN, end_wall_start=TRANSFER_END_WALL_H,
                 hole_start=(END_WALL_T, TRANSFER_DROP_HOLE))
    parts["transfer_chute"] = (place(tr, TRANSFER_ANCHOR, TRANSFER_TILT, TRANSFER_YAW), RAMP)

    # ---- Top ramp, wedge, pulley ----
    top = place(channel(TOP_LEN, end_wall_end=END_WALL_H), TOP_ANCHOR, TOP_TILT)
    ax, ay, az = TOP_ANCHOR
    if not vertical_wedge:
        # original: tall guide walls for the block wedge
        chute_z0 = az + (TOP_CHUTE_X[0] - ax) * math.tan(math.radians(TOP_TILT)) + CH_FLOOR
        for y0 in (ay, ay + CH_W - CH_WALL):
            top = top.union(box(TOP_CHUTE_X[0], y0, chute_z0, TOP_CHUTE_X[1], y0 + CH_WALL, TOP_CHUTE_TOP))
    parts["top_ramp"] = (top, RAMP)

    marble_2 = MARBLE_2
    if vertical_wedge:
        # Heights on the tilted top ramp at a given x
        t3, c3 = math.tan(math.radians(TOP_TILT)), math.cos(math.radians(TOP_TILT))
        top_bottom = lambda x: az + (x - ax) * t3
        top_floor = lambda x: top_bottom(x) + CH_FLOOR / c3
        top_wall = lambda x: top_bottom(x) + (CH_FLOOR + CH_WALL_H) / c3
        cx = PULLEY_X0 + PULLEY_FLANGE_T + PULLEY_HUB_L / 2      # under the pulley
        yc = ay + CH_W / 2
        wx0, wx1 = cx - WEDGE_T / 2, cx + WEDGE_T / 2
        # The wedge's sloping sides jam against the top edges of the channel
        # walls (at the high end of the wedge, where the walls are highest).
        gap_w = CH_W - 2 * CH_WALL
        z_jam = top_wall(wx1)
        z_b = top_floor(wx1) + WEDGE_GAP
        z_t = z_b + WEDGE_HEIGHT
        ta = math.tan(math.radians(WEDGE_HALF_ANGLE))
        width = lambda z: gap_w + 2 * (z - z_jam) * ta
        wb, wt = width(z_b), width(z_t)
        wedge = (cq.Workplane("YZ", origin=(wx0, 0, 0))
                 .polyline([(yc - wb / 2, z_b), (yc + wb / 2, z_b), (yc + wt / 2, z_t), (yc - wt / 2, z_t)])
                 .close().extrude(WEDGE_T))
        parts["wedge"] = (wedge, WOOD)
        # Pulley string: wedge -> over the hub -> trap door
        hub_r = PULLEY_HUB_D / 2 + PULLEY_STRING_D / 2
        ww = cyl(WEDGE_WEIGHT_D, (cx, PULLEY_Y + hub_r, z_t), (0, 0, 1), WEDGE_WEIGHT_T).cut(
            cyl(WEDGE_WEIGHT_HOLE, (cx, PULLEY_Y + hub_r, z_t - 1), (0, 0, 1), WEDGE_WEIGHT_T + 2))
        parts["wedge_weight"] = (ww, METAL)
        parts["pulley_string_wedge"] = (cyl(PULLEY_STRING_D, (cx, PULLEY_Y + hub_r, z_t), (0, 0, 1),
                                            PULLEY_Z - z_t), (0.20, 0.20, 0.20))
        tx0, ty0, tx1, ty1 = TRAP_STRING_TAB
        p0 = cq.Vector(cx, PULLEY_Y - hub_r, PULLEY_Z)
        p1 = cq.Vector((tx0 + tx1) / 2, (ty0 + ty1) / 2, TRAP_Z0 + CH_FLOOR)
        parts["pulley_string_trapdoor"] = (cyl(PULLEY_STRING_D, p0.toTuple(), (p1 - p0).toTuple(),
                                               (p1 - p0).Length), (0.20, 0.20, 0.20))
        # Marble 2 rests against the wedge's downhill face
        r = MARBLE_D / 2
        s3 = math.sin(math.radians(TOP_TILT))
        px = wx1 + r + r * s3
        marble_2 = (wx1 + r, yc, top_floor(px) + r * c3)
    else:
        wx0, wy0, wx1, wy1 = WEDGE
        wedge = (cq.Workplane("XZ", origin=(0, wy1, 0))
                 .polyline([(wx0, WEDGE_Z0), (wx1, WEDGE_Z0), (wx1, WEDGE_Z0 + WEDGE_H_HIGH),
                            (wx0, WEDGE_Z0 + WEDGE_H_LOW)]).close()
                 .extrude(wy1 - wy0))
        parts["wedge"] = (wedge, MECH)
        parts["wedge_disc"] = (cyl(WEDGE_DISC_D, WEDGE_DISC_C, (0, 0, 1), WEDGE_DISC_T), METAL)

    fl = PULLEY_FLANGE_T
    x0 = PULLEY_X0
    spool = (cyl(PULLEY_FLANGE_D, (x0, PULLEY_Y, PULLEY_Z), (1, 0, 0), fl)
             .union(cyl(PULLEY_HUB_D, (x0 + fl, PULLEY_Y, PULLEY_Z), (1, 0, 0), PULLEY_HUB_L))
             .union(cyl(PULLEY_FLANGE_D, (x0 + fl + PULLEY_HUB_L, PULLEY_Y, PULLEY_Z), (1, 0, 0), fl))
             .cut(cyl(PIVOT_HOLE_D, (x0 - 1, PULLEY_Y, PULLEY_Z), (1, 0, 0), PULLEY_HUB_L + 2 * fl + 2)))
    parts["pulley"] = (spool, MECH)
    parts["pulley_axle"] = (cyl(PIN_D, (PULLEY_AXLE_X[0], PULLEY_Y, PULLEY_Z), (1, 0, 0),
                                PULLEY_AXLE_X[1] - PULLEY_AXLE_X[0]), METAL)
    ax0, ay0, ax1, az0 = PULLEY_ARM
    arm = box(ax0, ay0, az0, ax1, post_y0, az0 + PULLEY_ARM_H).cut(
        cyl(PIVOT_HOLE_D, (ax0 - 1, PULLEY_Y, PULLEY_Z), (1, 0, 0), ax1 - ax0 + 2))
    parts["pulley_arm"] = (arm, SUPPORT)

    # ---- Wheel & axle (paddle wheel) ----
    hub_len = WHEEL_Y[1] - WHEEL_Y[0]
    wheel = cyl(WHEEL_HUB_D, (WHEEL_CX, WHEEL_Y[0], WHEEL_CZ), (0, 1, 0), hub_len)
    for i in range(WHEEL_PADDLES):
        paddle = box(0, WHEEL_PADDLE_Y[0], -WHEEL_PADDLE_T / 2, WHEEL_R, WHEEL_PADDLE_Y[1], WHEEL_PADDLE_T / 2)
        if winch_release:
            # Lip on the tip, on the face that is on top when the paddle is
            # loaded (pointing left), so the marble rides the wheel down.
            paddle = paddle.union(box(WHEEL_R - WHEEL_PADDLE_T, WHEEL_PADDLE_Y[0],
                                      -WHEEL_PADDLE_T / 2 - WHEEL_LIP_H, WHEEL_R,
                                      WHEEL_PADDLE_Y[1], -WHEEL_PADDLE_T / 2))
        paddle = paddle.rotate((0, 0, 0), (0, 1, 0), i * 360.0 / WHEEL_PADDLES)
        wheel = wheel.union(paddle.translate((WHEEL_CX, 0, WHEEL_CZ)))
    # Winch: the wheel is fixed to the axle (bore = axle).  Original: it
    # spins loose on a fixed pin.
    bore = PIN_D if winch_release else PIVOT_HOLE_D
    wheel = wheel.cut(cyl(bore, (WHEEL_CX, WHEEL_Y[0] - 1, WHEEL_CZ), (0, 1, 0), hub_len + 2))
    parts["paddle_wheel"] = (wheel, MECH)

    marbles = {"marble_1": MARBLE_1, "marble_2": marble_2}
    seesaw_piv = (SEESAW_PIVOT[0], RAMP_Y0, SEESAW_PIVOT[1])
    st = math.radians(SEESAW_TILT)

    def seesaw_to_global(u, n):
        return (seesaw_piv[0] + u * math.cos(st) - n * math.sin(st),
                seesaw_piv[2] + u * math.sin(st) + n * math.cos(st))

    if winch_release:
        # Rotating axle: the wheel and the drum are both glued to it
        parts["wheel_axle"] = (cyl(PIN_D, (WHEEL_CX, AXLE_Y[0], WHEEL_CZ), (0, 1, 0),
                                   AXLE_Y[1] - AXLE_Y[0]), METAL)
        # String drum -- the small-radius "axle" that winds the string
        fl = DRUM_FLANGE_T
        drum = (cyl(DRUM_FLANGE_D, (WHEEL_CX, DRUM_Y0, WHEEL_CZ), (0, 1, 0), fl)
                .union(cyl(DRUM_D, (WHEEL_CX, DRUM_Y0 + fl, WHEEL_CZ), (0, 1, 0), DRUM_L))
                .union(cyl(DRUM_FLANGE_D, (WHEEL_CX, DRUM_Y0 + fl + DRUM_L, WHEEL_CZ), (0, 1, 0), fl))
                .cut(cyl(PIN_D, (WHEEL_CX, DRUM_Y0 - 1, WHEEL_CZ), (0, 1, 0), DRUM_L + 2 * fl + 2)))
        parts["string_drum"] = (drum, MECH)

        # String from the drum to the tab on the seesaw's left end.  It leaves
        # the drum on the side that winds in when marble 2 turns the wheel
        # (anticlockwise seen from the front).
        drum_y = DRUM_Y0 + fl + DRUM_L / 2
        tab_u = (SEESAW_TAB_U[0] + SEESAW_TAB_U[1]) / 2
        gx, gz = seesaw_to_global(tab_u, SEESAW_FLOOR_ABOVE + CH_FLOOR)
        rho = DRUM_D / 2 + STRING_D / 2
        dx, dz = gx - WHEEL_CX, gz - WHEEL_CZ
        beta, alpha = math.atan2(dz, dx), math.acos(rho / math.hypot(dx, dz))
        for phi in (beta + alpha, beta - alpha):
            tx, tz = WHEEL_CX + rho * math.cos(phi), WHEEL_CZ + rho * math.sin(phi)
            # surface moves along (-sin, cos); winding means moving away from the tab
            if -math.sin(phi) * (gx - tx) + math.cos(phi) * (gz - tz) < 0:
                break
        v = cq.Vector(gx - tx, 0, gz - tz)
        parts["winch_string"] = (cyl(STRING_D, (tx, drum_y, tz), v.toTuple(), v.Length), (0.20, 0.20, 0.20))

        # Marble 3 waits on the seesaw, against its new left end wall
        r = MARBLE_D / 2
        mx, mz = seesaw_to_global(-SEESAW_LEN / 2 + END_WALL_T + r, SEESAW_FLOOR_ABOVE + CH_FLOOR + r)
        marbles["marble_3"] = (mx, RAMP_Y0 + CH_W / 2, mz)

    # ---- Pivot forks (uprights + pin) ----
    for name, (fx0, prongs, ztop, pin_z, pin_y) in FORKS.items():
        t = WHEEL_STOP_T if name == "wheel_stop_pin" else FORK_T
        pin_z = ztop - FORK_PIN_DROP if pin_z is None else pin_z
        pin_y = pin_y or (prongs[0][0], prongs[-1][1])
        f = None
        for y0, y1 in prongs:
            b = box(fx0, y0, z_deck, fx0 + t, y1, ztop)
            f = b if f is None else f.union(b)
        if winch_release and name == "fork_wheel":
            # The axle turns with the wheel, so the fork gets bearing holes
            # instead of a fixed pin.
            f = f.cut(cyl(PIVOT_HOLE_D, (fx0 + t / 2, pin_y[0] - 1, pin_z), (0, 1, 0), pin_y[1] - pin_y[0] + 2))
            parts[name] = (f, SUPPORT)
            continue
        f = f.union(cyl(PIN_D, (fx0 + t / 2, pin_y[0], pin_z), (0, 1, 0), pin_y[1] - pin_y[0]))
        parts[name] = (f, SUPPORT)

    # ---- Feed ramp (original design only: marble 2 rolled from the wheel to the seesaw) ----
    if not winch_release:
        parts["feed_ramp"] = (place(channel(FEED_LEN), FEED_ANCHOR, -FEED_TILT), RAMP)

    # ---- Seesaw ----
    half = SEESAW_LEN / 2
    ss = channel(SEESAW_LEN).translate((-half, 0, SEESAW_FLOOR_ABOVE))
    ss = ss.union(box(-SEESAW_BLOCK_W / 2, 0, -SEESAW_BLOCK_BELOW,
                      SEESAW_BLOCK_W / 2, CH_W, SEESAW_FLOOR_ABOVE))
    ss = ss.cut(cyl(PIVOT_HOLE_D, (0, -1, 0), (0, 1, 0), CH_W + 2))
    if winch_release:
        # End wall for marble 3 to rest against, and a tab reaching forward
        # under the drum for the winch string.  Marble 3's weight keeps the
        # left end down, so the old weight disc is not needed.
        ss = ss.union(box(-half, 0, SEESAW_FLOOR_ABOVE, -half + END_WALL_T, CH_W,
                          SEESAW_FLOOR_ABOVE + CH_FLOOR + SEESAW_END_WALL_H))
        u0, u1 = SEESAW_TAB_U
        ss = ss.union(box(u0, SEESAW_TAB_Y0 - RAMP_Y0, SEESAW_FLOOR_ABOVE, u1, 0,
                          SEESAW_FLOOR_ABOVE + CH_FLOOR))
        hole_y = DRUM_Y0 + DRUM_FLANGE_T + DRUM_L / 2 - RAMP_Y0
        ss = ss.cut(cyl(TRAP_STRING_HOLE_D, ((u0 + u1) / 2, hole_y, SEESAW_FLOOR_ABOVE - 1), (0, 0, 1),
                        CH_FLOOR + 2))
        parts["seesaw"] = (place(ss, seesaw_piv, SEESAW_TILT), MECH)
    else:
        sw = cyl(SEESAW_WEIGHT_D, (SEESAW_WEIGHT_U, CH_W / 2, SEESAW_FLOOR_ABOVE - SEESAW_WEIGHT_T),
                 (0, 0, 1), SEESAW_WEIGHT_T)
        parts["seesaw"] = (place(ss, seesaw_piv, SEESAW_TILT), MECH)
        parts["seesaw_weight"] = (place(sw, seesaw_piv, SEESAW_TILT), METAL)

    # ---- Counter-weighted lever ----
    lv = place(channel(LEVER_LEN, end_wall_start=END_WALL_H), (LEVER_X0, RAMP_Y0, LEVER_Z0))
    bx0, by0_, bx1, by1 = LEVER_BOX
    w = LEVER_BOX_WALL
    lv = lv.union(box(bx0, by0_, LEVER_Z0 - LEVER_BOX_H, bx1, by1, LEVER_Z0))
    lv = lv.cut(box(bx0 + w, by0_ + w, LEVER_Z0 - LEVER_BOX_H + w, bx1 - w, by1 - w, LEVER_Z0))
    pivot_z = FORKS["fork_lever"][2] - FORK_PIN_DROP
    lv = lv.union(box(LEVER_PIVOT_X - FORK_T / 2, RAMP_Y0, pivot_z - LEVER_BLOCK_BELOW,
                      LEVER_PIVOT_X + FORK_T / 2, RAMP_Y0 + CH_W, LEVER_Z0))
    lv = lv.cut(cyl(PIVOT_HOLE_D, (LEVER_PIVOT_X, RAMP_Y0 - 1, pivot_z), (0, 1, 0), CH_W + 2))
    lx_end = LEVER_X0 + LEVER_LEN
    lv = lv.union(box(LEVER_TAB_X[0], LEVER_TAB_Y[0], LEVER_Z0, LEVER_TAB_X[1], LEVER_TAB_Y[1], LEVER_Z0 + CH_FLOOR))
    lv = lv.union(box(LEVER_TAB_X[0], LEVER_TAB_Y[1], LEVER_Z0, lx_end, RAMP_Y0, LEVER_Z0 + CH_FLOOR))
    parts["lever"] = (lv, MECH)
    parts["lever_weight"] = (cyl(LEVER_WEIGHT_D, ((bx0 + bx1) / 2, (by0_ + by1) / 2, LEVER_Z0 - LEVER_BOX_H + w),
                                 (0, 0, 1), LEVER_WEIGHT_H), METAL)

    # ---- Tipping cradle, rocker and pin ----
    cr = place(channel(CRADLE_LEN), CRADLE_ANCHOR, CRADLE_TILT)
    ez0 = CRADLE_PIN_Z - CRADLE_EAR_H / 2
    for ex0, ex1 in CRADLE_EAR_X:
        cr = cr.union(box(ex0, CRADLE_EAR_Y0, ez0, ex1, RAMP_Y0, ez0 + CRADLE_EAR_H))
    cr = cr.cut(cyl(PIVOT_HOLE_D, (CRADLE_PIN_X[0], CRADLE_PIN_Y, CRADLE_PIN_Z), (1, 0, 0),
                    CRADLE_PIN_X[1] - CRADLE_PIN_X[0]))
    parts["cradle"] = (cr, MECH)
    rk = box(ROCKER_X[0], ROCKER_Y[0], CRADLE_PIN_Z - ROCKER_T / 2,
             ROCKER_X[1], ROCKER_Y[1], CRADLE_PIN_Z + ROCKER_T / 2)
    rk = rk.union(cyl(ROCKER_HUB_D, (ROCKER_X[0], CRADLE_PIN_Y, CRADLE_PIN_Z), (1, 0, 0),
                      ROCKER_X[1] - ROCKER_X[0]))
    rk = rk.cut(cyl(PIVOT_HOLE_D, (ROCKER_X[0] - 1, CRADLE_PIN_Y, CRADLE_PIN_Z), (1, 0, 0),
                    ROCKER_X[1] - ROCKER_X[0] + 2))
    parts["rocker"] = (rk, MECH)
    parts["cradle_pin"] = (cyl(PIN_D, (CRADLE_PIN_X[0], CRADLE_PIN_Y, CRADLE_PIN_Z), (1, 0, 0),
                               CRADLE_PIN_X[1] - CRADLE_PIN_X[0]), METAL)

    # ---- Trap-door lever ----
    td = place(channel(TRAP_LEN), (TRAP_X0, TRAP_Y0, TRAP_Z0))
    gx = TRAP_GATE_X
    td = td.union(box(gx, TRAP_Y0, TRAP_Z0, gx + TRAP_GATE_T, TRAP_Y0 + CH_W,
                      TRAP_Z0 + CH_FLOOR + END_WALL_H))
    td = td.union(cyl(2 * TRAP_KNUCKLE_R, (TRAP_X0, TRAP_Y0, TRAP_HINGE_Z), (0, 1, 0), CH_W))
    td = td.union(box(TRAP_X0, TRAP_Y0, TRAP_HINGE_Z - TRAP_KNUCKLE_R,
                      TRAP_X0 + FORK_T / 2, TRAP_Y0 + CH_W, TRAP_Z0))
    td = td.cut(cyl(PIVOT_HOLE_D, (TRAP_X0, TRAP_Y0 - 1, TRAP_HINGE_Z), (0, 1, 0), CH_W + 2))
    for tx0, ty0, tx1, ty1 in (TRAP_LATCH_TAB, TRAP_STRING_TAB):
        td = td.union(box(tx0, ty0, TRAP_Z0, tx1, ty1, TRAP_Z0 + CH_FLOOR))
    sx0, sy0, sx1, sy1 = TRAP_STRING_TAB
    td = td.cut(cyl(TRAP_STRING_HOLE_D, ((sx0 + sx1) / 2, (sy0 + sy1) / 2, TRAP_Z0 - 1), (0, 0, 1), CH_FLOOR + 2))
    parts["trapdoor"] = (td, MECH)

    # ---- Entry ramp ----
    parts["entry_ramp"] = (place(channel(ENTRY_LEN), ENTRY_ANCHOR, ENTRY_TILT), RAMP)

    # ---- Support posts ----
    for name, (x0, y0, x1, y1, zt) in POSTS.items():
        if winch_release and name == "post_feed_ramp":
            continue
        parts[name] = (box(x0, y0, z_deck, x1, y1, zt), SUPPORT)
    for name, (x0, x1, py0, qy0, y1, zt, t) in STOP_POSTS.items():
        parts[name] = (box(x0, py0, z_deck, x1, y1, zt).union(box(x0, qy0, zt, x1, y1, zt + t)), SUPPORT)
    x0, x1, py0, qy0, y1, zt, t = TRAP_LATCH_POST
    parts["trap_latch_post"] = (box(x0, py0, z_deck, x1, y1, zt).union(box(x0, qy0, zt, x1, y1, zt + t)), SUPPORT)

    # ---- Marbles ----
    for name, c in marbles.items():
        parts[name] = (cq.Workplane("XY").sphere(MARBLE_D / 2).translate(c), MARBLE)

    return parts


def export(parts, out_dir="output", name="smet_rev3_assembly"):
    os.makedirs(out_dir, exist_ok=True)
    assy = cq.Assembly(name=name)
    for pname, (wp, rgb) in parts.items():
        assy.add(wp, name=pname, color=cq.Color(*rgb))
    step_path = os.path.join(out_dir, f"{name}.step")
    stl_path = os.path.join(out_dir, f"{name}.stl")
    assy.export(step_path)
    compound = cq.Compound.makeCompound([wp.val() for wp, _ in parts.values()])
    cq.exporters.export(compound, stl_path, tolerance=0.02, angularTolerance=0.1)
    return step_path, stl_path


if __name__ == "__main__":
    built = build()
    step, stl = export(built)
    total = sum(wp.val().Volume() for wp, _ in built.values())
    print(f"{len(built)} parts, total volume {total:,.0f} mm^3")
    print("wrote", step)
    print("wrote", stl)
