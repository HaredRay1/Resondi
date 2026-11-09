"""Render the team's Blender device model (source-material/3d/Resondi_.blend).

Run: blender -b source-material/3d/Resondi_.blend --python build/dev2/render_blend.py
Writes figures/Resondi-Device-3D.png (three-quarter view). The camera and
lighting are set here, in memory only: the scene's own camera misses the device and its
light overexposes the white plastic. The .blend file itself is not saved.
"""
import os
import bpy
from mathutils import Vector

OUT = os.path.normpath(os.path.join(os.path.dirname(bpy.data.filepath), "..", "..", "figures"))
ROSE_BG = (1.0, 0.913, 0.947, 1)  # #FFF5F9 in linear light

s = bpy.context.scene
s.render.resolution_x, s.render.resolution_y = 1500, 940
s.render.resolution_percentage = 100
s.render.image_settings.file_format = "PNG"
s.render.film_transparent = False
s.render.engine = "CYCLES"  # headless EEVEE returned black frames on this PC
s.cycles.device = "CPU"
s.cycles.samples = 48
s.cycles.use_denoising = True
s.render.use_compositing = False
s.render.use_sequencer = False
s.view_settings.view_transform = "Standard"
s.view_settings.look = "None"
s.view_settings.exposure = 0

world = s.world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = ROSE_BG
bg.inputs[1].default_value = 0.30

for o in s.objects:
    if o.type == "LIGHT":
        o.hide_render = True

# Floor in the background colour, so the device has a contact shadow
bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, -0.0005))
floor = bpy.context.active_object
fm = bpy.data.materials.new("Floor")
fm.use_nodes = True
fm.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = ROSE_BG
fm.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
floor.data.materials.append(fm)


def area(name, loc, energy, size):
    light = bpy.data.lights.new(name, "AREA")
    light.energy, light.size = energy, size
    ob = bpy.data.objects.new(name, light)
    s.collection.objects.link(ob)
    ob.location = loc
    aim(ob, Vector((0, -0.03, 0.03)))


def aim(ob, target):
    ob.rotation_euler = (target - Vector(ob.location)).to_track_quat("-Z", "Y").to_euler()


area("Key", (-0.25, -0.35, 0.55), 2.0, 0.5)
area("Fill", (0.45, -0.1, 0.3), 0.5, 0.6)


def shot(name, loc, target, lens):
    cam = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    s.collection.objects.link(cam)
    cam.location = loc
    cam.data.lens = lens
    aim(cam, Vector(target))
    s.camera = cam
    s.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


shot("Resondi-Device-3D", (0.2, -0.5, 0.42), (-0.008, -0.05, 0.015), 60)
print("rendered to", OUT)
