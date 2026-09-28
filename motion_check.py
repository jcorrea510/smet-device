"""
Collision and motion check for the redesigned wedge and wheel & axle.

    python motion_check.py

1. static: no two parts overlap, apart from overlaps already in the
   original design
2. trap door -> pulley -> wedge: the trap door tips until its stop; the
   wedge is pulled up by the same amount, clears marble 2 without hitting the
   pulley, and marble 2 rolls clear down the top ramp to the spiral
3. marble 2 -> wheel & axle: marble 2 sits in the left paddle's cup and the
   wheel turns until it touches something (should be the existing stop pin)
4. wheel & axle -> seesaw: how far the winding string tips the seesaw for a
   few wheel angles; the seesaw (with marble 3) tips to its right-hand stop
   without hitting anything else
5. seesaw -> marble 3: once tipped, marble 3 rolls along the seesaw and off
   its right end without hitting anything
"""

import itertools
import math

import cadquery as cq

import smet_rev3_assembly as m


def overlaps(parts):
    items = [(n, w.val()) for n, (w, _) in parts.items()]
    out = {}
    for (a, sa), (b, sb) in itertools.combinations(items, 2):
        ba, bb = sa.BoundingBox(), sb.BoundingBox()
        if (ba.xmax < bb.xmin or bb.xmax < ba.xmin or ba.ymax < bb.ymin or
                bb.ymax < ba.ymin or ba.zmax < bb.zmin or bb.zmax < ba.zmin):
            continue
        v = sa.intersect(sb).Volume()
        if v > 0.01:
            out[(a, b)] = round(v, 2)
    return out


def rot_y(shape, x, z, deg):
    """Rotate about a line parallel to +Y through (x, z).  Positive angles
    lower the +X side."""
    return shape.rotate((x, 0, z), (x, 1, z), deg)


def main():
    parts = m.build()
    before = overlaps(m.build(winch_release=False, vertical_wedge=False))
    new = {k: v for k, v in overlaps(parts).items() if k not in before}
    print("1. overlaps already in the original design:", before)
    print("   new overlaps:", new or "none")

    static = {n: w.val() for n, (w, _) in parts.items()}
    strings = {"pulley_string_wedge", "pulley_string_trapdoor", "winch_string"}

    def hits(shape, skip):
        found = []
        for n, s in static.items():
            if n not in skip and n not in strings:
                v = shape.intersect(s).Volume()
                if v > 0.01:
                    found.append((n, round(v, 2)))
        return found

    r = m.MARBLE_D / 2

    # ---- 2. trap door -> pulley -> wedge -> marble 2 ----
    trap = parts["trapdoor"][0]
    hx, hz = m.TRAP_X0, m.TRAP_HINGE_Z
    trap_deg = None
    for deg in range(0, 60):
        h = hits(rot_y(trap, hx, hz, deg).val(), {"trapdoor", "fork_trapdoor", "marble_1"})
        if h:
            trap_deg = deg
            break
    tx = (m.TRAP_STRING_TAB[0] + m.TRAP_STRING_TAB[2]) / 2 - hx
    pull = tx * math.sin(math.radians(trap_deg))
    print(f"\n2. trap door tips {trap_deg} deg before touching {h}: "
          f"pulls the string {pull:.1f} mm, so the wedge lifts {pull:.1f} mm")
    wedge = parts["wedge"][0].union(parts["wedge_weight"][0])
    wb = static["wedge"].BoundingBox()
    m2 = static["marble_2"].Center()
    need = (m2.z + r) - wb.zmin
    print(f"   wedge must lift {need:.1f} mm to clear marble 2 "
          f"({'OK' if pull > need else 'NOT ENOUGH'})")
    lifted = wedge.translate((0, 0, pull)).val()
    print("   lifted wedge (with its washers) touches:", hits(lifted, {"wedge", "wedge_weight"}) or "nothing")
    t3 = math.tan(math.radians(m.TOP_TILT))
    blocked = None
    for step in range(0, 200, 2):
        x = m2.x - step
        if x < m.TOP_ANCHOR[0] + r:
            break
        ball = cq.Workplane("XY").sphere(r - 0.05).translate((x, m2.y, m2.z - step * t3)).val()
        h = hits(ball, {"marble_2", "top_ramp", "wedge", "wedge_weight"})
        if ball.intersect(lifted).Volume() > 0.01:
            h.append(("lifted wedge", "hit"))
        if h:
            blocked = (round(x, 1), h)
            break
    print("   marble 2 rolling to the spiral:",
          f"blocked at x={blocked[0]}: {blocked[1]}" if blocked else "clear")

    # ---- 3. marble 2 turns the wheel ----
    d = m.WHEEL_R - m.WHEEL_PADDLE_T - r
    cup = cq.Workplane("XY").sphere(r).translate((m.WHEEL_CX - d, 262.0, m.WHEEL_CZ + m.WHEEL_PADDLE_T / 2 + r))
    loaded = parts["paddle_wheel"][0].union(cup)
    print("\n3. marble 2 in the cup at rest touches:", hits(cup.val(), {"paddle_wheel"}) or "nothing")
    stop_deg = 90
    for deg in range(0, 95, 2):
        # anticlockwise seen from the front = lowers the -X side = negative here
        h = hits(rot_y(loaded, m.WHEEL_CX, m.WHEEL_CZ, -deg).val(), {"paddle_wheel", "wheel_axle"})
        if h:
            stop_deg = deg
            print(f"   wheel + marble 2 turn freely until {deg} deg, then touch {h}")
            break

    # ---- 4. wheel & axle -> string -> seesaw ----
    px, pz = m.SEESAW_PIVOT
    tab_u = sum(m.SEESAW_TAB_U) / 2
    n_top = m.SEESAW_FLOOR_ABOVE + m.CH_FLOOR
    rho = m.DRUM_D / 2 + m.STRING_D / 2

    def tab_point(extra_deg):
        """Tab hole position after lifting the seesaw's left end by extra_deg."""
        a = math.radians(m.SEESAW_TILT - extra_deg)
        return (px + tab_u * math.cos(a) - n_top * math.sin(a), pz + tab_u * math.sin(a) + n_top * math.cos(a))

    def free_length(extra_deg):
        gx, gz = tab_point(extra_deg)
        return math.sqrt((gx - m.WHEEL_CX) ** 2 + (gz - m.WHEEL_CZ) ** 2 - rho ** 2)

    seesaw = parts["seesaw"][0].union(parts["marble_3"][0])
    tip_deg = None
    for deg10 in range(0, 300, 5):
        deg = deg10 / 10
        # lifting the left end = lowering the +X side = positive here
        h = hits(rot_y(seesaw, px, pz, deg).val(), {"seesaw", "marble_3", "fork_seesaw"})
        if h:
            tip_deg = deg
            break
    print(f"\n4. seesaw starts tilted {m.SEESAW_TILT} deg (left end down). It can tip {tip_deg} deg "
          f"before touching {h};\n   marble 3 starts rolling once it is past level.")
    for wdeg in range(10, stop_deg + 1, 5):
        wound = rho * math.radians(wdeg)
        extra = 0.0
        while extra < tip_deg and free_length(0) - free_length(extra) < wound:
            extra += 0.05
        now = m.SEESAW_TILT - extra
        print(f"   wheel {wdeg:3d} deg: string winds {wound:4.1f} mm -> seesaw tips {extra:4.1f} deg "
              f"(now {now:+.1f} deg, {'marble 3 rolls' if now < -0.5 else 'marble 3 waits'})")
        if extra >= tip_deg:
            print("   the seesaw is on its stop, so the string holds the wheel here (marble 2 stays in its cup)")
            break

    # ---- 5. marble 3 rolls off the tipped seesaw ----
    a = math.radians(m.SEESAW_TILT - tip_deg)
    tipped = rot_y(parts["seesaw"][0], px, pz, tip_deg).val()
    m3 = static["marble_3"].Center()
    u0 = -m.SEESAW_LEN / 2 + m.END_WALL_T + r
    blocked = None
    for step in range(0, int(m.SEESAW_LEN - m.END_WALL_T - r) + 1, 2):
        u, n = u0 + step, n_top + r
        x = px + u * math.cos(a) - n * math.sin(a)
        z = pz + u * math.sin(a) + n * math.cos(a)
        ball = cq.Workplane("XY").sphere(r - 0.05).translate((x, m3.y, z)).val()
        h = hits(ball, {"seesaw", "marble_3"})
        if ball.intersect(tipped).Volume() > 0.01:
            h.append(("tipped seesaw", "hit"))
        if h:
            blocked = (round(x, 1), h)
            break
    print("\n5. marble 3 rolling off the tipped seesaw:",
          f"blocked at x={blocked[0]}: {blocked[1]}" if blocked else "clear to the right end (drops onto the lever)")


if __name__ == "__main__":
    main()
