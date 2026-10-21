"""Blender (headless) render of the OHT fab scene from viewer3d/scene.json.

Usage (inside a container/VM with Blender >= 3.6):
  blender -b -P blender_render.py -- --scene viewer3d/scene.json --t 1230 --out /out/frame.png \
          [--run 0] [--engine CYCLES|BLENDER_EEVEE] [--samples 64] [--res 1920 1080] [--anim T0 T1 FPS]

Builds: floor, ceiling rails (beveled curves), hangers, OHT vehicles (body + hoist frame + FOUP) at the
positions implied by the occupancy log at time t (same interpolation as the web viewer), coloured by
dwell time (green moving -> red stuck). Camera: 3/4 aerial view. Renders one PNG, or a frame sequence
when --anim is given (then encode with ffmpeg outside Blender).
"""
import argparse
import bisect
import json
import math
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ap = argparse.ArgumentParser()
ap.add_argument("--scene", required=True)
ap.add_argument("--run", type=int, default=0)
ap.add_argument("--t", type=float, default=1230.0)
ap.add_argument("--out", default="/out/frame.png")
ap.add_argument("--engine", default="CYCLES")
ap.add_argument("--samples", type=int, default=64)
ap.add_argument("--res", type=int, nargs=2, default=[1920, 1080])
ap.add_argument("--anim", type=float, nargs=3, default=None, help="T0 T1 FPS (sim-seconds, frames per sim-second)")
ap.add_argument("--stuck", type=float, default=30.0)
a = ap.parse_args(argv)

S = 0.001
RAIL_H = 4.0
data = json.load(open(a.scene, encoding="utf-8"))
minx, miny, maxx, maxy = data["bbox"]
cx, cy = (minx + maxx) / 2 * S, (miny + maxy) / 2 * S
W, D = (maxx - minx) * S, (maxy - miny) * S
xy = lambda x, y: (x * S - cx, -(y * S - cy))   # rail y grows "down" in the layout; flip to Blender +Y


# ── scene reset ───────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = a.engine
scene.render.resolution_x, scene.render.resolution_y = a.res
scene.render.image_settings.file_format = "PNG"
if a.engine == "CYCLES":
    scene.cycles.samples = a.samples
    scene.cycles.use_denoising = True
    prefs = bpy.context.preferences.addons.get("cycles")
    if prefs:
        try:
            prefs.preferences.compute_device_type = "CUDA"
            prefs.preferences.get_devices()
            for d in prefs.preferences.devices:
                d.use = True
            scene.cycles.device = "GPU"
        except Exception:
            scene.cycles.device = "CPU"
world = bpy.data.worlds.new("W"); scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.93, 0.97, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 0.6


def mat(name, rgb, rough=0.5, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1) if "Emission Color" in b.inputs else None
        b.inputs["Emission Strength"].default_value = emit
    return m


M_FLOOR = mat("floor", (0.82, 0.84, 0.87), 0.9)
M_RAIL = mat("rail", (0.72, 0.75, 0.78), 0.35, 0.8)
M_HANG = mat("hanger", (0.55, 0.58, 0.62), 0.5, 0.6)
M_BODY = mat("body", (0.96, 0.96, 0.97), 0.35)
M_FRAME = mat("frame", (0.75, 0.78, 0.82), 0.4, 0.6)
M_FOUP = mat("foup", (0.45, 0.5, 0.56), 0.6)
M_TOOL = mat("tool", (0.88, 0.9, 0.93), 0.7)

# floor
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
fl = bpy.context.object; fl.scale = (W + 60, D + 60, 1); fl.data.materials.append(M_FLOOR)

# rails: one curve object with a bevel
curve = bpy.data.curves.new("rails", "CURVE"); curve.dimensions = "3D"
curve.bevel_depth = 0.12; curve.bevel_resolution = 2; curve.fill_mode = "FULL"
for l in data["links"]:
    x1, y1 = xy(l[0], l[1]); x2, y2 = xy(l[2], l[3])
    sp = curve.splines.new("POLY"); sp.points.add(1)
    sp.points[0].co = (x1, y1, RAIL_H, 1); sp.points[1].co = (x2, y2, RAIL_H, 1)
rails = bpy.data.objects.new("rails", curve); rails.data.materials.append(M_RAIL)
scene.collection.objects.link(rails)

# hangers (instances of one cylinder)
bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.4, location=(0, 0, -100))
hang_src = bpy.context.object; hang_src.data.materials.append(M_HANG)
hang_pts = []
for l in data["links"]:
    if l[4] != "LINE":
        continue
    x1, y1 = xy(l[0], l[1]); x2, y2 = xy(l[2], l[3])
    n = max(1, int(math.hypot(x2 - x1, y2 - y1) / 6))
    for k in range(n + 1):
        hang_pts.append((x1 + (x2 - x1) * k / n, y1 + (y2 - y1) * k / n))
for i, (x, y) in enumerate(hang_pts):
    o = bpy.data.objects.new(f"h{i}", hang_src.data); o.location = (x, y, RAIL_H + 0.8)
    scene.collection.objects.link(o)

# tool rows: pale boxes under each intrabay rail (visual only)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -100))
tool_src = bpy.context.object; tool_src.data.materials.append(M_TOOL)
for i, l in enumerate(data["links"][::9]):
    x1, y1 = xy(l[0], l[1]); x2, y2 = xy(l[2], l[3])
    if abs(y2 - y1) < abs(x2 - x1) * 0.3:   # horizontal interbay links: skip
        continue
    o = bpy.data.objects.new(f"tool{i}", tool_src.data)
    o.location = ((x1 + x2) / 2 + 1.6, (y1 + y2) / 2, 1.0); o.scale = (2.0, 2.4, 2.0)
    scene.collection.objects.link(o)

# ── OHT positions from the occupancy log ─────────────────────
run = data["runs"][a.run]
sec_pts = {k: [xy(p[0], p[1]) for p in v] for k, v in data["sections"].items()}
ev_by = {}
for t, o, s in run["events"]:
    ev_by.setdefault(o, []).append((t, s))


def sec_pos(sec, f):
    pts = sec_pts.get(str(sec))
    if not pts:
        return None
    if len(pts) == 1:
        return pts[0][0], pts[0][1], 0.0
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.hypot(pts[i][0] - pts[i-1][0], pts[i][1] - pts[i-1][1]))
    tgt = max(0, min(1, f)) * cum[-1]
    i = 1
    while i < len(cum) - 1 and cum[i] < tgt:
        i += 1
    seg = (cum[i] - cum[i-1]) or 1.0
    u = (tgt - cum[i-1]) / seg
    x = pts[i-1][0] + (pts[i][0] - pts[i-1][0]) * u
    y = pts[i-1][1] + (pts[i][1] - pts[i-1][1]) * u
    return x, y, math.atan2(pts[i][1] - pts[i-1][1], pts[i][0] - pts[i-1][0])


def positions(t):
    out = []
    for o, ev in ev_by.items():
        ts = [e[0] for e in ev]
        k = bisect.bisect_right(ts, t) - 1
        if k < 0:
            continue
        te, sec = ev[k]
        tn = ev[k + 1][0] if k + 1 < len(ev) else te + 30
        f = min(1.0, (t - te) / max(1.0, tn - te))
        p = sec_pos(sec, f)
        if p:
            out.append((p[0], p[1], p[2], min(1.0, (t - te) / a.stuck)))
    return out


# vehicle prototype meshes
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -100)); body_src = bpy.context.object
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -100)); frame_src = bpy.context.object
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -100)); foup_src = bpy.context.object
frame_src.data.materials.append(M_FRAME); foup_src.data.materials.append(M_FOUP)
tint_mats = [mat(f"tint{i}", (0.24 + 0.76 * s, 0.86 - 0.56 * s, 0.52 - 0.21 * s), 0.35)
             for i, s in enumerate([k / 7 for k in range(8)])]
veh_objs = []


def place_vehicles(t):
    for o in veh_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    veh_objs.clear()
    for i, (x, y, ang, s) in enumerate(positions(t)):
        b = bpy.data.objects.new(f"v{i}", body_src.data.copy()); b.data.materials.clear()
        b.data.materials.append(M_BODY); b.data.materials.append(tint_mats[min(7, int(s * 7.999))])
        # colour the roof polygons with the tint material (index 1)
        for poly in b.data.polygons:
            poly.material_index = 1 if poly.normal.z > 0.5 else 0
        b.location = (x, y, RAIL_H - 0.45); b.scale = (1.6, 0.9, 0.5); b.rotation_euler = (0, 0, ang)
        f = bpy.data.objects.new(f"f{i}", frame_src.data); f.location = (x, y, RAIL_H - 1.15); f.scale = (1.2, 0.08, 0.9); f.rotation_euler = (0, 0, ang)
        p = bpy.data.objects.new(f"p{i}", foup_src.data); p.location = (x, y, RAIL_H - 1.55); p.scale = (0.5, 0.5, 0.45); p.rotation_euler = (0, 0, ang)
        for o in (b, f, p):
            scene.collection.objects.link(o); veh_objs.append(o)


# ── camera + light ────────────────────────────────────────────
cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 35
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam); scene.camera = cam
cam.location = (-W * 0.15, -D * 1.05, 95)
direction = Vector((0, 0, 3)) - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.0; sun.angle = math.radians(3)
so = bpy.data.objects.new("sun", sun); so.location = (50, -80, 120)
so.rotation_euler = (math.radians(50), math.radians(10), math.radians(25)); scene.collection.objects.link(so)

if a.anim:
    t0, t1, fps = a.anim
    n = int((t1 - t0) * fps)
    for i in range(n):
        place_vehicles(t0 + i / fps)
        scene.render.filepath = a.out.replace(".png", f"_{i:04d}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", scene.render.filepath, flush=True)
else:
    place_vehicles(a.t)
    scene.render.filepath = a.out
    bpy.ops.render.render(write_still=True)
    print("rendered", a.out, "vehicles", len(veh_objs) // 3)
