# SMET rev3: parametric CadQuery rebuild

`SMET_rev3_assembly.stl` is a mesh of the whole simple-machines marble tower, with no CAD source.
`smet_rev3_assembly.py` rebuilds it as an editable CadQuery model. All dimensions are variables in
millimetres at the top of the file.

```bash
pip install -r requirements.txt
python smet_rev3_assembly.py   # writes output/smet_rev3_assembly.step and .stl
python compare.py              # checks the rebuild against the original, writes renders/
python motion_check.py         # collision + motion check for the wedge and the wheel & axle
```

* `output/smet_rev3_assembly.step`: 59 named, coloured parts (60 solids, because `fork_wheel` is two
  uprights). Import it into Onshape.
* `output/smet_rev3_assembly.stl`: one mesh for slicing and printing.
* `renders/`: side-by-side previews (original STL = blue, updated design = orange), the labelled
  `wedge_detail.png` and `winch_detail.png`, and `comparison_report.txt`.

## What's in the model

The tower is 312.0 × 304.8 × 757.0 mm overall (X × Y × Z). The base is 304.8 mm (12 in) square, and
marble 1 (arriving from the previous group) overhangs the left edge by 7.2 mm. The machines, top to bottom:

| Simple machine  | Parts |
|-----------------|-------|
| Pulley          | `pulley` spool on `pulley_axle`, held by `pulley_arm` |
| Wedge           | `wedge`, hung from the pulley string and jammed into the `top_ramp` (see below) |
| Screw           | `spiral_upper` / `spiral_lower`: a 2-turn helical channel on three ¼ in dowels |
| Inclined planes | `entry_ramp`, `top_ramp`, `transfer_chute`, 6 `zigzag_ramp_*` |
| Wheel & axle    | `paddle_wheel` + `string_drum` on a shared `wheel_axle`: a winch that tips the seesaw (see below) |
| Levers          | `seesaw`, the counter-weighted `lever`, the tipping `cradle` + `rocker`, and the hinged `trapdoor` |

Every straight ramp shares one U-channel profile: 25.4 mm wide, 2 mm walls, 3.2 mm floor, walls 10 mm tall.

## How the machine runs

1. **Marble 1** comes from the previous group. It rolls down the `entry_ramp` (inclined plane) from the
   left edge of the base onto the `trapdoor` (lever).
2. The trap door tips and pulls a string over the `pulley` at the top. The other end of that string holds
   the `wedge`, which is jammed into the `top_ramp` in front of **marble 2**. The pull yanks the wedge up
   out of the ramp.
3. Marble 2 rolls down the `spiral` (screw), the `transfer_chute` and the six `zigzag_ramp`s (inclined
   planes).
4. Marble 2 drops into a cup on the **wheel & axle** and stays there. Its weight turns the wheel, and a
   drum on the same axle winds up a string that lifts the left end of the `seesaw` (lever).
5. The seesaw tips, and **marble 3**, which was waiting on it, rolls off onto the counter-weighted `lever`.
   That tips it into the `cradle` at the right edge, which hands it to the next group.

Each machine moves the next one. Marble 1 runs the trap door, which runs the pulley, which pulls the
wedge. Marble 2 runs the wheel & axle, which moves the seesaw.

## Redesign 1: the wedge (`VERTICAL_WEDGE`)

In the original, the wedge sat loose on the ramp floor, so it didn't really work as a wedge. Now it is a
small wooden wedge (12 mm thick, 20 mm tall, 17 mm wide at the bottom and 27 mm at the top) that hangs
straight down from the pulley string. Its sloping sides are jammed into the top ramp against the top
edges of the two side walls, and its flat face holds marble 2 back.

When marble 1 tips the trap door, the trap door drops about 22° onto its stop and pulls the string down
about 21 mm. The wedge only needs to rise about 15 mm to clear marble 2. Even fully raised, it still
stops about 2.5 mm below the pulley.

The wedge's weight is what holds the trap door level until marble 1 arrives. A wooden wedge on its own
(about 2.6 g) is too light for that. So there is a stack of washers (`wedge_weight`) on its string,
where the original design had a disc. **Tune it by hand:** add washers until the trap door stays up by
itself, then check that marble 1 still tips it. If the trap door is printed solid PLA, the wedge plus
washers needs to weigh about 21–30 g. A lower-infill trap door needs less.

The tall guide walls on the top ramp were only there for the old wedge, so they're gone.

## Redesign 2: the wheel & axle tips the seesaw (`WINCH_RELEASE`)

In the original, the paddle wheel spun loose on a pin. Marble 2 knocked it round and fell off onto the
feed ramp, so the wheel didn't pass any energy on (`renders/winch_detail.png`):

1. Marble 2 drops through the lowest zig-zag ramp into the left paddle. Each paddle now has a 7 mm lip at
   its tip, which makes a cup, so marble 2 stays on the wheel. Its weight turns the wheel. The marble
   can't spill out before about 83°, and the wheel never turns that far.
2. The wheel is glued to its axle, so the axle turns too. A small drum on the front of the axle (8 mm
   across) winds up a string.
3. The string runs down at an angle to a tab on the seesaw's left end and lifts that end. About 10° of
   wheel turn is enough to tip the seesaw past level. At about 45° the seesaw lands on its existing
   right-hand stop, and the string then holds the wheel still.
4. **Marble 3** was resting against a new end wall on the seesaw's left end. Its weight is what used to
   keep the seesaw down, so the seesaw's weight disc is gone. Marble 3 now rolls off the right end onto
   the lever and runs the rest of the machine.

The feed ramp (and its post) is removed, because nothing rolls from the wheel to the seesaw any more.
The wheel & axle now moves the seesaw itself.

Why it's a wheel & axle: marble 2 pushes on the wheel about 22 mm from the centre, and the string pulls
4.5 mm from it (the drum radius plus half the string). The wheel multiplies marble 2's pull almost
5 times. Lifting the seesaw's left end with marble 3 on it takes about 9.3 g of pull on the string, which
is more than marble 2 weighs (about 5.2 g). Marble 2 could not lift it with a plain string, but through
the wheel & axle it has about 2.7 times more force than it needs. (Estimates assume a solid-printed PLA
seesaw and ⅝ in glass marbles.)

**What to build.** New or changed pieces:

| Part | Material |
|------|----------|
| `wedge` | small block of wood, cut to the wedge shape |
| `wedge_weight` | steel washers threaded on the string (tune the number) |
| `pulley_string_*`, `winch_string` | thread |
| `wheel_axle` | 3 mm bamboo skewer or steel rod, glued into the wheel and drum |
| `string_drum` | small 3D print (or a short piece of 5/16 in dowel with card flanges) |
| `paddle_wheel` | reprint of the existing wheel with the taller lips |
| `seesaw` | reprint with the new left end wall and string tab |
| `top_ramp` | the same ramp without the tall guide walls |

The rest of the model is unchanged, and nothing collides. `python motion_check.py` checks all of this:
- the trap door drops, lifts the wedge clear of marble 2 without hitting the pulley, and marble 2 rolls
  down to the spiral;
- marble 2 sits in the wheel's cup and the wheel turns;
- the seesaw tips onto its stop;
- marble 3 rolls off the seesaw onto the lever.

Set `VERTICAL_WEDGE = False` and `WINCH_RELEASE = False` to get the original design back.

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
| Wedge | `VERTICAL_WEDGE`, `WEDGE_T`, `WEDGE_HEIGHT`, `WEDGE_HALF_ANGLE` (deg), `WEDGE_GAP` | True, 12, 20, 15, 1 |
| | `WEDGE_WEIGHT_D`, `WEDGE_WEIGHT_T`, `PULLEY_STRING_D` | 19, 3.04, 1.0 |
| | original block wedge: `WEDGE_H_LOW`, `WEDGE_H_HIGH` | 6, 18 |
| Pulley | `PULLEY_FLANGE_D`, `PULLEY_HUB_D`, `PULLEY_HUB_L`, `PULLEY_FLANGE_T` | 28, 20, 10, 1.5 |
| Winch | `WINCH_RELEASE`, `WHEEL_LIP_H`, `DRUM_D`, `DRUM_FLANGE_D`, `DRUM_L` | True, 7, 8, 16, 8 |
| | `AXLE_Y`, `DRUM_Y0`, `STRING_D` | (224, 286), 224, 1.0 |
| Seesaw (redesign) | `SEESAW_END_WALL_H`, `SEESAW_TAB_U`, `SEESAW_TAB_Y0` | 14, (−45, −39), 226 |
| Marbles | `MARBLE_D` | 15.875 (⅝ in) |

Positions are also variables: the `*_ANCHOR` points, the pivot coordinates and the `POSTS`, `STOP_POSTS`
and `FORKS` tables. The support posts are separate absolute coordinates. If you move a ramp or change its
tilt, update the post that holds it up, then re-run `compare.py` or check the renders.

## How close is the rebuild?

`compare.py` checks the rebuild against the original STL with both redesigns switched off, so the
check is not affected by them. From `renders/comparison_report.txt`:

* All 55 bodies in the original mesh match a rebuilt part. The worst bounding-box difference on any part is 0.007 mm.
* The overall bounding box matches to within 0.005 mm.
* Total volume is 3,406,020 mm³ vs 3,404,209 mm³ (+0.05%). All of the difference comes from true cylinders
  and spheres in the rebuild replacing the STL's faceted ones (12- to 24-sided pins, dowels and weights).

## Notes on the original mesh

* The zero-area one-triangle "bodies" and the open ends of the two spiral sections are not damage. The two
  sections share an end face, so a mesh split separates those triangles. The rebuild's STL does exactly the same.
* The lever's counterweight box is sealed with a 19 mm weight inside. In the STL the cavity shows up as a
  separate inside-out box.
