"""Builds the gallery's display copies of the collected vector logos.

The collected files are kept exactly as they were found (build-collected-marks.mjs checks each
against its checksum), so a white logo meant for a navy page, or a file with a wide margin, arrives
that way. For each collected SVG this writes a copy for the gallery to show on the page's own light
and dark grounds, and leaves the source file alone for download:

1. The copy is trimmed to the logo itself (its viewBox is cut to what it draws), so every logo is
   sized by its own extent and not by however much margin its file happened to carry.
2. For each of the two grounds, ink that would disappear into it — black lettering on the dark page,
   a white logo on the light one — is redrawn: neutral ink is reversed, as a logo's own reverse
   artwork would be, and coloured ink is lightened or darkened only as far as it needs to be read,
   keeping its hue. Only ink that meets the page is redrawn: white lettering inside a green badge
   stays white, because it reads against the badge, not the page.

The copies stay vector: they are recoloured by changing the file's own colour values. Raster files
(PNG, JPEG, GIF, and EPS previews) are left as they are for now. Per-logo settings are in
collected-display-overrides.json; the manifest (src/gallery/collectedDisplay.js) records which
copies were redrawn, so the gallery can say so.

Run: npm run build:collected-display (Python 3 with numpy, scipy and Pillow; Node for resvg)
"""

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageColor
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
OUT_DIR = "identity-display"
OVERRIDES = json.loads((ROOT / "scripts/collected-display-overrides.json").read_text())

# The page grounds a tile can sit on: the lighter is the light theme's tinted page (art sits on
# --page; covers on a checker no darker than it), the dark theme's card surface.
GROUNDS = {"light": "#eceae4", "dark": "#211e1a"}
MAX_HEIGHT, MAX_WIDTH = 480, 2400


# ── Colour ─────────────────────────────────────────────────────────────────────────────────────

def to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def lin_to_oklab(rgb):
    m1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                   [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    m2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                   [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    return np.cbrt(rgb @ m1.T) @ m2.T


def oklab_to_lin(lab):
    m1 = np.array([[1, 0.3963377774, 0.2158037573],
                   [1, -0.1055613458, -0.0638541728],
                   [1, -0.0894841775, -1.2914855480]])
    m2 = np.array([[4.0767416621, -3.3077115913, 0.2309699292],
                   [-1.2684380046, 2.6097574011, -0.3413193965],
                   [-0.0041960863, -0.7034186147, 1.7076147010]])
    return ((lab @ m1.T) ** 3) @ m2.T


def oklab_to_lin_clipped(lab):
    """Back to linear RGB, giving up chroma rather than lightness or hue to stay in gamut."""
    lo = np.zeros(len(lab))
    hi = np.ones(len(lab))
    for _ in range(16):
        mid = (lo + hi) / 2
        rgb = oklab_to_lin(np.column_stack([lab[:, 0], lab[:, 1] * mid, lab[:, 2] * mid]))
        ok = np.all((rgb >= -1e-4) & (rgb <= 1 + 1e-4), axis=1)
        lo = np.where(ok, mid, lo)
        hi = np.where(ok, hi, mid)
    return np.clip(oklab_to_lin(np.column_stack([lab[:, 0], lab[:, 1] * lo, lab[:, 2] * lo])), 0, 1)


def luminance(lin):
    return lin @ np.array([0.2126, 0.7152, 0.0722])


def contrast(y, ground_y):
    return (np.maximum(y, ground_y) + 0.05) / (np.minimum(y, ground_y) + 0.05)


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0, 1)
    return t * t * (3 - 2 * t)


def hex_rgb(value):
    return np.array(ImageColor.getrgb(value)[:3], dtype=float) / 255


# How faint ink must be against a ground before it is redrawn (a contrast ratio range: all of it
# redrawn below the first, none above the second), and the contrast coloured ink is taken to.
FAINT = {"dark": (2.2, 3.6), "light": (1.4, 2.0)}
TARGET = {"dark": 5.0}


def redraw(rgb, theme):
    """Each colour as it is drawn on a theme's ground, and how much it had to change (0 to 1).

    Neutral ink is reversed, as a logo's own reverse artwork is: black to near white on the dark
    page, white to near black on the light one, greys mirrored. On the dark page coloured ink keeps
    its hue and is lightened only as far as the target contrast; on the light page it is left alone,
    since a brand's yellows and light greens are printed on white as they are.
    """
    ground_y = luminance(to_linear(hex_rgb(GROUNDS[theme])))
    lin = to_linear(rgb)
    lab = lin_to_oklab(lin)
    lightness, chroma = lab[:, 0], np.hypot(lab[:, 1], lab[:, 2])
    weight = smoothstep(0.03, 0.08, chroma)
    amount = smoothstep(FAINT[theme][1], FAINT[theme][0], contrast(luminance(lin), ground_y))
    if theme == "light":
        amount = amount * (1 - weight)
        target = np.column_stack([0.16 + 0.4 * (1 - lightness), lab[:, 1], lab[:, 2]])
    else:
        lo, hi = lightness.copy(), np.ones_like(lightness)
        for _ in range(18):
            mid = (lo + hi) / 2
            y = luminance(oklab_to_lin_clipped(np.column_stack([mid, lab[:, 1], lab[:, 2]])))
            enough = contrast(y, ground_y) >= TARGET[theme]
            hi, lo = np.where(enough, mid, hi), np.where(enough, lo, mid)
        neutral = 0.97 - 0.3 * lightness
        target = np.column_stack([(1 - weight) * neutral + weight * hi, lab[:, 1], lab[:, 2]])
    mixed = lab + (target - lab) * amount[:, None]
    return to_srgb(oklab_to_lin_clipped(mixed)), amount


def facing_mask(alpha, amount, facing_share):
    """Which faint pixels belong to ink that meets the page, rather than sitting on other ink.

    Faint pixels are grouped into connected shapes. A shape is redrawn when at least
    `facing_share` of what borders it is page (transparency); a shape bordered mostly by other ink
    — lettering on a badge, a knockout inside a box — keeps its colour, since it reads against that.
    """
    faint = (amount > 0.2) & (alpha > 0.1)
    if not faint.any():
        return faint
    labels, count = ndimage.label(faint, structure=np.ones((3, 3)))
    neighbour = ndimage.grey_dilation(labels, size=(3, 3))
    ring = (neighbour > 0) & ~faint
    clear = np.bincount(neighbour[ring & (alpha <= 0.1)], minlength=count + 1)
    inked = np.bincount(neighbour[ring & (alpha > 0.1)], minlength=count + 1)
    share = clear / np.maximum(clear + inked, 1)
    redrawn = share >= facing_share
    redrawn[0] = False
    return redrawn[labels] & faint


# ── Helpers ─────────────────────────────────────────────────────────────────────────────────────

def border(rgb, width=2):
    return np.concatenate([rgb[:width].reshape(-1, 3), rgb[-width:].reshape(-1, 3),
                           rgb[:, :width].reshape(-1, 3), rgb[:, -width:].reshape(-1, 3)])


def trim_box(alpha, threshold=0.06):
    rows = np.where((alpha > threshold).any(axis=1))[0]
    cols = np.where((alpha > threshold).any(axis=0))[0]
    if not len(rows):
        return 0, 0, alpha.shape[1], alpha.shape[0]
    return cols[0], rows[0], cols[-1] + 1, rows[-1] + 1


# ── Vector files ───────────────────────────────────────────────────────────────────────────────

COLOUR_PROPERTY = re.compile(
    r"((?:fill|stroke|stop-color|flood-color)\s*(?:=\s*[\"']|:)\s*)(#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)|[a-zA-Z]+)")
ROOT_TAG = re.compile(r"<(?:\w+:)?svg\b[^>]*>", re.S)
SKIP = {"none", "currentcolor", "transparent", "inherit", "url"}


def parse_colour(value):
    """An SVG colour value as RGB from 0 to 1, including the rgb(12.5%, …) form PDF exports use."""
    if value.lower() in SKIP:
        return None
    match = re.fullmatch(r"rgba?\(\s*([^)]*)\)", value.strip())
    if match:
        parts = [p.strip() for p in re.split(r"[\s,/]+", match.group(1)) if p.strip()][:3]
        try:
            return np.array([float(p[:-1]) / 100 if p.endswith("%") else float(p) / 255 for p in parts])
        except ValueError:
            return None
    try:
        return np.array(ImageColor.getrgb(value)[:3], dtype=float) / 255
    except ValueError:
        return None


def hex_of(rgb):
    return "#%02x%02x%02x" % tuple(int(round(v * 255)) for v in np.clip(rgb, 0, 1))


def set_attribute(tag, name, value):
    pattern = re.compile(r'(\s%s\s*=\s*)(["\'])[^"\']*\2' % re.escape(name))
    if pattern.search(tag):
        return pattern.sub(lambda m: f'{m.group(1)}"{value}"', tag, count=1)
    return tag[:-1].rstrip("/") + f' {name}="{value}"' + ("/>" if tag.endswith("/>") else ">")


def view_box(tag):
    match = re.search(r'viewBox\s*=\s*["\']([^"\']+)["\']', tag)
    if match:
        return [float(v) for v in re.split(r"[\s,]+", match.group(1).strip())]
    size = [re.search(r'\s%s\s*=\s*["\']([\d.]+)' % name, tag) for name in ("width", "height")]
    return [0, 0, float(size[0].group(1)), float(size[1].group(1))]


def rasterize(jobs):
    result = subprocess.run(["node", str(ROOT / "scripts/rasterize-collected-svg.mjs")],
                            input=json.dumps(jobs), capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


def load(path):
    image = Image.open(path)
    image.load()
    return np.asarray(image.convert("RGBA"), dtype=float) / 255


def build_vector(asset, settings, work):
    """A trimmed, and where its ink needs it, recoloured copy of a vector file. None if the file
    draws its own ground, which the raster route deals with."""
    source = PUBLIC / asset["file"]
    text = source.read_text(encoding="utf-8")
    # Make the default black explicit, so lettering drawn with no fill can be recoloured too.
    root_tag = ROOT_TAG.search(text).group(0)
    if not re.search(r"\sfill\s*=", root_tag):
        text = text.replace(root_tag, set_attribute(root_tag, "fill", "#000000"), 1)
        root_tag = ROOT_TAG.search(text).group(0)
    vx, vy, vw, vh = view_box(root_tag)
    staged = work / f"{asset['id']}.svg"
    staged.write_text(text, encoding="utf-8")
    smooth = rasterize([{"src": str(staged), "out": str(work / f"{asset['id']}-aa.png"), "height": MAX_HEIGHT,
                         "maxWidth": 2400, "aspect": vw / vh}])[0]
    rgba = load(smooth["out"])
    if (border(rgba[..., 3:4].repeat(3, axis=2))[:, 0] > 0.5).mean() > 0.6:
        return None
    left, top, right, bottom = trim_box(rgba[..., 3])
    sx, sy = vw / rgba.shape[1], vh / rgba.shape[0]
    pad = 0.5 * max(sx, sy)
    box = [vx + left * sx - pad, vy + top * sy - pad, (right - left) * sx + 2 * pad, (bottom - top) * sy + 2 * pad]
    trimmed_tag = root_tag
    for name in ("x", "y"):
        trimmed_tag = re.sub(r'\s%s\s*=\s*(["\'])[^"\']*\1' % name, "", trimmed_tag)
    trimmed_tag = set_attribute(trimmed_tag, "viewBox", " ".join(f"{v:.3f}".rstrip("0").rstrip(".") for v in box))
    trimmed_tag = set_attribute(trimmed_tag, "width", f"{box[2]:.2f}")
    trimmed_tag = set_attribute(trimmed_tag, "height", f"{box[3]:.2f}")
    trimmed = text.replace(root_tag, trimmed_tag, 1)
    aspect = box[2] / box[3]

    # Each place the file sets a colour is decided on its own, since one colour can be both the
    # lettering beside an emblem and the emblem's outline. To see what each one paints, the file is
    # drawn once more, without anti-aliasing, with every such colour swapped for a code of its own.
    # Colours inside a mask (whose luminance is its meaning) and gradient stops keep their values;
    # what they paint is left as it is.
    masked = [m.span() for m in re.finditer(r"<(?:\w+:)?mask\b.*?</(?:\w+:)?mask>", trimmed, re.S)]
    places = []
    for match in COLOUR_PROPERTY.finditer(trimmed):
        colour = parse_colour(match.group(2))
        inside_mask = any(start <= match.start() < end for start, end in masked)
        if colour is not None and not inside_mask and not match.group(1).lstrip().startswith("stop-color"):
            places.append((match.start(2), match.end(2), colour))
    if len(places) > 4000:
        raise SystemExit(f"{asset['id']}: too many colour values to tell apart ({len(places)})")
    code = lambda k: ((k + 1) // 256 * 16 + 8, (k + 1) // 16 % 16 * 16 + 8, (k + 1) % 16 * 16 + 8)
    coded, last = [], 0
    for k, (start, end, _) in enumerate(places):
        coded += [trimmed[last:start], "#%02x%02x%02x" % code(k)]
        last = end
    coded.append(trimmed[last:])
    staged.write_text("".join(coded), encoding="utf-8")
    crisp = rasterize([{"src": str(staged), "out": str(work / f"{asset['id']}-px.png"), "height": MAX_HEIGHT,
                        "maxWidth": 2400, "aspect": aspect, "antialias": False}])[0]
    pixels = load(crisp["out"])
    values = np.round(pixels[..., :3] * 255).astype(int)
    levels = np.clip(np.round((values - 8) / 16), 0, 15).astype(int)
    exact = (np.abs(values - (levels * 16 + 8)) <= 4).all(axis=2) & (pixels[..., 3] > 0.99)
    place = np.where(exact, levels[..., 0] * 256 + levels[..., 1] * 16 + levels[..., 2] - 1, -1)
    place[place >= len(places)] = -1
    alpha = pixels[..., 3]

    outputs = {}
    for theme in ("light", "dark"):
        name = f"{asset['id']}.{theme}.svg"
        content, recoloured = trimmed, False
        if settings.get(theme, True) is True and places:
            new_colours, amounts = redraw(np.array([colour for _, _, colour in places]), theme)
            amount = np.where(place >= 0, amounts[np.maximum(place, 0)], 0)
            mask = facing_mask(alpha, amount, settings.get("facing", 0.5))
            faint = np.bincount(place[(amount > 0.2) & (place >= 0)], minlength=len(places))
            facing = np.bincount(place[mask & (place >= 0)], minlength=len(places))
            swap = [faint[k] > 0 and facing[k] >= 0.5 * faint[k] and amounts[k] > 0.05 for k in range(len(places))]
            if DEBUG:
                for k, (start, end, colour) in enumerate(places):
                    if faint[k]:
                        print(f"  {theme} {trimmed[start:end]:>32} faint={faint[k]:6d} facing={facing[k]:6d} -> {hex_of(new_colours[k]) if swap[k] else 'kept'}")
            if any(swap):
                parts, last = [], 0
                for k, (start, end, _) in enumerate(places):
                    if swap[k]:
                        parts += [trimmed[last:start], hex_of(new_colours[k])]
                        last = end
                parts.append(trimmed[last:])
                content, recoloured = "".join(parts), True
        outputs[theme] = (name, content, recoloured)
    if outputs["dark"][1] == outputs["light"][1]:
        outputs["dark"] = outputs["light"]
    entry = {}
    for theme, (name, content, recoloured) in outputs.items():
        (PUBLIC / OUT_DIR / name).write_text(content, encoding="utf-8")
        entry[theme] = {"file": f"{OUT_DIR}/{name}", "aspect": round(aspect, 4), "recoloured": recoloured}
        # A logo whose parts lie over one another so that no recolouring keeps them apart is shown
        # in its own colours on a light plate of its own on that ground.
        if settings.get(theme) == "plate":
            entry[theme]["plate"] = True
    return entry


def collected_assets():
    script = ("import('./src/gallery/collectedData.js').then(({ COLLECTED_BODIES, COLLECTED_SPECIMENS }) =>"
              " console.log(JSON.stringify([...COLLECTED_BODIES, ...COLLECTED_SPECIMENS].flatMap((each) => each.assets))))")
    result = subprocess.run(["node", "--input-type=module", "-e", script], cwd=ROOT, capture_output=True, text=True, check=True)
    return json.loads(result.stdout)


DEBUG = False


def main():
    global DEBUG
    DEBUG = "--debug" in sys.argv
    only = set(sys.argv[1:]) - {"--debug"}
    assets = collected_assets()
    unknown = set(OVERRIDES) - {a["id"] for a in assets} - {"_comment"}
    if unknown:
        raise SystemExit(f"Overrides name unknown assets: {sorted(unknown)}")
    (PUBLIC / OUT_DIR).mkdir(exist_ok=True)
    manifest_path = ROOT / "src/gallery/collectedDisplay.js"
    manifest = {}
    if only and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text().split("= ", 1)[1])
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for asset in assets:
            if only and asset["id"] not in only:
                continue
            settings = OVERRIDES.get(asset["id"], {})
            if asset["format"] != "svg" or not asset.get("isVector") or settings.get("skip"):
                continue
            entry = build_vector(asset, settings, work)
            if entry is None:
                print(asset["id"], "draws its own ground; left as it is")
                continue
            manifest[asset["id"]] = entry
            print(asset["id"],
                  "light-redrawn" if entry["light"]["recoloured"] else "", "dark-redrawn" if entry["dark"]["recoloured"] else "")
    ordered = {asset["id"]: manifest[asset["id"]] for asset in assets if asset["id"] in manifest}
    manifest_path.write_text(
        "// Generated by scripts/build_collected_display.py: each collected file's display copies for the\n"
        "// light and dark page — its ground removed, trimmed, and where its ink would disappear, redrawn.\n"
        f"export const COLLECTED_DISPLAY = {json.dumps(ordered, indent=1)}\n")
    keep = {Path(e[t]["file"]).name for e in ordered.values() for t in ("light", "dark")}
    for stale in (PUBLIC / OUT_DIR).iterdir():
        if stale.name not in keep and not only:
            stale.unlink()


if __name__ == "__main__":
    main()
