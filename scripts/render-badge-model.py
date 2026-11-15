"""Render exported badge GLBs with Blender for an independent geometry review.

blender --background --factory-startup --python scripts/render-badge-model.py -- \
  --input /absolute/S01-O01-cylinder.glb --output /absolute/render-directory \
  --views front oblique side

These are offline renders of the exact GLB, not screenshots of the web viewer.
"""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

parser = argparse.ArgumentParser()
parser.add_argument("--input", required=True)
parser.add_argument("--output", required=True)
parser.add_argument("--views", nargs="+", default=["front", "oblique", "side"])
parser.add_argument("--size", type=int, default=1000)
parser.add_argument("--samples", type=int, default=48)
parser.add_argument("--reference-size-mm", type=float, default=65)
args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
source = Path(args.input).resolve()
output = Path(args.output).resolve()
output.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source))
badge_meshes = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
if not badge_meshes:
    raise RuntimeError("The GLB contains no meshes")
corners = [obj.matrix_world @ Vector(corner) for obj in badge_meshes for corner in obj.bound_box]
minimum = Vector(tuple(min(c[i] for c in corners) for i in range(3)))
maximum = Vector(tuple(max(c[i] for c in corners) for i in range(3)))
# A fixed nominal reference frame makes before/after cameras and lights exactly identical even
# when the old drawing's bevels enlarged its bounds. The builder's neutral face is centred at zero.
center = Vector((0, 0, 0))
reach = args.reference_size_mm / 1000
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = args.samples
scene.cycles.use_denoising = bool(getattr(bpy.app.build_options, "openimagedenoise", False))
scene.cycles.max_bounces = 5
scene.render.resolution_x = args.size
scene.render.resolution_y = args.size
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGBA"
scene.render.film_transparent = False
scene.render.threads_mode = "FIXED"
scene.render.threads = 4
scene.world = bpy.data.worlds.new("Badge review studio")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.055, 0.07, 0.085, 1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4
scene.view_settings.view_transform = "AgX"
scene.view_settings.look = "AgX - Medium High Contrast"

def point_at(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()

# glTF's Y-up (x,y,z) becomes Blender's Z-up (x,-z,y). The badge face points toward -Y.
def studio_vector(v):
    return Vector((v[0], -v[2], v[1]))

for name, position, watts, size, color in [
    ("Warm key", (-0.8, 0.95, 1.1), 0.035, 0.7, (1.0, 0.86, 0.69)),
    ("Cool fill", (0.9, 0.25, 0.8), 0.014, 0.9, (0.74, 0.84, 1.0)),
    ("Lower edge", (-0.5, -0.8, 0.35), 0.009, 0.55, (1.0, 0.84, 0.64)),
]:
    light = bpy.data.lights.new(name, "AREA")
    light.energy = watts
    light.shape = "DISK"
    light.size = reach * size
    light.color = color
    obj = bpy.data.objects.new(name, light)
    scene.collection.objects.link(obj)
    obj.location = center + studio_vector(position) * reach
    point_at(obj, center)

camera_data = bpy.data.cameras.new("Review camera")
camera = bpy.data.objects.new("Review camera", camera_data)
scene.collection.objects.link(camera)
scene.camera = camera
camera_data.type = "ORTHO"
camera_data.ortho_scale = reach * 1.28
camera_data.clip_start = reach * 0.01
camera_data.clip_end = reach * 20
directions = {
    "front": (0, 0, 1),
    "oblique": (0.43, 0.15, 0.92),
    "side": (1, 0.04, 0),
    "top": (0, 1, 0.08),
    "back": (-0.35, 0.12, -0.93),
}
renders = []
for view in args.views:
    if view not in directions:
        raise ValueError(f"Unknown view: {view}")
    camera.location = center + studio_vector(directions[view]).normalized() * reach * 2.5
    point_at(camera, center)
    destination = output / f"{source.stem}-{view}.png"
    scene.render.filepath = str(destination)
    bpy.ops.render.render(write_still=True)
    renders.append(str(destination))
print(json.dumps({"input": str(source), "units": "metres", "meshCount": len(badge_meshes), "bounds": {"min": list(minimum), "max": list(maximum)}, "referenceSizeMm": args.reference_size_mm, "fixedTarget": list(center), "renders": renders, "browserScreenshot": False}))
