"""Blender (headless) close-up render of an OHT bay from viewer3d/scene-closeup.json.

Usage:
  blender -b -P blender_closeup.py -- --scene scene-closeup.json --run 1 --t 930 --out /out/frame.png \
          [--view rail|oblique|follow] [--samples 128] [--res 1920 1080] [--anim T0 T1 FPS]

Scene: raised floor, ceiling with light panels, C-channel rails with hangers, tool cabinets with load
ports along the bays, and OHT vehicles (bogie, rounded body, blue belt line, status lamp, retracted
hoist belts, gripper, FOUP with lid and handle) placed from the occupancy log at time t.
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
ap.add_argument("--run", type=int, default=1)
ap.add_argument("--t", type=float, default=930.0)
ap.add_argument("--out", default="/out/frame.png")
ap.add_argument("--view", default="rail", choices=["rail", "oblique", "follow"])
ap.add_argument("--samples", type=int, default=128)
ap.add_argument("--res", type=int, nargs=2, default=[1920, 1080])
ap.add_argument("--anim", type=float, nargs=3, default=None)
ap.add_argument("--stuck", type=float, default=30.0)
a = ap.parse_args(argv)

S = 0.001
RAIL_H = 4.2
data = json.load(open(a.scene, encoding="utf-8"))
minx, miny, maxx, maxy = data["bbox"]
cx, cy = (minx + maxx) / 2 * S, (miny + maxy) / 2 * S
W, D = (maxx - minx) * S, (maxy - miny) * S
xy = lambda x, y: (x * S - cx, -(y * S - cy))

# ── scene / render settings ────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.render.resolution_x, scene.render.resolution_y = a.res
scene.render.image_settings.file_format = "PNG"
scene.cycles.samples = a.samples
scene.cycles.use_denoising = True
scene.view_settings.view_transform = "Filmic" if "Filmic" in [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items] else "AgX"
scene.view_settings.look = "None"
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
world = bpy.data.worlds.new("W"); scene.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.85, 0.88, 0.92, 1); bg.inputs[1].default_value = 0.5


def mat(name, rgb, rough=0.5, metal=0.0, emit=0.0, alpha=1.0, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if coat and "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = coat
    if emit:
        if "Emission Color" in b.inputs:
            b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    if alpha < 1:
        b.inputs["Alpha"].default_value = alpha; m.blend_method = "BLEND"
    return m


M = {
    "floor": mat("floor", (0.80, 0.82, 0.85), 0.9),
    "ceil": mat("ceil", (0.93, 0.94, 0.96), 1.0),
    "lamp": mat("lamp", (1, 1, 1), 1.0, emit=2.5),
    "rail": mat("rail", (0.76, 0.78, 0.81), 0.3, 0.85),
    "hang": mat("hang", (0.62, 0.65, 0.69), 0.4, 0.7),
    "cab": mat("cab", (0.91, 0.92, 0.94), 0.55, 0.05),
    "trim": mat("trim", (0.32, 0.38, 0.46), 0.5, 0.4),
    "port": mat("port", (0.68, 0.72, 0.77), 0.35, 0.7),
    "bogie": mat("bogie", (0.16, 0.18, 0.21), 0.6, 0.3),
    "body": mat("body", (0.96, 0.96, 0.97), 0.25, 0.05, coat=0.8),
    "blue": mat("blue", (0.16, 0.33, 0.66), 0.45, 0.2),
    "belt": mat("belt", (0.1, 0.11, 0.13), 0.9),
    "foup": mat("foup", (0.55, 0.64, 0.76), 0.25, 0.0, alpha=0.9, coat=0.6),
    "lid": mat("lid", (0.22, 0.28, 0.36), 0.5),
}
lamp_mats = [mat(f"st{i}", (0.2 + 0.7 * s, 0.77 - 0.5 * s, 0.42 - 0.12 * s), 0.4, emit=4.0) for i, s in enumerate([k / 7 for k in range(8)])]


def box(name, size, loc, m, rot=0.0, bevel=0.0):
    """Unit cube scaled to `size`, with the scale baked into the mesh so instances share the dimensions."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = name; o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.rotation_euler = (0, 0, rot)
    o.data.materials.append(m)
    if bevel:
        mod = o.modifiers.new("bevel", "BEVEL"); mod.width = bevel; mod.segments = 3
        bpy.ops.object.modifier_apply(modifier="bevel")
    return o


# ── floor, ceiling, lamps ───────────────────────────────────────
box("floor", (W + 40, D + 40, 0.02), (0, 0, -0.01), M["floor"])
box("ceil", (W + 40, D + 40, 0.02), (0, 0, RAIL_H + 1.7), M["ceil"])
lamp_src = box("lamp", (1.2, 0.6, 0.04), (0, 0, -50), M["lamp"])
for i, x in enumerate(range(int(-W / 2 - 15), int(W / 2 + 15), 3)):
    for j, y in enumerate(range(int(-D / 2 - 15), int(D / 2 + 15), 3)):
        o = bpy.data.objects.new(f"lamp{i}_{j}", lamp_src.data); o.location = (x, y, RAIL_H + 1.66); scene.collection.objects.link(o)

# ── rails: per-link C-channel from three boxes (top flange, bottom flange, web), unit length along x ──
fl_src = box("flange", (1.0, 0.34, 0.05), (0, 0, -50), M["rail"])
web_src = box("web", (1.0, 0.05, 0.22), (0, 0, -50), M["rail"])
k = 0
for l in data["links"]:
    x1, y1 = xy(l[0], l[1]); x2, y2 = xy(l[2], l[3])
    ln = math.hypot(x2 - x1, y2 - y1) or 0.01
    ang = math.atan2(y2 - y1, x2 - x1)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    sx, sy = -math.sin(ang) * 0.145, math.cos(ang) * 0.145
    for src, dx, dy, z in ((fl_src, 0, 0, RAIL_H + 0.135), (fl_src, 0, 0, RAIL_H - 0.135),
                           (web_src, sx, sy, RAIL_H), (web_src, -sx, -sy, RAIL_H)):
        o = bpy.data.objects.new(f"r{k}", src.data); k += 1
        o.location = (mx + dx, my + dy, z); o.rotation_euler = (0, 0, ang); o.scale = (ln, 1, 1)
        scene.collection.objects.link(o)
hang_src = box("hang", (0.035, 0.035, 1.45), (0, 0, -50), M["hang"])
k = 0
for l in data["links"]:
    x1, y1 = xy(l[0], l[1]); x2, y2 = xy(l[2], l[3])
    n = max(1, round(math.hypot(x2 - x1, y2 - y1) / 4))
    for i in range(n):
        o = bpy.data.objects.new(f"h{k}", hang_src.data); k += 1
        o.location = (x1 + (x2 - x1) * (i + 0.5) / n, y1 + (y2 - y1) * (i + 0.5) / n, RAIL_H + 0.87); scene.collection.objects.link(o)

# ── tool cabinets along the bays ────────────────────────────────
cab_src = box("cab", (2.2, 2.6, 2.3), (0, 0, -50), M["cab"], bevel=0.04)
trim_src = box("trim", (2.24, 2.64, 0.12), (0, 0, -50), M["trim"])
port_src = box("port", (0.55, 0.55, 0.12), (0, 0, -50), M["port"])
k = 0
for l in data["links"]:
    x1, y1 = xy(l[0], l[1]); x2, y2 = xy(l[2], l[3])
    if abs(y2 - y1) < abs(x2 - x1):
        continue
    n = max(1, round(abs(y2 - y1) / 3.2))
    for i in range(n):
        px, py = x1 + (x2 - x1) * (i + 0.5) / n + 2.1, y1 + (y2 - y1) * (i + 0.5) / n
        for src, z, dx in ((cab_src, 1.15, 0), (trim_src, 2.36, 0), (port_src, 0.95, -1.5)):
            o = bpy.data.objects.new(f"t{k}", src.data); k += 1; o.location = (px + dx, py, z); scene.collection.objects.link(o)

# ── vehicles from the occupancy log ─────────────────────────────
run = data["runs"][a.run]
sec_pts = {kk: [xy(p[0], p[1]) for p in v] for kk, v in data["sections"].items()}
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
    seg = (cum[i] - cum[i-1]) or 1.0; u = (tgt - cum[i-1]) / seg
    return (pts[i-1][0] + (pts[i][0] - pts[i-1][0]) * u, pts[i-1][1] + (pts[i][1] - pts[i-1][1]) * u,
            math.atan2(pts[i][1] - pts[i-1][1], pts[i][0] - pts[i-1][0]))


def positions(t):
    out = []
    for o, ev in ev_by.items():
        ts = [e[0] for e in ev]
        k2 = bisect.bisect_right(ts, t) - 1
        if k2 < 0:
            continue
        te, sec = ev[k2]
        if sec < 0:
            continue
        tn = ev[k2 + 1][0] if k2 + 1 < len(ev) else te + 30
        p = sec_pos(sec, min(1.0, (t - te) / max(1.0, tn - te)))
        if p:
            out.append((o, p[0], p[1], p[2], min(1.0, (t - te) / a.stuck)))
    return out


bogie_src = box("bogie", (1.1, 0.26, 0.22), (0, 0, -50), M["bogie"])
body_src = box("body", (1.75, 0.95, 0.62), (0, 0, -50), M["body"], bevel=0.08)
band_src = box("band", (1.78, 0.98, 0.08), (0, 0, -50), M["blue"])
belt_src = box("belt", (0.024, 0.024, 0.3), (0, 0, -50), M["belt"])
grip_src = box("grip", (0.62, 0.4, 0.08), (0, 0, -50), M["bogie"])
foup_src = box("foup", (0.44, 0.44, 0.42), (0, 0, -50), M["foup"], bevel=0.04)
lid_src = box("lid", (0.46, 0.46, 0.05), (0, 0, -50), M["lid"])
handle_src = box("handle", (0.3, 0.05, 0.04), (0, 0, -50), M["bogie"])
lamp_srcs = [box(f"lampsrc{i}", (0.28, 0.12, 0.05), (0, 0, -50), lm) for i, lm in enumerate(lamp_mats)]
veh_objs = []


def place(t):
    for o in veh_objs:
        bpy.data.objects.remove(o, do_unlink=True)
    veh_objs.clear()
    for i, (oid, x, y, ang, s) in enumerate(positions(t)):
        c, sn = math.cos(ang), math.sin(ang)
        def put(src, dx, dy, z):
            o = bpy.data.objects.new(f"v{i}_{src.name}", src.data)
            o.location = (x + dx * c - dy * sn, y + dx * sn + dy * c, z); o.rotation_euler = (0, 0, ang)
            scene.collection.objects.link(o); veh_objs.append(o)
        put(bogie_src, 0, 0, RAIL_H)
        put(body_src, 0, 0, RAIL_H - 0.55)
        put(band_src, 0, 0, RAIL_H - 0.72)
        put(lamp_srcs[min(7, int(s * 7.999))], 0, 0.49, RAIL_H - 0.45)
        put(belt_src, 0.22, 0, RAIL_H - 0.98); put(belt_src, -0.22, 0, RAIL_H - 0.98)
        put(grip_src, 0, 0, RAIL_H - 1.14)
        put(foup_src, 0, 0, RAIL_H - 1.42)
        put(lid_src, 0, 0, RAIL_H - 1.19)
        put(handle_src, 0, 0, RAIL_H - 1.15)


# ── camera anchored on the busiest section ──────────────────────
cnt = {}
for t, o, s in run["events"]:
    if s >= 0:
        cnt[s] = cnt.get(s, 0) + 1
best = max(cnt, key=cnt.get)
pts = sec_pts[str(best)]
p0, p1 = pts[0], pts[-1]
ba = math.atan2(p1[1] - p0[1], p1[0] - p0[0]); bx, by = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
dx, dy = math.cos(ba), math.sin(ba)
cam_data = bpy.data.cameras.new("cam"); cam_data.lens = 32
cam = bpy.data.objects.new("cam", cam_data); scene.collection.objects.link(cam); scene.camera = cam


def aim(pos, tgt):
    cam.location = pos
    cam.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()


def set_view(t):
    if a.view == "rail":
        aim((bx - dx * 9 - dy * 1.6, by - dy * 9 + dx * 1.6, RAIL_H + 0.5), (bx + dx * 10, by + dy * 10, RAIL_H - 1.2))
    elif a.view == "oblique":
        aim((bx - dx * 8 - dy * 7, by - dy * 8 + dx * 7, RAIL_H + 5.0), (bx + dx * 3, by + dy * 3, RAIL_H - 1.2))
    else:  # follow the vehicle nearest the busiest section
        ps = positions(t)
        if ps:
            oid, x, y, ang, _ = min(ps, key=lambda p: math.hypot(p[1] - bx, p[2] - by))
            c, sn = math.cos(ang), math.sin(ang)
            aim((x - c * 4.4 + sn * 2.2, y - sn * 4.4 - c * 2.2, RAIL_H - 0.75), (x + c * 0.3, y + sn * 0.3, RAIL_H - 0.85))


sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 1.0; sun.angle = math.radians(9)
so = bpy.data.objects.new("sun", sun); so.rotation_euler = (math.radians(48), math.radians(12), math.radians(-35)); scene.collection.objects.link(so)
area = bpy.data.lights.new("fill", "AREA"); area.energy = 400; area.size = 12
ao = bpy.data.objects.new("fill", area); ao.location = (bx - dx * 4, by - dy * 4, RAIL_H + 1.5); ao.rotation_euler = (0, 0, 0); scene.collection.objects.link(ao)

if a.anim:
    t0, t1, fps = a.anim
    n = int((t1 - t0) * fps)
    for i in range(n):
        t = t0 + i / fps
        place(t); set_view(t)
        scene.render.filepath = a.out.replace(".png", f"_{i:04d}.png")
        bpy.ops.render.render(write_still=True)
        print("rendered", scene.render.filepath, flush=True)
else:
    place(a.t); set_view(a.t)
    scene.render.filepath = a.out
    bpy.ops.render.render(write_still=True)
    print("rendered", a.out, "vehicles", len(veh_objs) // 10)
