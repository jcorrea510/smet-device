"""
Collision and motion check for the wheel & axle winch.

    python motion_check.py

1. static: no two parts overlap in the updated design, apart from overlaps
   that were already in the original design
2. marble 2 lands in the left paddle's cup; the wheel (carrying marble 2)
   turns until it touches something -- it should be the existing stop pin
3. how far the string lifts and the peg drops for a few wheel angles
4. the release lever swings its peg down through the slot without hitting
   anything
5. marble 3 rolls down the feed ramp to the seesaw with the wheel turned and
   marble 2 hanging in its cup, without touching anything but the ramp
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


def main():
    parts = m.build(winch_release=True)
    before = overlaps(m.build(winch_release=False))
    new = {k: v for k, v in overlaps(parts).items() if k not in before}
    print("1. overlaps already in the original design:", before)
    print("   new overlaps:", new or "none")

    static = {n: w.val() for n, (w, _) in parts.items()}

    def hits(shape, skip):
        found = []
        for n, s in static.items():
            if n not in skip:
                v = shape.intersect(s).Volume()
                if v > 0.01:
                    found.append((n, round(v, 2)))
        return found

    # Marble 2 resting in the cup of the left paddle (lip at the tip)
    r = m.MARBLE_D / 2
    d = m.WHEEL_R - m.WHEEL_PADDLE_T - r
    m2 = cq.Workplane("XY").sphere(r).translate(
        (m.WHEEL_CX - d, 262.0, m.WHEEL_CZ + m.WHEEL_PADDLE_T / 2 + r))
    loaded = parts["paddle_wheel"][0].union(m2)
    print("\n2. marble 2 in the cup at rest touches:",
          hits(m2.val(), {"paddle_wheel", "marble_2"}) or "nothing")
    stop_deg = None
    for deg in range(0, 95, 2):
        w = loaded.rotate((m.WHEEL_CX, 0, m.WHEEL_CZ), (m.WHEEL_CX, 1, m.WHEEL_CZ), -deg).val()
        h = hits(w, {"paddle_wheel", "wheel_axle", "marble_2"})
        if h:
            print(f"   wheel + marble 2 turn freely until {deg} deg, then touch {h}")
            stop_deg = deg
            break
    else:
        print("   wheel turns 90 deg with no contact")
        stop_deg = 90

    # String lift -> lever -> peg drop
    drum_y = m.DRUM_Y0 + m.DRUM_FLANGE_T + m.DRUM_L / 2
    front = m.RELEASE_PIVOT_Y - drum_y
    back = m.RELEASE_PEG_Y - m.RELEASE_PIVOT_Y
    print("\n3. string lift and peg drop (peg sticks up "
          f"{m.RELEASE_PEG_UP} mm, so it must drop more than that)")
    for wdeg in (20, 30, 45, stop_deg):
        lift = m.DRUM_D / 2 * math.radians(wdeg)
        tilt = math.degrees(math.asin(min(1.0, lift / front)))
        drop = back * math.sin(math.radians(tilt))
        print(f"   wheel {wdeg:3d} deg: string lifts {lift:4.1f} mm, lever tips {tilt:4.1f} deg, "
              f"peg drops {drop:4.1f} mm")

    # Release lever swinging (peg end down = negative rotation about +X)
    lever = parts["release_lever"][0]
    pb = static["release_nail"].BoundingBox()
    pz = (pb.zmin + pb.zmax) / 2
    final_tilt = math.degrees(math.asin(min(1.0, m.DRUM_D / 2 * math.radians(stop_deg) / front)))
    for deg in range(0, int(final_tilt) + 3, 2):
        lv = lever.rotate((0, m.RELEASE_PIVOT_Y, pz), (1, m.RELEASE_PIVOT_Y, pz), -deg).val()
        h = hits(lv, {"release_lever", "release_nail", "counterweight_penny", "winch_string", "marble_3"})
        if h:
            print(f"\n4. lever touches {h} at {deg} deg")
            break
    else:
        print(f"\n4. lever swings {int(final_tilt) + 2} deg with no contact")

    # Marble 3 rolling down the feed ramp past the turned wheel
    wheel_end = loaded.rotate((m.WHEEL_CX, 0, m.WHEEL_CZ), (m.WHEEL_CX, 1, m.WHEEL_CZ), -stop_deg).val()
    lever_end = lever.rotate((0, m.RELEASE_PIVOT_Y, pz), (1, m.RELEASE_PIVOT_Y, pz), -final_tilt).val()
    t = math.radians(m.FEED_TILT)
    m3 = static["marble_3"].Center()
    blocked = None
    for step in range(0, 60):
        x = m3.x + step
        if x > 100:
            break
        z = m3.z - step * math.tan(t)
        ball = cq.Workplane("XY").sphere(r - 0.05).translate((x, m3.y, z)).val()
        h = [(n, v) for n, v in hits(ball, {"marble_3", "feed_ramp", "paddle_wheel", "release_lever"})]
        for n, shp in (("turned wheel + marble 2", wheel_end), ("dropped lever", lever_end)):
            if ball.intersect(shp).Volume() > 0.01:
                h.append((n, "hit"))
        if h:
            blocked = (round(x, 1), h)
            break
    if blocked:
        print(f"\n5. marble 3 blocked at x={blocked[0]}: {blocked[1]}")
    else:
        print(f"\n5. marble 3 rolls clear from x={m3.x:.1f} to x=100 (the seesaw starts at x=105)")


if __name__ == "__main__":
    main()
