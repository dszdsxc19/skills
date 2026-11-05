"""Screen-space graphics over versioned Blender frames; adapt draw_graphics()."""
import argparse
import json
import math
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PAPER = (239, 234, 223)
NAVY = "#263e49"
TEAL = "#397e80"


@lru_cache(maxsize=32)
def font(size, bold=False):
    size = max(1, size)
    f = ImageFont.truetype(str(ROOT/"assets/fonts/NotoSansSC.ttf"), size)
    f.set_variation_by_axes([900 if bold else 600])
    return f


def balanced_lines(value, size, width):
    f = font(size); result = []
    while f.getlength(value) > width:
        target = f.getlength(value)/math.ceil(f.getlength(value)/width)
        options = []
        for i in range(1, len(value)):
            length = f.getlength(value[:i])
            if length > width:
                break
            if value[i] in "，。！？、；：":
                continue
            options.append((abs(length-target)+(0 if value[i-1] in "，。！？、；：" else size*1.6), i))
        cut = min(options)[1]; result.append(value[:cut]); value = value[cut:]
    return result+[value]


def put(draw, xy, value, size, color=NAVY, bold=False):
    draw.text(xy, str(value), font=font(size, bold), fill=color, anchor="lt")


def draw_graphics(layer, film, shot, t):
    """Editable topic-specific graphics. The example displays scan events."""
    width, height = film["width"], film["height"]
    unit = min(width/720, height/1280)
    d = ImageDraw.Draw(layer)
    title_size = round(53*unit)
    put(d, (44*unit, 73*unit), shot.get("label", ""), round(18*unit))
    for row, line in enumerate(shot.get("headline", [film["title"]])):
        y = (147+row*73)*unit
        if row == 1:
            d.rectangle((43*unit, y+48*unit, 46*unit+font(title_size, True).getlength(line), y+61*unit), fill="#dfbc72")
        put(d, (43*unit, y), line, title_size, bold=True)
    count = sum(t >= event["time"] for event in film["events"] if event.get("kind") == "scan")
    put(d, (44*unit, 337*unit), "已检测 / 示例", round(18*unit), "#727976")
    put(d, (41*unit, 367*unit), f"{count:02}", round(87*unit), TEAL, True)
    put(d, (170*unit, 425*unit), "件", round(23*unit))
    caption = next((c for seg in film["segments"] for c in seg["captions"] if c["start"] <= t <= c["end"]+.1), None)
    if caption:
        size = round(23*unit); lines = balanced_lines(caption["text"], size, width-110*unit)
        top = height-105*unit-len(lines)*31*unit
        d.rounded_rectangle((35*unit, top-12*unit, width-35*unit, height-72*unit), radius=9*unit, fill=(250, 248, 241, 245))
        for i, line in enumerate(lines):
            put(d, ((width-font(size).getlength(line))/2, top+i*31*unit), line, size)
    d.rectangle((0, height-67*unit, width, height), fill=(*PAPER, 255))
    put(d, (43*unit, height-54*unit), film.get("disclosure", ""), round(16*unit), "#727976")
    d.line((44*unit, height-20*unit, width-44*unit, height-20*unit), fill="#d3d1c7", width=max(1, round(2*unit)))
    d.line((44*unit, height-20*unit, 44*unit+(width-88*unit)*t/film["duration"], height-20*unit), fill=TEAL, width=max(1, round(2*unit)))


def draw_graphic_scene(film, shot, t):
    """Replace this simple diagram for a pure 2D shot such as a bill or chart."""
    result = Image.new("RGBA", (film["width"], film["height"]), PAPER+(255,))
    d = ImageDraw.Draw(result)
    progress = min(1, max(0, (t-shot["start"])/(shot["end"]-shot["start"])))
    y = round(film["height"]*.60)
    d.rounded_rectangle((60, y, film["width"]-60, y+60), radius=15, fill="#d3d1c7")
    d.rounded_rectangle((60, y, 60+(film["width"]-120)*progress, y+60), radius=15, fill=TEAL)
    return result


def compose(image, film, shot, t):
    size = (film["width"], film["height"])
    base = Image.new("RGBA", size, PAPER+(255,))
    if image is not None:
        if image.size != size:
            raise ValueError(f"Frame dimensions mismatch: {image.size} != {size}")
        base = Image.alpha_composite(base, image.convert("RGBA"))
    else:
        base = draw_graphic_scene(film, shot, t)
    gradient = np.zeros((size[1], size[0], 4), np.uint8); gradient[:, :, :3] = PAPER
    gradient[:, :, 3] = (255*np.clip((.38*size[1]-np.arange(size[1]))/(.14*size[1]), 0, 1))[:, None].astype(np.uint8)
    base = Image.alpha_composite(base, Image.fromarray(gradient))
    layer = Image.new("RGBA", size)
    draw_graphics(layer, film, shot, t)
    return Image.alpha_composite(base, layer).convert("RGB")


def checked_entry(manifest, film, shot):
    if manifest["spec"] != {k: film[k] for k in ["width", "height", "fps", "frames"]}:
        raise ValueError("Render manifest is from a different timeline; render the changed shots.")
    entry = manifest["shots"][shot["id"]]
    if any(entry[k] != shot[k] for k in ["start_frame", "end_frame"]) or entry["mode"] != shot.get("mode", "3d"):
        raise ValueError(f"Shot cache range or mode changed: {shot['id']}")
    expected_spec = {k: film[k] for k in ["width", "height", "fps"]}
    if entry.get("spec") != expected_spec:
        raise ValueError(f"Shot cache output specification changed: {shot['id']}")
    return entry


def frame_image(film, manifest, shot, index):
    if shot.get("mode", "3d") == "graphic":
        return None
    entry = checked_entry(manifest, film, shot)
    path = ROOT/entry["directory"]/f"frame-{index:06}.png"
    return Image.open(path).convert("RGBA")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stills", action="store_true")
    parser.add_argument("--movie", action="store_true")
    args = parser.parse_args()
    film = json.loads((ROOT/"timeline.json").read_text())
    full = ROOT/"render/manifest.json"
    manifest = json.loads(full.read_text()) if full.exists() else None
    if args.stills:
        preview = manifest or json.loads((ROOT/"qa/preview_manifest.json").read_text())
        images = []
        for shot in film["shots"]:
            index = (shot["start_frame"]+shot["end_frame"])//2
            image = compose(frame_image(film, preview, shot, index), film, shot, index/film["fps"])
            image.save(ROOT/f"qa/{shot['id']}.jpg", quality=94)
            images.append(image)
        thumb_w = min(360, film["width"]); thumb_h = round(film["height"]*thumb_w/film["width"])
        sheet = Image.new("RGB", (thumb_w*len(images), thumb_h), PAPER)
        for i, image in enumerate(images):
            sheet.paste(image.resize((thumb_w, thumb_h)), (i*thumb_w, 0))
        sheet.save(ROOT/"out/storyboard.jpg", quality=94)
        images[0].save(ROOT/"out/poster.jpg", quality=94)
    if args.movie:
        if manifest is None:
            raise ValueError("Full 3D frames have not been rendered.")
        for shot in film["shots"]:
            entry = checked_entry(manifest, film, shot)
            if entry["mode"] == "3d":
                if len(entry["frame_indices"]) != shot["end_frame"]-shot["start_frame"]:
                    raise ValueError(f"Incomplete frame range: {shot['id']}")
        credits = json.loads((ROOT/"audio/credits.json").read_text())
        output = ROOT/"out"/film.get("output_name", "final.mp4")
        command = ["ffmpeg", "-v", "warning", "-f", "rawvideo", "-pix_fmt", "rgb24",
                   "-s", f"{film['width']}x{film['height']}", "-r", str(film["fps"]), "-i", "pipe:0"]
        if credits["audio_enabled"]:
            command += ["-i", str(ROOT/"audio/final.wav"), "-c:a", "aac", "-b:a", "192k"]
        command += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-metadata", "comment="+json.dumps(credits, ensure_ascii=False),
                    "-frames:v", str(film["frames"]), "-y", str(output)]
        with (ROOT/"qa/encode.log").open("w") as log:
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log)
            try:
                for index in range(film["frames"]):
                    shot = next(s for s in film["shots"] if s["start_frame"] <= index < s["end_frame"])
                    image = compose(frame_image(film, manifest, shot, index), film, shot, index/film["fps"])
                    process.stdin.write(image.tobytes())
                process.stdin.close()
                if process.wait() != 0:
                    raise RuntimeError("FFmpeg failed; inspect qa/encode.log")
            except BaseException:
                process.kill(); raise
        shutil.copy2(ROOT/"audio/credits.json", ROOT/"out/credits.json")
        print("MOVIE", output, output.stat().st_size, flush=True)


if __name__ == "__main__":
    main()
