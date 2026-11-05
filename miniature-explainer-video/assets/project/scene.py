"""Runnable sorting example. Replace the assets and pose(t) for the actual film."""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import geometry as g


def smooth(value):
    value = min(1, max(0, value))
    return value * value * (3 - 2 * value)


def main():
    if not bpy.app.background:
        raise RuntimeError("This starter initializes a new scene. Run it in a separate blender -b process.")
    parser = argparse.ArgumentParser()
    parser.add_argument("--stills", action="store_true")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    film = json.loads((ROOT / "timeline.json").read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = film["width"], film["height"]
    sc.render.resolution_percentage = 100
    sc.render.fps = film["fps"]
    sc.frame_start, sc.frame_end = 1, film["frames"]
    sc.render.image_settings.file_format = next(i.identifier for i in sc.render.image_settings.bl_rna.properties["file_format"].enum_items if i.identifier == "PNG")
    sc.render.image_settings.color_mode = "RGBA"
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.exposure = .15
    sc.eevee.taa_render_samples = 16
    sc.eevee.use_fast_gi = True
    methods = [i.identifier for i in sc.eevee.bl_rna.properties["fast_gi_method"].enum_items]
    if "AMBIENT_OCCLUSION_ONLY" in methods:
        sc.eevee.fast_gi_method = "AMBIENT_OCCLUSION_ONLY"
    sc.eevee.fast_gi_distance = 3
    sc.world = bpy.data.worlds.new("Soft neutral studio")
    sc.world.use_nodes = True
    background = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
    background.inputs["Color"].default_value = (.78, .81, .83, 1)
    background.inputs["Strength"].default_value = .5
    sun_data = bpy.data.lights.new("Morning key", "SUN")
    sun = bpy.data.objects.new("Morning key", sun_data); sc.collection.objects.link(sun)
    sun.rotation_euler = (.45, -.40, -.5); sun_data.energy = 1.4; sun_data.angle = .3
    area_data = bpy.data.lights.new("Large softbox", "AREA")
    area = bpy.data.objects.new("Large softbox", area_data); sc.collection.objects.link(area)
    area.location = (-3, -4, 8); area_data.energy = 350; area_data.shape = "DISK"; area_data.size = 6
    area.rotation_euler = (Vector((0, 0, .5)) - area.location).to_track_quat("-Z", "Y").to_euler()
    g.use_set("Sorting set", 0)
    g.floor("Sorting island", (7, 4.6))
    g.box("Conveyor base", (0, 0, .62), (5.9, 1.78, .40), "metal", .06)
    g.box("Conveyor surface", (0, 0, .86), (5.8, 1.63, .08), "rubber", .025)
    rollers = []
    for x in [-2.83, 2.83]:
        rollers.append(g.cyl("Conveyor roller", (x, 0, .79), .16, 1.72, "metal", rot=(math.pi / 2, 0, 0)))
    for y in [-.82, .82]:
        g.box("Detector column", (0, y, 1.40), (.18, .18, 1.15), "teal")
    g.box("Detector overhead", (0, 0, 1.98), (.24, 1.83, .14), "teal")
    g.text("SCAN", (0, -.94, 1.97), .14, "white")
    light = g.ball("Scan indicator", (0, -.95, 1.70), .07, "green")
    events = [e for e in film["events"] if e.get("kind") == "scan"]
    parcels = []
    for i, event in enumerate(events):
        root = g.empty("Parcel " + str(i + 1), parent=g.ACTIVE)
        g.box("Parcel carton", (0, 0, 0), (.52, .55, .46), ["woodlight", "orange", "blue"][i % 3], parent=root)
        g.box("Parcel tape", (0, 0, .238), (.065, .57, .015), "paper", .003, root)
        g.box("Parcel label", (.13, -.04, .25), (.17, .24, .012), "white", .005, root)
        for j in range(5):
            g.box("Barcode", (.075 + j * .022, -.04, .259), (.008, .12, .003), "navy", 0, root)
        parcels.append((root, event))
    g.box("Output divider", (1.85, 0, .99), (1.70, .035, .18), "metal", .01)
    camera_data = bpy.data.cameras.new("Miniature lens")
    camera = bpy.data.objects.new("Camera", camera_data); sc.collection.objects.link(camera); sc.camera = camera
    camera_data.type = "ORTHO"; camera_data.shift_y = .13; camera_data.clip_end = 80
    for frame in range(film["frames"]):
        t = frame / film["fps"]
        shot = next(s for s in film["shots"] if s["start_frame"] <= frame < s["end_frame"])
        close = shot["id"] == "scan"
        target = Vector((.2 if close else 0, 0, .9))
        camera.location = target + Vector((8, -12, 10))
        camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
        camera_data.ortho_scale = 9.3 if close else 10.8
        camera.keyframe_insert(data_path="location", frame=frame + 1)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame + 1)
        camera_data.keyframe_insert(data_path="ortho_scale", frame=frame + 1)
        for i, (parcel, event) in enumerate(parcels):
            x = (t - event["time"]) * 1.28
            y = (-.45 if i % 2 == 0 else .45) * smooth(x / .9)
            parcel.location = (x, y, 1.13)
            parcel.scale = (1 if -2.65 <= x <= 2.65 else .001,) * 3
            parcel.keyframe_insert(data_path="location", frame=frame + 1)
            parcel.keyframe_insert(data_path="scale", frame=frame + 1)
        flash = max([math.exp(-((t - e["time"]) / .12) ** 2) for e in events] or [0])
        light.scale = (1 + .55 * flash,) * 3
        light.keyframe_insert(data_path="scale", frame=frame + 1)
        for roller in rollers:
            roller.rotation_euler.y = t * 3
            roller.keyframe_insert(data_path="rotation_euler", frame=frame + 1)
    sc.frame_set(1)
    bpy.ops.file.pack_all()
    for font in bpy.data.fonts:
        if font.filepath and font.filepath != "<builtin>":
            font.filepath = "//assets/fonts/" + Path(font.filepath).name
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "scene.blend"))
    if args.stills:
        import render
        render.render_shots(stills=True)
    print("SCENE_SAVED", ROOT / "scene.blend", len(sc.objects), "objects", flush=True)


if __name__ == "__main__":
    main()
