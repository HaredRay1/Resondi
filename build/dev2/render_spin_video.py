"""Product video of the Resondi device: four camera moves on a dark studio floor, no text.

Recreates the camera work of the team's earlier clip (6.7 s, 1920x1080, 30 fps) with the new
device model. Run:
  blender -b source-material/3d/Resondi_.blend --python build/dev2/render_spin_video.py
Env: ENGINE=EEVEE|CYCLES (default EEVEE), FRAMES=a-b to render part, PCT=resolution %.
Writes PNG frames to build/dev2/out/video/; build/dev2/encode_video.py makes the MP4.
The .blend file itself is not saved.
"""
import os
import bpy
from mathutils import Vector

OUT = os.path.normpath(os.path.join(os.path.dirname(bpy.data.filepath), "..", "..", "build", "dev2", "out", "video"))
os.makedirs(OUT, exist_ok=True)

s = bpy.context.scene
s.render.resolution_x, s.render.resolution_y = 1920, 1080
s.render.resolution_percentage = int(os.environ.get("PCT", "100"))
s.render.fps = 30
s.frame_start, s.frame_end = 1, 200
if os.environ.get("FRAMES"):
    a, b = os.environ["FRAMES"].split("-")
    s.frame_start, s.frame_end = int(a), int(b)
s.frame_step = int(os.environ.get("STEP", "1"))
s.render.image_settings.file_format = "PNG"
s.render.film_transparent = False
s.render.use_compositing = False
s.render.use_sequencer = False
s.view_settings.view_transform = "Standard"
s.view_settings.look = "None"

engine = os.environ.get("ENGINE", "EEVEE")
if engine == "CYCLES":
    s.render.engine = "CYCLES"
    s.cycles.device = "CPU"
    s.cycles.samples = int(os.environ.get("SAMPLES", "24"))
    s.cycles.use_denoising = True
    s.cycles.max_bounces = 4
else:
    s.render.engine = "BLENDER_EEVEE"
    s.eevee.taa_render_samples = 24
    try:
        s.eevee.use_raytracing = True
        s.eevee.use_shadows = True
    except AttributeError:
        pass

DARK = (0.052, 0.042, 0.046, 1)  # warm charcoal, like the original clip
world = s.world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = DARK
bg.inputs[1].default_value = 1.0

for o in s.objects:
    if o.type == "LIGHT" or o.type == "CAMERA":
        o.hide_render = True

# Large floor that fades into the background
bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -0.0005))
floor = bpy.context.active_object
fm = bpy.data.materials.new("StudioFloor")
fm.use_nodes = True
fp = fm.node_tree.nodes["Principled BSDF"]
fp.inputs["Base Color"].default_value = (0.075, 0.058, 0.064, 1)
fp.inputs["Roughness"].default_value = 0.55
floor.data.materials.append(fm)


def aim(ob, target):
    ob.rotation_euler = (Vector(target) - Vector(ob.location)).to_track_quat("-Z", "Y").to_euler()


def area(name, loc, energy, size, target=(0, -0.03, 0.02)):
    light = bpy.data.lights.new(name, "AREA")
    light.energy, light.size = energy, size
    ob = bpy.data.objects.new(name, light)
    s.collection.objects.link(ob)
    ob.location = loc
    aim(ob, target)


area("Top", (0.0, -0.05, 0.75), 4.5, 0.6)       # pool of light on the floor
area("Key", (-0.45, -0.5, 0.45), 1.8, 0.5)
area("Rim", (0.4, 0.45, 0.35), 2.0, 0.4)


def keyed_camera(name, lens, keys, dist=1.0):
    """keys: list of (frame, location, target); dist pushes the camera back along its view line."""
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    s.collection.objects.link(cam)
    cam.data.lens = lens
    cam.data.dof.use_dof = True
    cam.data.dof.aperture_fstop = 5.6
    for f, loc, tgt in keys:
        loc = Vector(tgt) + (Vector(loc) - Vector(tgt)) * dist
        cam.location = loc
        aim(cam, tgt)
        cam.data.dof.focus_distance = (Vector(loc) - Vector(tgt)).length
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
        cam.data.dof.keyframe_insert("focus_distance", frame=f)
    return cam


DEV = (0.0, 0.0, 0.03)
SENS = (-0.074, -0.114, 0.006)
shots = [
    # A: close three-quarter on the box, trucking right
    (1, keyed_camera("A", 40, [(1, (-0.22, -0.20, 0.17), (0.0, 0.0, 0.03)),
                               (45, (-0.08, -0.29, 0.17), (0.02, 0.0, 0.03))], 1.25)),
    # B: low close-up on the chest piece, sliding along the cable
    (46, keyed_camera("B", 45, [(46, (0.06, -0.27, 0.07), (-0.06, -0.115, 0.006)),
                                (90, (-0.05, -0.30, 0.07), (-0.08, -0.11, 0.006))], 1.35)),
    # C: top-down, drifting from the chest piece to the box
    (91, keyed_camera("C", 38, [(91, (-0.06, -0.10, 0.42), (-0.06, -0.08, 0.0)),
                                (130, (0.02, -0.04, 0.42), (0.02, -0.02, 0.0))])),
    # D: starts close, pulls back to a wide three-quarter
    (131, keyed_camera("D", 40, [(131, (-0.20, -0.22, 0.13), (0.0, -0.02, 0.03)),
                                 (200, (-0.36, -0.52, 0.36), (0.0, -0.05, 0.02))], 1.3)),
]
for frame, cam in shots:
    m = s.timeline_markers.new(cam.name, frame=frame)
    m.camera = cam
s.camera = shots[0][1]

# Even camera speed within each shot, with a gentle ease at its ends
for _, cam in shots:
    ad = cam.animation_data
    if ad and ad.action:
        try:
            curves = ad.action.fcurves
        except AttributeError:  # layered actions (Blender 4.4+)
            curves = [fc for layer in ad.action.layers for strip in layer.strips
                      for bag in strip.channelbags for fc in bag.fcurves]
        for fc in curves:
            for kp in fc.keyframe_points:
                kp.interpolation = "SINE"
                kp.easing = "EASE_IN_OUT"

s.render.filepath = os.path.join(OUT, "f_")
bpy.ops.render.render(animation=True)
print("rendered frames", s.frame_start, "-", s.frame_end, "to", OUT)
