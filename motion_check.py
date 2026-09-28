"""
Collision and motion check for the wheel & axle winch.

    python motion_check.py

* static check: no two parts overlap in the updated design, other than
  overlaps that were already in the original design
* turns the paddle wheel and tips the release tray through their motion and
  reports the first part they touch
* prints how far the string lifts and how far the tray tips for a few
  wheel angles
"""

import itertools
import math

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
    print("overlaps already in the original design:", before)
    print("new overlaps:", new or "none")

    static = {n: w.val() for n, (w, _) in parts.items()}

    def hits(shape, skip):
        found = []
        for n, s in static.items():
            if n not in skip:
                v = shape.intersect(s).Volume()
                if v > 0.01:
                    found.append((n, round(v, 2)))
        return found

    # Marble 1 pushes the left side of the wheel down: counter-clockwise seen
    # from the front, which is a negative rotation about +Y.
    wheel = parts["paddle_wheel"][0]
    for deg in range(0, 95, 5):
        w = wheel.rotate((m.WHEEL_CX, 0, m.WHEEL_CZ), (m.WHEEL_CX, 1, m.WHEEL_CZ), -deg).val()
        h = hits(w, {"paddle_wheel", "wheel_axle"})
        if h:
            print(f"wheel turns freely until {deg} deg, then touches {h}")
            break
    else:
        print("wheel turns 90 deg with no contact")

    # The tray tips forward (front end down): positive rotation about +Y.
    tray = parts["release_tray"][0]
    xp, zp = m.TRAY_PIVOT
    for deg in range(0, 41, 2):
        t = tray.rotate((xp, 0, zp), (xp, 1, zp), deg).val()
        h = hits(t, {"release_tray", "winch_string", "marble_2"})
        if h:
            print(f"tray tips {deg} deg forward, then touches {h}")
            break
    else:
        print("tray tips 40 deg forward with no contact")

    string_x = m.WHEEL_CX + m.DRUM_D / 2 + m.STRING_D / 2
    arm = abs((string_x - xp) / math.cos(math.radians(m.TRAY_REST_TILT)))
    for wdeg in (30, 45, 68):
        lift = m.DRUM_D / 2 * math.radians(wdeg)
        tilt = math.degrees(math.asin(min(1.0, lift / arm)))
        print(f"wheel {wdeg} deg: string lifts {lift:.1f} mm -> tray tips {tilt:.1f} deg "
              f"({tilt - m.TRAY_REST_TILT:+.1f} deg past level)")


if __name__ == "__main__":
    main()
