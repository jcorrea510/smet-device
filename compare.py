"""
Compare the CadQuery rebuild against the original STL.

    python compare.py

* rebuilds the ORIGINAL design (both redesigns off), matches every body of
  the original mesh to a rebuilt part and prints the bounding-box and volume
  difference of each pair, plus the overall bounding box and volume
* lists the parts the redesign adds, changes or removes
* renders the original STL next to the updated design into ./renders/
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import cadquery as cq
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.optimize import linear_sum_assignment

import smet_rev3_assembly as model

ORIGINAL = "SMET_rev3_assembly.stl"
REBUILT = os.path.join("output", "smet_rev3_assembly.stl")
VIEWS = [(25, -60, "iso front-left"), (25, 30, "iso back-right"),
         (0, -90, "front"), (0, 0, "right side"), (90, -90, "top")]


def original_bodies(mesh):
    """Split the original mesh into real bodies.

    The STL contains zero-area sliver triangles (pairs with opposite normals,
    left where the two spiral sections meet) -- these are dropped.  The two
    spiral sections are open where they meet, so they are only closed when
    taken together, and the lever's sealed weight cavity is stored as a
    separate inside-out shell; both are merged with their neighbour so every
    group below is a closed volume."""
    bodies = [b for b in mesh.split(only_watertight=False) if len(b.faces) > 1]
    group_of = list(range(len(bodies)))          # tiny union-find

    def root(i):
        while group_of[i] != i:
            i = group_of[i]
        return i

    for i, b in enumerate(bodies):
        if b.is_watertight and b.volume > 0:
            continue
        # merge with the body whose bounding box overlaps it most
        best, best_ov = None, 0.0
        for j, c in enumerate(bodies):
            if j == i:
                continue
            lo = np.maximum(b.bounds[0], c.bounds[0])
            hi = np.minimum(b.bounds[1], c.bounds[1])
            ov = np.prod(np.clip(hi - lo, 0, None))
            if ov > best_ov:
                best, best_ov = j, ov
        if best is not None:
            group_of[root(i)] = root(best)
    groups = {}
    for i in range(len(bodies)):
        groups.setdefault(root(i), []).append(bodies[i])
    return [trimesh.util.concatenate(g) for g in groups.values()]


def part_mesh(wp):
    verts, tris = wp.val().tessellate(0.02, 0.1)
    return trimesh.Trimesh([(v.x, v.y, v.z) for v in verts], tris, process=True)


def _draw(ax, mesh, color, center, radius, el, az):
    n = mesh.face_normals
    light = np.array([0.4, -0.6, 0.7])
    light /= np.linalg.norm(light)
    shade = 0.30 + 0.70 * np.abs(n @ light)
    cols = np.c_[np.outer(shade, color), np.ones_like(shade)]
    ax.add_collection3d(Poly3DCollection(mesh.triangles, facecolors=cols, edgecolor="none"))
    for k, setter in enumerate((ax.set_xlim, ax.set_ylim, ax.set_zlim)):
        setter(center[k] - radius, center[k] + radius)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(el, az)
    ax.set_proj_type("ortho")
    ax.set_axis_off()


def render_compare(orig, rebuilt, path, title, views=VIEWS, crop=None):
    """Original (top row, blue) vs rebuild (bottom row, orange).
    `crop` = (min_xyz, max_xyz) limits the view to one region."""
    meshes = []
    for m in (orig, rebuilt):
        if crop is not None:
            for k in range(3):
                for bound, sign in ((crop[0][k], 1.0), (crop[1][k], -1.0)):
                    normal = np.zeros(3)
                    normal[k] = sign
                    origin = np.zeros(3)
                    origin[k] = bound
                    m = trimesh.intersections.slice_mesh_plane(m, normal, origin)
        meshes.append(m)
    b = meshes[0].bounds
    center, radius = b.mean(0), (b[1] - b[0]).max() / 2 * 1.02
    fig = plt.figure(figsize=(4.0 * len(views), 8.4))
    for row, (m, color, label) in enumerate(((meshes[0], (0.30, 0.55, 0.85), "original STL"),
                                             (meshes[1], (0.90, 0.50, 0.20), "updated design"))):
        for i, (el, az, name) in enumerate(views):
            ax = fig.add_subplot(2, len(views), row * len(views) + i + 1, projection="3d")
            _draw(ax, m, color, center, radius, el, az)
            ax.set_title(f"{label} - {name}", fontsize=9)
    fig.suptitle(title, fontsize=13)
    plt.subplots_adjust(left=0, right=1, bottom=0, top=0.93, wspace=0, hspace=0.05)
    plt.savefig(path, dpi=90)
    plt.close(fig)


WINCH_PARTS = ["paddle_wheel", "wheel_axle", "string_drum", "fork_wheel", "wheel_stop_pin",
               "winch_string", "seesaw", "fork_seesaw", "seesaw_stop_left", "seesaw_stop_right",
               "marble_3", "lever"]
WINCH_STEPS = ("1. Marble 2 drops into a cup on the wheel and stays there; its weight turns the wheel.   "
               "2. The drum on the same axle winds up the string.\n"
               "3. The string lifts the left end of the seesaw.   "
               "4. The seesaw tips and marble 3 rolls off onto the lever, then on to the cradle.")
WEDGE_PARTS = ["pulley", "pulley_axle", "pulley_arm", "wedge", "wedge_weight", "pulley_string_wedge",
               "pulley_string_trapdoor", "top_ramp", "marble_2"]
WEDGE_STEPS = ("1. The wedge hangs from the pulley string and is jammed into the top ramp between its walls, "
               "holding marble 2.\n"
               "2. Marble 1 tips the trap door, which pulls the other end of the string down.   "
               "3. The wedge is pulled up out of the ramp and marble 2 rolls to the spiral.")


def render_detail(parts, names, path, title, steps, views, crop, extra=None):
    """Close-up of a few parts only, clipped to `crop` = (min_xyz, max_xyz)."""
    fig = plt.figure(figsize=(6 * len(views), 7.5))
    meshes = {n: part_mesh(parts[n][0]) for n in names if n in parts}
    meshes.update(extra or {})
    lo, hi = np.asarray(crop[0], float), np.asarray(crop[1], float)
    center, radius = (lo + hi) / 2, (hi - lo).max() / 2
    for i, (el, az, name) in enumerate(views):
        ax = fig.add_subplot(1, len(views), i + 1, projection="3d")
        for n, m in meshes.items():
            for k in range(3):
                for bound, sign in ((lo[k], 1.0), (hi[k], -1.0)):
                    normal = np.zeros(3)
                    normal[k] = sign
                    origin = np.zeros(3)
                    origin[k] = bound
                    m = trimesh.intersections.slice_mesh_plane(m, normal, origin)
            if len(m.faces):
                color = parts[n][1] if n in parts else (0.15, 0.75, 0.35)
                _draw(ax, m, color, center, radius, el, az)
        ax.set_title(name, fontsize=10)
    fig.suptitle(title, fontsize=13)
    fig.text(0.5, 0.02, steps, ha="center", fontsize=10)
    plt.subplots_adjust(left=0, right=1, bottom=0.08, top=0.93, wspace=0)
    plt.savefig(path, dpi=90)
    plt.close(fig)


def render_winch(parts, path):
    r = model.MARBLE_D / 2
    cup = (model.WHEEL_CX - (model.WHEEL_R - model.WHEEL_PADDLE_T - r), 262.0,
           model.WHEEL_CZ + model.WHEEL_PADDLE_T / 2 + r)
    extra = {"marble_2 (in cup)": part_mesh(cq.Workplane("XY").sphere(r).translate(cup))}
    render_detail(parts, WINCH_PARTS, path, "Wheel & axle: marble 2's weight tips the seesaw", WINCH_STEPS,
                  ((20, -55, "iso front-left"), (0, -90, "front"), (0, 0, "side, from the right")),
                  ((0, 215, 185), (210, 290, 345)), extra)


def render_wedge(parts, path):
    render_detail(parts, WEDGE_PARTS, path, "Wedge: hung from the pulley and jammed into the top ramp",
                  WEDGE_STEPS,
                  ((20, -55, "iso front-left"), (0, -90, "front"), (0, 0, "side, from the right")),
                  ((195, 165, 655), (275, 245, 745)))


def main():
    orig = trimesh.load(ORIGINAL)

    # ---- 1. Fidelity: the original design (winch off) vs the original STL ----
    parts = model.build(winch_release=False, vertical_wedge=False)
    obodies = original_bodies(orig)
    # The original's two spiral sections only form a closed volume together,
    # so compare them against the two rebuilt sections combined.
    spiral = [n for n in parts if n.startswith("spiral_")]
    parts = dict(parts)
    combined = parts[spiral[0]][0].union(parts[spiral[1]][0])
    for n in spiral:
        del parts[n]
    parts["spiral (both sections)"] = (combined, None)
    names = list(parts)
    pmeshes = [part_mesh(parts[n][0]) for n in names]
    cost = np.array([[np.abs(o.bounds - p.bounds).sum() for p in pmeshes] for o in obodies])
    rows, cols = linear_sum_assignment(cost)
    print("1. ORIGINAL DESIGN (WINCH_RELEASE=False, VERTICAL_WEDGE=False) vs the original STL")
    print(f"Original bodies: {len(obodies)}   Rebuilt parts: {len(names)}\n")
    print(f"{'part':22s} {'max bbox err':>12s} {'orig vol':>12s} {'new vol':>12s} {'vol err':>8s}")
    worst_bb = 0.0
    for r, c in sorted(zip(rows, cols), key=lambda rc: names[rc[1]]):
        o, n = obodies[r], names[c]
        bb = np.abs(o.bounds - pmeshes[c].bounds).max()
        ov, nv = o.volume, parts[n][0].val().Volume()
        worst_bb = max(worst_bb, bb)
        print(f"{n:22s} {bb:12.3f} {ov:12.1f} {nv:12.1f} {100 * (nv - ov) / ov:7.2f}%")
    unmatched = set(range(len(names))) - set(cols)
    if unmatched:
        print("Unmatched rebuilt parts:", [names[i] for i in unmatched])
    print(f"\nWorst per-part bounding-box deviation: {worst_bb:.3f} mm")

    rebuilt_orig = trimesh.util.concatenate(pmeshes)
    ov = sum(b.volume for b in obodies)
    nv = sum(wp.val().Volume() for wp, _ in parts.values())
    print("\nOverall            original STL             rebuild")
    print(f"bbox min   {np.round(orig.bounds[0], 3)!s:24s} {np.round(rebuilt_orig.bounds[0], 3)}")
    print(f"bbox max   {np.round(orig.bounds[1], 3)!s:24s} {np.round(rebuilt_orig.bounds[1], 3)}")
    print(f"volume     {ov:,.0f} mm^3{'':9s} {nv:,.0f} mm^3  ({100 * (nv - ov) / ov:+.3f}%)")

    # ---- 2. What the wheel & axle redesign changes ----
    old = model.build(winch_release=False, vertical_wedge=False)
    new = model.build()
    added = [n for n in new if n not in old]
    removed = [n for n in old if n not in new]
    changed = []
    for n in new:
        if n in old:
            a, b = old[n][0].val(), new[n][0].val()
            ba, bb = a.BoundingBox(), b.BoundingBox()
            diff = max(abs(ba.xmin - bb.xmin), abs(ba.ymin - bb.ymin), abs(ba.zmin - bb.zmin),
                       abs(ba.xmax - bb.xmax), abs(ba.ymax - bb.ymax), abs(ba.zmax - bb.zmax))
            if diff > 1e-3 or abs(a.Volume() - b.Volume()) > 1e-3:
                changed.append(n)
    print("\n2. REDESIGN (wheel & axle tips the seesaw, wedge hangs from the pulley)")
    print("added:  ", ", ".join(added) or "-")
    print("changed:", ", ".join(changed) or "-")
    print("removed:", ", ".join(removed) or "-")
    print(f"{len(old) - len(changed) - len(removed)} of {len(old)} original parts are untouched")

    if not os.path.exists(REBUILT):
        model.export(new)
    rebuilt = trimesh.load(REBUILT)
    if "--no-render" not in sys.argv:
        os.makedirs("renders", exist_ok=True)
        render_compare(orig, rebuilt, "renders/compare_overview.png",
                       "Whole assembly: original (top) vs updated design (bottom)")
        render_compare(orig, rebuilt, "renders/compare_wheel_axle.png",
                       "Wheel & axle: original (top) vs winch that tips the seesaw (bottom)",
                       views=[(20, -55, "iso front-left"), (0, -90, "front"), (0, 0, "right side")],
                       crop=((-10, 210, 230), (200, 290, 350)))
        render_winch(new, "renders/winch_detail.png")
        render_wedge(new, "renders/wedge_detail.png")
        detail = [(30, -60, "iso"), (20, 150, "iso back"), (90, -90, "top")]
        render_compare(orig, rebuilt, "renders/compare_spiral_top.png",
                       "Spiral, top ramp, wedge and pulley",
                       views=detail, crop=((20, 0, 570), (305, 290, 745)))
        render_compare(orig, rebuilt, "renders/compare_mechanisms.png",
                       "Wheel, seesaw, lever, cradle and trap door",
                       views=[(25, -60, "iso"), (15, -120, "iso front-right"), (0, -90, "front")],
                       crop=((-10, 140, 180), (305, 290, 345)))
        print("\nwrote renders/compare_*.png")


if __name__ == "__main__":
    main()
