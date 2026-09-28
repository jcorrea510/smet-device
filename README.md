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

* `output/smet_rev3_assembly.step`: 62 named, coloured parts (63 solids, because `fork_wheel` is two
  uprights). Import it into Onshape.
* `output/smet_rev3_assembly.stl`: one mesh for slicing and printing.
* `renders/`: side-by-side previews (original STL = blue, updated design = orange), the labelled
  `winch_detail.png`, and `comparison_report.txt`.

## What's in the model

The tower is 312.0 × 304.8 × 757.0 mm overall (X × Y × Z). The base is 304.8 mm (12 in) square, and one
marble overhangs the left edge by 7.2 mm. The machines, top to bottom:

| Simple machine  | Parts |
|-----------------|-------|
| Pulley          | `pulley` spool on `pulley_axle`, held by `pulley_arm` |
| Wedge           | `wedge` (plus `wedge_disc`) on the `top_ramp` |
| Screw           | `spiral_upper` / `spiral_lower`: a 2-turn helical channel on three ¼ in dowels |
| Inclined planes | 6 `zigzag_ramp_*`, plus `transfer_chute`, `feed_ramp`, `exit_ramp` |
| Wheel & axle    | `paddle_wheel` + `string_drum` on a shared `wheel_axle`: a winch that releases marble 2 (see below) |
| Levers          | `seesaw`, the counter-weighted `lever`, the tipping `cradle` + `rocker`, and the hinged `trapdoor` |

Every straight ramp shares one U-channel profile: 25.4 mm wide, 2 mm walls, 3.2 mm floor, walls 10 mm tall.

## Wheel & axle redesign: the winch

In the original design the paddle wheel spun loose on a fixed pin. Marble 1 tipped it and fell off, so no
energy went anywhere else. Now the wheel is a winch whose work starts the second half of the machine:

1. Marble 1 drops through the lowest zig-zag ramp into a paddle. The paddles now have a 5 mm lip, so the
   marble rides the wheel down (about 70°) before spilling onto the feed ramp as before.
2. The wheel is fixed to a 3 mm axle that turns in the fork and a new front bearing post. A 16 mm string
   drum on the front of the axle turns with the wheel and winds up the string.
3. The string lifts the tail of the `release_tray`, which pivots above the exit ramp. The tray tips forward.
4. Marble 2, which used to sit loose at the top of the exit ramp, rolls out onto the exit ramp and runs on
   to the trap door.

Why it counts as a wheel & axle: marble 1 pushes on the wheel 20–32 mm from the axle, and the string pulls
8.5 mm from it (the drum radius plus half the string). That multiplies the force by roughly 2.4–3.8 times.
Tipping the loaded tray takes about 5.3 g of pull on the string, which is more than marble 1 weighs
(about 5.2 g). Marble 1 couldn't tip the tray by pulling a string directly, but it can through the wheel &
axle. That's the energy transfer: marble 1's potential energy → the wheel turning → the string lifting
the tray → marble 2 moving. (Estimates assume PLA parts and a glass ⅝ in marble.)

What changed: `paddle_wheel` (lips, bore now fixed to the axle), `fork_wheel` (bearing holes instead of a
fixed pin, so its two uprights are now separate solids), and `marble_2` (now waits in the tray). Added: `wheel_axle`, `string_drum`,
`axle_bearing_post`, `release_tray`, `fork_release_tray` (carries the tray pivot pin and a rest pin),
and `winch_string`. The other 53 parts are unchanged. The model has no collisions: the wheel turns
freely until the existing stop pin catches it at about 80°, and the tray tips 40° forward without
hitting anything.

Set `WINCH_RELEASE = False` to get the original passive paddle wheel back.

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
| Other ramps | `FEED_TILT`/`FEED_LEN`, `EXIT_TILT`/`EXIT_LEN`, `TOP_TILT`/`TOP_LEN`, `TRANSFER_TILT`/`TRANSFER_LEN` | 5/95.965, −3/175.941, 3/159.218, 5/151.413 |
| Wedge | `WEDGE_H_LOW`, `WEDGE_H_HIGH` | 6, 18 |
| Pulley | `PULLEY_FLANGE_D`, `PULLEY_HUB_D`, `PULLEY_HUB_L`, `PULLEY_FLANGE_T` | 28, 20, 10, 1.5 |
| Winch | `WINCH_RELEASE`, `WHEEL_LIP_H`, `DRUM_D`, `DRUM_FLANGE_D`, `DRUM_L` | True, 5, 16, 28, 12 |
| | `AXLE_Y`, `BEARING_POST_Y`, `STRING_D` | (167, 286), (189.2, 197.2), 1.0 |
| Release tray | `TRAY_PIVOT` (x, z), `TRAY_REST_TILT` (deg), `TRAY_FRONT`, `TRAY_BACK`, `TRAY_TAIL` | (74, 216), 5, 10, 19, 7 |
| | `TRAY_REST_U`, `TRAY_FORK_X` | −10, (62, 78) |
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
