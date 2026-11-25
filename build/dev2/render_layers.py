"""Render the device model as separate layers for the exploded view (user, 25 Nov 2026: break down the parts, like
the phone exploded view they saw).

Run: blender -b source-material/3d/Resondi_.blend --python build/dev2/render_layers.py
Writes build/dev2/out/layers/*.png (transparent, one orthographic camera) and layers.json (the camera scale and the
screen position of each callout). compose_exploded.py stacks them. The .blend file is not saved.

Outer parts are the team's model. The internal parts (board, ESP32, boost converter, microSD module, battery,
microphone, rocker switch) are not in the model: they are simple shapes of the parts in the bill of materials, and
where they sit inside the enclosure is NOT recorded, so every use of this figure says the layout is illustrative.
An orthographic camera without roll moves a lifted part straight up the image, so the stacking is done in 2D.
"""
import json
import math
import os

import bpy
from mathutils import Vector

ROOT = os.path.normpath(os.path.join(os.path.dirname(bpy.data.filepath), "..", ".."))
OUT = os.path.join(ROOT, "build", "dev2", "out", "layers")
os.makedirs(OUT, exist_ok=True)
MM = 0.001
s = bpy.context.scene


def mat(name, rgb, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


GREEN = mat("x_pcb", (0.015, 0.16, 0.07), 0.45)
BLUE = mat("x_pcb_blue", (0.02, 0.09, 0.32), 0.45)
BLACK = mat("x_black", (0.02, 0.02, 0.022), 0.5)
STEEL = mat("x_steel", (0.62, 0.63, 0.65), 0.28, 1.0)
GOLD = mat("x_gold", (0.75, 0.52, 0.16), 0.35, 1.0)
COPPER = mat("x_copper", (0.62, 0.26, 0.10), 0.4, 0.8)
BATT = mat("x_batt", (0.055, 0.06, 0.07), 0.45)
BATTL = mat("x_battl", (0.80, 0.16, 0.36), 0.5)
WHITE = mat("x_white", (0.82, 0.82, 0.82), 0.5)
TEXT = mat("x_text", (0.95, 0.95, 0.95), 0.6)


def box(name, x0, x1, y0, y1, z0, z1, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.name = name
    o.location = ((x0 + x1) / 2 * MM, (y0 + y1) / 2 * MM, (z0 + z1) / 2 * MM)
    o.scale = ((x1 - x0) * MM, (y1 - y0) * MM, (z1 - z0) * MM)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if m:
        o.data.materials.append(m)
    if bevel:
        b = o.modifiers.new("b", "BEVEL")
        b.width, b.segments = bevel * MM, 4
    return o


def cyl(name, x, y, z0, z1, r, m):
    bpy.ops.mesh.primitive_cylinder_add(radius=r * MM, depth=(z1 - z0) * MM, vertices=64,
                                        location=(x * MM, y * MM, (z0 + z1) / 2 * MM))
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(m)
    return o


def label(name, txt, x, y, z, size, m):
    c = bpy.data.curves.new(name, "FONT")
    c.body, c.size, c.align_x, c.align_y, c.extrude = txt, size * MM, "CENTER", "CENTER", 0.0001
    c.materials.append(m)
    o = bpy.data.objects.new(name, c)
    o.location = (x * MM, y * MM, z * MM)
    s.collection.objects.link(o)
    return o


def cut(target, cutter):
    b = target.modifiers.new("cut", "BOOLEAN")
    b.operation, b.object, b.solver = "DIFFERENCE", cutter, "EXACT"
    cutter.hide_render = True


obj = bpy.data.objects
# open the body and cut the openings in the cover, so the opened parts look like what they are
cavity = box("cut_cavity", -74, 74, -44, 44, 4, 70, None)
for n in ("Band_Coral", "Base_White"):
    cut(obj[n], cavity)
cut(obj["Top_Plate"], box("cut_lcd", -70, 14, -4, 32, 30, 70, None))
for k, (cx, cy) in enumerate(((52, 20), (52, -23))):
    c = cyl("cut_btn%d" % k, cx, cy, 30, 70, 14, BLACK)
    cut(obj["Top_Plate"], c)

# parts that are in the bill of materials but not in the model
box("x_lcd_board", -76, 20, -11, 39, 46.5, 48.3, GREEN, 0.4)
for k, (cx, cy) in enumerate(((52, 20), (52, -23))):
    cyl("x_btn_body%d" % k, cx, cy, 30, 50, 12, WHITE)
box("x_batt", -62, 48, -32, 32, 6, 18, BATT, 4)
box("x_batt_band", -62.2, -46, -32.2, 32.2, 5.9, 18.1, BATTL, 4)
label("x_batt_t", "10,000 mAh", 2, 4, 18.3, 13, TEXT)
label("x_batt_t2", "Li-ion", 2, -11, 18.3, 8, TEXT)
PZ = 25.0
box("x_pcb", -62, 28, -26, 44, PZ, PZ + 1.6, GREEN, 0.5)
for i in range(12):
    for j, yy in ((0, -23), (1, 41)):
        cyl("x_hole%d_%d" % (i, j), -58 + i * 7.3, yy, PZ + 1.5, PZ + 1.75, 1.1, GOLD)
# ESP32 30-pin development board
box("x_esp_hdrA", -54, -2, 10.5, 13, PZ + 1.6, PZ + 8, BLACK)
box("x_esp_hdrB", -54, -2, 33.5, 36, PZ + 1.6, PZ + 8, BLACK)
box("x_esp", -55, -1, 9.5, 37, PZ + 8, PZ + 9.6, BLACK, 0.6)
box("x_esp_can", -52, -34, 14.5, 32, PZ + 9.6, PZ + 12.6, STEEL, 0.5)
box("x_esp_usb", -5, 1, 19, 27.5, PZ + 9.6, PZ + 12.4, STEEL, 0.5)
box("x_esp_ic", -24, -18, 20, 26, PZ + 9.6, PZ + 10.6, BLACK)
label("x_esp_t", "ESP32", -43, 23, PZ + 12.75, 5.5, BLACK)
for i in range(15):
    for yy in (11.7, 34.8):
        cyl("x_pin%d_%d" % (i, int(yy)), -52 + i * 3.5, yy, PZ + 9.5, PZ + 10.4, 0.8, GOLD)
# LM2577 boost converter
box("x_boost", -52, -8, -20, 2, PZ + 3, PZ + 4.6, BLUE, 0.4)
cyl("x_boost_coil", -22, -9, PZ + 4.6, PZ + 11, 7, BLACK)
cyl("x_boost_coil2", -22, -9, PZ + 11, PZ + 11.6, 5, COPPER)
for x in (-47, -12):
    cyl("x_boost_cap%d" % x, x, -9, PZ + 4.6, PZ + 14, 4, STEEL)
box("x_boost_ic", -40, -31, -15, -4, PZ + 4.6, PZ + 8, BLACK)
box("x_boost_pot", -33, -28, -2.5, 1.5, PZ + 4.6, PZ + 12, BLUE)
# resistors
for k, x in enumerate((8, 14)):
    o = cyl("x_res%d" % k, x, 30, PZ + 2, PZ + 10, 1.5, COPPER)
    o.rotation_euler = (math.radians(90), 0, 0)
    o.location.z = (PZ + 3.4) * MM
# microSD module and card, at the model's card slot on the front wall
box("x_sd", -14, 24, -47, -29, PZ, PZ + 1.6, BLUE, 0.4)
box("x_sd_cage", -3, 13, -46, -32, PZ + 1.6, PZ + 4, STEEL, 0.4)
label("x_sd_t", "microSD", 5, -39, PZ + 4.1, 3.6, BLACK)
box("x_sd_card", -0.5, 10.5, -56, -44, PZ + 1.9, PZ + 2.9, BLACK, 0.4)
# INMP441 microphone, drawn above the sensor head
cyl("x_mic", -74, -114, 16, 17.6, 8, BLUE)
box("x_mic_can", -77.5, -70.5, -117, -111, 17.6, 19.2, STEEL, 0.4)
cyl("x_mic_hole", -74, -114, 19.15, 19.3, 0.9, BLACK)
for i in range(6):
    a = math.radians(60 * i + 30)
    cyl("x_mic_pad%d" % i, -74 + 6.3 * math.cos(a), -114 + 6.3 * math.sin(a), 17.5, 17.8, 0.8, GOLD)
# liner strips close the slits the two cut boxes leave between base and band
CORAL = obj["Band_Coral"].data.materials[0]
for k, b4 in enumerate(((-74, 74, 43, 44.6), (-74, 74, -44.6, -43), (-74.6, -73, -44, 44), (73, 74.6, -44, 44))):
    box("x_liner%d" % k, b4[0], b4[1], b4[2], b4[3], 4.2, 43.4, CORAL)
# power rocker switch on the right-hand side wall, next to the cable connector
box("x_rocker", 78.5, 81, 17, 33, 23, 36, BLACK, 0.8)
box("x_rocker_key", 80.5, 82.6, 19, 31, 25, 34, WHITE, 0.8)

GROUPS = {
    "screws": lambda n: n.startswith("Screw"),
    "buttons": lambda n: n.startswith("Button") or n.startswith("x_btn"),
    "leds": lambda n: n.startswith("LED_"),
    "lcd": lambda n: n.startswith("LCD_") or n.startswith("x_lcd"),
    "cover": lambda n: n in ("Top_Plate", "Logo_Text", "Logo_Heartbeat"),
    "board": lambda n: n.startswith(("x_pcb", "x_hole", "x_esp", "x_pin", "x_boost", "x_res", "x_sd")),
    "battery": lambda n: n.startswith("x_batt"),
    "body": lambda n: n in ("Band_Coral", "Base_White", "SD_Slot") or n.startswith(("Connector", "x_rocker", "x_liner")),
    "mic": lambda n: n.startswith("x_mic"),
    "sensor": lambda n: n.startswith(("Sensor", "Wire", "Logo_Cross", "Logo_Leaf")),
}
drawable = [o for o in obj if o.type in ("MESH", "CURVE", "FONT") and not o.name.startswith("cut_")]
owner = {}
for o in drawable:
    hit = [g for g, f in GROUPS.items() if f(o.name)]
    assert len(hit) <= 1, (o.name, hit)
    owner[o.name] = hit[0] if hit else None

for o in obj:
    if o.type == "LIGHT":
        o.hide_render = True
s.render.engine = "CYCLES"
s.cycles.device = "CPU"
s.cycles.samples = 64
s.cycles.use_denoising = True
s.render.film_transparent = True
s.render.image_settings.file_format = "PNG"
s.render.image_settings.color_mode = "RGBA"
s.render.use_compositing = s.render.use_sequencer = False
s.view_settings.view_transform, s.view_settings.look, s.view_settings.exposure = "Standard", "None", 0
world = s.world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (1, 0.97, 0.98, 1)
bg.inputs[1].default_value = 0.42

EL, AZ = math.radians(32), math.radians(38)      # camera height above the horizon, turned to the right of the front
W, H, PX = 1300, 1150, 4.6                       # pixels, and pixels per millimetre
target = Vector((0, -0.035, 0.028))
view = Vector((math.sin(AZ) * math.cos(EL), -math.cos(AZ) * math.cos(EL), math.sin(EL)))
cam = bpy.data.objects.new("XCam", bpy.data.cameras.new("XCam"))
s.collection.objects.link(cam)
cam.data.type = "ORTHO"
cam.data.ortho_scale = max(W, H) / PX * MM
cam.location = target + view * 2.0
cam.rotation_euler = (-view).to_track_quat("-Z", "Y").to_euler()
cam.data.clip_end = 10
s.camera = cam
s.render.resolution_x, s.render.resolution_y, s.render.resolution_percentage = W, H, 100


def area(loc, energy, size):
    light = bpy.data.lights.new("xl", "AREA")
    light.energy, light.size = energy, size
    o = bpy.data.objects.new("xl", light)
    s.collection.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector((0, -0.03, 0.03)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


area((-0.35, -0.45, 0.7), 4.2, 0.6)
area((0.6, -0.25, 0.35), 1.3, 0.7)

right = Vector((math.cos(AZ), math.sin(AZ), 0))
up = Vector((-math.sin(AZ) * math.sin(EL), math.cos(AZ) * math.sin(EL), math.cos(EL)))


def px(x, y, z):
    d = Vector((x * MM, y * MM, z * MM)) - target
    return [W / 2 + d.dot(right) / MM * PX, H / 2 - d.dot(up) / MM * PX]


POINTS = {
    "screws": px(74, 44, 51), "buttons": px(58, 22, 61), "lcd": px(6, 18, 54), "leds": px(23, 18, 55),
    "cover": px(60, -44, 50), "esp": px(-30, 30, PZ + 10), "sd": px(18, -38, PZ + 1.6), "boost": px(-12, -9, PZ + 14),
    "pcb": px(24, 20, PZ + 1.6), "battery": px(40, -20, 18), "body": px(79, -30, 30), "rocker": px(82, 25, 30),
    "mic": px(-70, -116, 19), "sensor": px(-62, -118, 11),
}
RIM = [px(-74, -44, 44), px(74, -44, 44), px(74, 44, 44)]   # front edges of the opening, left to right on screen
json.dump({"px_per_mm": PX, "el": EL, "az": AZ, "target": [v / MM for v in target], "W": W, "H": H, "px_per_mm_up": PX * math.cos(EL), "points": POINTS, "rim": RIM},
          open(os.path.join(OUT, "layers.json"), "w"), indent=1)

# the same parts without what sits below the cover, for the closed device in the animation
TOPS = {"lcd_top": lambda n: n.startswith("LCD_"), "buttons_top": lambda n: n.startswith("Button")}
only = os.environ.get("LAYERS", "").split(",") if os.environ.get("LAYERS") else list(GROUPS) + list(TOPS)   # e.g. LAYERS=body
for g in only:
    for o in drawable:
        o.hide_render = not TOPS[g](o.name) if g in TOPS else owner[o.name] != g
    s.render.filepath = os.path.join(OUT, g + ".png")
    bpy.ops.render.render(write_still=True)
print("layers done:", [n for n, g in owner.items() if g is None])
