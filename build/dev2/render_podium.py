"""Product shot of the Resondi device on a white podium (recreates the old Ausculta hero image).

Run: blender -b source-material/3d/Resondi_.blend --python build/dev2/render_podium.py
Writes two transparent PNGs to build/dev2/out/: podium_full.png (device + podium) and
podium_mask.png (device only, used for the pink glow). build/dev2/compose_podium.py then
composites figures/Resondi-Device-Podium.png. The .blend file itself is not saved.
"""
import os
import bpy
from mathutils import Vector

HERE = os.path.normpath(os.path.join(os.path.dirname(bpy.data.filepath), "..", "..", "build", "dev2", "out"))
os.makedirs(HERE, exist_ok=True)

s = bpy.context.scene
s.render.resolution_x, s.render.resolution_y = 1620, 1080
s.render.resolution_percentage = 100
s.render.image_settings.file_format = "PNG"
s.render.image_settings.color_mode = "RGBA"
s.render.film_transparent = True
s.render.engine = "CYCLES"  # headless EEVEE returned black frames on this PC
s.cycles.device = "CPU"
s.cycles.samples = 40
if os.environ.get("PREVIEW"):  # quick framing check
    s.render.resolution_percentage, s.cycles.samples = 35, 6
s.cycles.use_denoising = True
s.render.use_compositing = False
s.render.use_sequencer = False
s.view_settings.view_transform = "Standard"
s.view_settings.look = "None"

world = s.world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (1, 1, 1, 1)
bg.inputs[1].default_value = 0.45

for o in s.objects:
    if o.type == "LIGHT":
        o.hide_render = True

from math import radians
from mathutils import Matrix

# Stand the box upright on its front face so the screen faces the camera (like the old
# Ausculta photo). The sensor stays flat on the podium; the ribbon cable is redrawn.
SENSOR = ("Sensor_", "Logo_Cross", "Logo_Leaf")
pivot = Vector((0, -0.05, 0))
R = Matrix.Translation(pivot) @ Matrix.Rotation(radians(90), 4, "X") @ Matrix.Translation(-pivot)
wire_mats = {}
for o in list(s.objects):
    if o.type not in ("MESH", "CURVE", "FONT"):
        continue
    if o.name.startswith("Wire_"):
        wire_mats[o.name] = o.active_material
        o.hide_render = True
    elif o.name.startswith(SENSOR):
        o.matrix_world = Matrix.Translation((-0.045, -0.05, 0)) @ o.matrix_world
    else:
        o.matrix_world = R @ o.matrix_world
bpy.context.view_layer.update()


def bbox(name):
    o = s.objects[name]
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])


cmn, cmx = bbox("Connector_Housing")
smn, smx = bbox("Sensor_Sleeve")
start = Vector((smx.x - 0.002, (smn.y + smx.y) / 2, (smn.z + smx.z) / 2))
end = Vector((cmx.x - 0.002, (cmn.y + cmx.y) / 2, (cmn.z + cmx.z) / 2))
ctrl = [start, start + Vector((0.05, -0.012, -0.002)), Vector((0.10, -0.175, 0.0045)),
        Vector((0.135, -0.13, 0.0045)), Vector((0.125, end.y - 0.004, end.z * 0.45)),
        end + Vector((0.02, 0, 0)), end]


def catmull(p, n=24):
    out = []
    pts = [p[0]] + p + [p[-1]]
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(p[-1])
    return out


path = catmull(ctrl)
for i, name in enumerate(["Wire_Green", "Wire_Blue", "Wire_Yellow", "Wire_Red"]):
    off = (i - 1.5) * 0.0024
    cd = bpy.data.curves.new(name + "_new", "CURVE")
    cd.dimensions = "3D"
    cd.bevel_depth, cd.bevel_resolution = 0.0012, 4
    sp = cd.splines.new("POLY")
    sp.points.add(len(path) - 1)
    for j, p in enumerate(path):
        a, b = path[max(j - 1, 0)], path[min(j + 1, len(path) - 1)]
        t = (b - a).normalized()
        side = Vector((-t.y, t.x, 0)).normalized() if abs(t.z) < 0.9 else Vector((0, 0, 1))
        q = p + side * off
        sp.points[j].co = (q.x, q.y, max(q.z, 0.0012), 1)
    ob = bpy.data.objects.new(name + "_new", cd)
    ob.data.materials.append(wire_mats[name])
    s.collection.objects.link(ob)

device = [o for o in s.objects if o.type in ("MESH", "CURVE", "FONT") and not o.hide_render]

# White podium: a bevelled cylinder whose top sits just under the device
bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=0.17, depth=0.05, location=(0.0, -0.095, -0.0255))
pod = bpy.context.active_object
pod.name = "Podium"
bev = pod.modifiers.new("Bevel", "BEVEL")
bev.width, bev.segments = 0.006, 6
bpy.ops.object.shade_smooth()
pm = bpy.data.materials.new("PodiumWhite")
pm.use_nodes = True
p = pm.node_tree.nodes["Principled BSDF"]
p.inputs["Base Color"].default_value = (0.92, 0.92, 0.93, 1)
p.inputs["Roughness"].default_value = 0.32
pod.data.materials.append(pm)


def aim(ob, target):
    ob.rotation_euler = (Vector(target) - Vector(ob.location)).to_track_quat("-Z", "Y").to_euler()


def area(name, loc, energy, size, target=(0, -0.04, 0.02)):
    light = bpy.data.lights.new(name, "AREA")
    light.energy, light.size = energy, size
    ob = bpy.data.objects.new(name, light)
    s.collection.objects.link(ob)
    ob.location = loc
    aim(ob, target)


area("Key", (-0.35, -0.55, 0.45), 3.0, 0.6, (0, -0.1, 0.05))
area("Fill", (0.5, -0.4, 0.25), 1.0, 0.7, (0, -0.1, 0.05))
area("Rim", (0.0, 0.4, 0.45), 1.5, 0.5, (0, -0.1, 0.05))

cam = bpy.data.objects.new("PodiumCam", bpy.data.cameras.new("PodiumCam"))
s.collection.objects.link(cam)
cam.location = (0.15, -0.84, 0.21)  # a few degrees off-axis: reads flat but shows depth
cam.data.lens = 62
aim(cam, (0.0, -0.09, 0.012))
s.camera = cam


def render(name):
    s.render.filepath = os.path.join(HERE, name)
    bpy.ops.render.render(write_still=True)


render("podium_full.png")

# Device only, flat white, for the glow silhouette
pod.hide_render = True
s.cycles.samples = 1
s.cycles.use_denoising = False
s.cycles.max_bounces = 0
render("podium_mask.png")
print("rendered to", HERE)
