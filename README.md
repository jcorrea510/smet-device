# SMET rev3: parametric CadQuery rebuild

`SMET_rev3_assembly.stl` is a mesh of the whole simple-machines marble tower, with no CAD source.
`smet_rev3_assembly.py` rebuilds it as an editable CadQuery model. All dimensions are variables in
millimetres at the top of the file.

```bash
pip install -r requirements.txt
python smet_rev3_assembly.py   # writes output/smet_rev3_assembly.step and .stl
python compare.py              # checks the rebuild against the original, writes renders/
python motion_check.py         # collision + motion check for the wheel & axle winch
```

* `output/smet_rev3_assembly.step`: 63 named, coloured parts (64 solids, because `fork_wheel` is two
  uprights). Import it into Onshape.
* `output/smet_rev3_assembly.stl`: one mesh for slicing and printing.
* `renders/`: side-by-side previews (original STL = blue, updated design = orange), the labelled
  `winch_detail.png`, and `comparison_report.txt`.

## What's in the model

The tower is 312.0 × 304.8 × 757.0 mm overall (X × Y × Z). The base is 304.8 mm (12 in) square, and
marble 1 (arriving from the previous group) overhangs the left edge by 7.2 mm. The machines, top to bottom:

| Simple machine  | Parts |
|-----------------|-------|
| Pulley          | `pulley` spool on `pulley_axle`, held by `pulley_arm` |
| Wedge           | `wedge` (plus `wedge_disc`) on the `top_ramp` |
| Screw           | `spiral_upper` / `spiral_lower`: a 2-turn helical channel on three ¼ in dowels |
| Inclined planes | `entry_ramp`, `top_ramp`, `transfer_chute`, 6 `zigzag_ramp_*`, `feed_ramp` |
| Wheel & axle    | `paddle_wheel` + `string_drum` on a shared `wheel_axle`: a winch that releases marble 3 (see below) |
| Levers          | `seesaw`, the counter-weighted `lever`, the tipping `cradle` + `rocker`, and the hinged `trapdoor` |

Every straight ramp shares one U-channel profile: 25.4 mm wide, 2 mm walls, 3.2 mm floor, walls 10 mm tall.

## How the machine runs

1. **Marble 1** comes from the previous group. It rolls down the `entry_ramp` (inclined plane) from the
   left edge of the base onto the `trapdoor` (lever).
2. The trap door tips and pulls a string over the `pulley` at the top. That lifts the `wedge`, which was
   holding **marble 2** at the top of the `top_ramp`.
3. Marble 2 rolls down the `spiral` (screw), the `transfer_chute` and the six `zigzag_ramp`s (inclined
   planes).
4. Marble 2 drops into a cup on the **wheel & axle** and stays there. Its weight turns the wheel, and
   that releases **marble 3**. See the next section.
5. Marble 3 rolls down the `feed_ramp` onto the `seesaw` (lever), then onto the counter-weighted `lever`.
   That tips it into the `cradle` at the right edge, which hands it to the next group.

Each marble does its own part of the run. Marble 1 starts the machine, marble 2 does the top half, and
marble 3 does the bottom half. Each one is started by the machine before it.

## Wheel & axle redesign

In the original design the paddle wheel spun loose on a pin. Marble 2 knocked it round and fell off onto
the feed ramp, so the wheel didn't pass any energy on. Now the wheel is a winch (`renders/winch_detail.png`):

1. Marble 2 drops through the lowest zig-zag ramp into the left paddle. Each paddle now has a 7 mm lip at
   its tip, which makes a cup, so marble 2 stays on the wheel. Its weight turns the wheel about 80°, until
   the existing stop pin catches it. The marble can't spill out before about 83°, so it stays in the cup
   and the wheel stays turned.
2. The wheel is glued to its axle, so the axle turns too. A small drum on the front of the axle
   (14 mm across) winds up the string.
3. The string lifts the front end of the `release_lever`. This is a 4 mm wooden stick under the feed ramp
   that pivots on a nail in the wheel fork's front upright. Its back end carries a peg that pokes 4 mm up
   through a slot in the feed ramp. When the front end goes up, the peg drops down out of the way
   (16 mm at 80° of wheel turn, and already more than 4 mm at 20°).
4. **Marble 3** was resting against the peg at the top of the feed ramp. It now rolls to the seesaw and
   runs the rest of the machine. A penny taped under the lever's front end keeps the peg up until then.

Why it's a wheel & axle: marble 2 pushes on the wheel about 22 mm from the centre, and the string pulls
7.5 mm from it, so the wheel multiplies marble 2's force about 3 times. It takes about 3.2 g of pull to
lift the penny end of the lever. Marble 2 (about 5.2 g) can easily supply that, about 5 times over. The
penny holds the peg up about 7 times harder than marble 3 pushes it down. (Estimates assume pine sticks,
a ⅝ in glass marble and a US penny.)

**What to build.** Nearly everything new is wood or hardware:

| Part | Material |
|------|----------|
| `release_lever` (stick + peg) | 4 mm square wood strip (craft stick or basswood) |
| `release_nail` | small nail or brad, 2 mm, into the existing fork upright |
| `wheel_axle` | 3 mm bamboo skewer or steel rod, glued into the wheel and drum |
| `counterweight_penny` | one penny, taped on |
| `winch_string` | thread, tied to the lever and wound once on the drum |
| `string_drum` | small 3D print (or a slice of ⅝ in dowel with flanges glued on) |
| `paddle_wheel` | reprint the existing wheel with the taller lips |
| `feed_ramp` | the same ramp, plus a 6 × 10 mm slot for the peg |

The rest of the model is unchanged, and nothing collides. `python motion_check.py` checks:
- marble 2 lands in the cup;
- the wheel turns to the stop pin;
- the lever swings freely;
- marble 3 rolls clear under the turned wheel all the way to the seesaw.

Set `WINCH_RELEASE = False` to get the original paddle wheel back.

## Adjustable dimensions (top of `smet_rev3_assembly.py`)

| Group | Variables | Default |
|-------|-----------|---------|
| Frame | `BASE_W`, `BASE_D`, `BASE_T` | 304.8, 304.8, 19.05 |
| | `POST_SIZE`, `FRAME_H` | 19.05, 757.001 |
| | `BACKING_T` (board between posts and ramps) | 11.05 |
| Channel profile | `CH_W`, `CH_WALL`, `CH_FLOOR`, `CH_WALL_H` | 25.4, 2.0, 3.2, 10.0 |
| | `END_WALL_T`, `END_WALL_H` | 2.0, 14.0 |
| Zig-zag ramps | `ZIG_COUNT`, `ZIG_TILT` (deg), `ZIG_LEN` | 6, 3.0, 290.8 |
| | `ZIG_DROP_HOLE`, `ZIG_Z0`, `ZIG_PITCH` (vertical spacing), `ZIG_X_INSET` | 20.8, 344.865, 39.039, 7.366 |
| Spiral | `SPIRAL_R_MID`, `SPIRAL_W`, `SPIRAL_PITCH` (drop per turn) | 80, 25.4, 35 |
| | `SPIRAL_INNER_WALL_H`, `SPIRAL_OUTER_WALL_H` | 8, 18 |
| | `SPIRAL_UPPER_SWEEP`, `SPIRAL_LOWER_SWEEP` (deg), `SPIRAL_TOP_Z` | 350, 340, 657.3 |
| | `TAB_W`, `TAB_R_IN`, `TAB_R_OUT`, `TAB_HOLE_D` | 12, 92.2, 108.5, 6.7 |
| Dowels | `DOWEL_D`, `DOWEL_R`, `DOWEL_ABOVE_TAB` | 6.35, 102, 4 |
| Pins / pivots | `PIN_D`, `PIVOT_HOLE_D`, `FORK_T`, `FORK_PIN_DROP` | 3.0, 3.5, 8.0, 4.0 |
| Paddle wheel | `WHEEL_R`, `WHEEL_HUB_D`, `WHEEL_PADDLE_T`, `WHEEL_PADDLES` | 32, 16, 2.4, 4 |
| Seesaw | `SEESAW_LEN`, `SEESAW_TILT`, `SEESAW_WEIGHT_D`, `SEESAW_WEIGHT_T` | 90, 1.0, 19, 1.52 |
| Lever | `LEVER_LEN`, `LEVER_BOX_H`, `LEVER_BOX_WALL`, `LEVER_WEIGHT_D`, `LEVER_WEIGHT_H` | 137, 13, 1, 19, 10.64 |
| Trap door | `TRAP_LEN`, `TRAP_KNUCKLE_R`, `TRAP_GATE_T`, `TRAP_STRING_HOLE_D` | 114, 3.5, 3.0, 1.8 |
| Other ramps | `FEED_TILT`/`FEED_LEN`, `ENTRY_TILT`/`ENTRY_LEN`, `TOP_TILT`/`TOP_LEN`, `TRANSFER_TILT`/`TRANSFER_LEN` | 5/95.965, −3/175.941, 3/159.218, 5/151.413 |
| Wedge | `WEDGE_H_LOW`, `WEDGE_H_HIGH` | 6, 18 |
| Pulley | `PULLEY_FLANGE_D`, `PULLEY_HUB_D`, `PULLEY_HUB_L`, `PULLEY_FLANGE_T` | 28, 20, 10, 1.5 |
| Winch | `WINCH_RELEASE`, `WHEEL_LIP_H`, `DRUM_D`, `DRUM_FLANGE_D`, `DRUM_L` | True, 7, 14, 24, 8 |
| | `AXLE_Y`, `DRUM_Y0`, `STRING_D` | (224, 286), 224, 1.0 |
| Release lever | `LEVER_STICK`, `RELEASE_PIVOT_Y`, `RELEASE_PEG_Y`, `RELEASE_FRONT_Y` | 4, 242, 262, 222 |
| | `RELEASE_PEG_UP`, `RELEASE_NAIL_D`, `RELEASE_SLOT` (x, y) | 4, 2, (6, 10) |
| | `COIN_D`, `COIN_T`, `COIN_Y` (penny counterweight) | 19.05, 1.52, 226 |
| Marbles | `MARBLE_D` | 15.875 (⅝ in) |

Positions are also variables: the `*_ANCHOR` points, the pivot coordinates and the `POSTS`, `STOP_POSTS`
and `FORKS` tables. The support posts are separate absolute coordinates. If you move a ramp or change its
tilt, update the post that holds it up, then re-run `compare.py` or check the renders.

## How close is the rebuild?

`compare.py` checks the rebuild against the original STL with `WINCH_RELEASE = False`, so the check is
not affected by the redesign. From `renders/comparison_report.txt`:

* All 55 bodies in the original mesh match a rebuilt part. The worst bounding-box difference on any part is 0.007 mm.
* The overall bounding box matches to within 0.005 mm.
* Total volume is 3,406,020 mm³ vs 3,404,209 mm³ (+0.05%). All of the difference comes from true cylinders
  and spheres in the rebuild replacing the STL's faceted ones (12- to 24-sided pins, dowels and weights).

## Notes on the original mesh

* The zero-area one-triangle "bodies" and the open ends of the two spiral sections are not damage. The two
  sections share an end face, so a mesh split separates those triangles. The rebuild's STL does exactly the same.
* The lever's counterweight box is sealed with a 19 mm weight inside. In the STL the cavity shows up as a
  separate inside-out box.
