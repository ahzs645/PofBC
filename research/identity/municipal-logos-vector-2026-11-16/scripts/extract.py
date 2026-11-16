"""Extract logos drawn as vector paths in PDFs, as clean SVGs.

Every shape written is a path the PDF itself draws, in the PDF's own colour (as MuPDF reports it in
RGB); nothing is traced, redrawn or recoloured. Jobs are listed in jobs.json next to this script:

  {"id", "pdf" (path under the downloads dir), "sha256", "page" (1-based), "rect" [x0,y0,x1,y1] in PDF points,
   "out" (path under public/), "title",
   optional "skip": [drawing indices to leave out], "only": [indices to keep],
   optional "excludeFill": ["#ffffff", ...] colours to leave out (e.g. a page ground),
   optional "maxSize": drawings wider/taller than this are left out (page grounds, rules)}

    python3 -I extract.py <downloads-dir> [job-id ...]

The PDFs are not kept in this package; source-register.json gives each one's URL, and every job
checks the SHA-256 of the file it is given.
"""
import hashlib, json, sys
from pathlib import Path
import pymupdf

HERE = Path(__file__).resolve().parent
PKG = HERE.parent
ROOT = PKG.parents[2]
hexof = lambda rgb: "#%02x%02x%02x" % tuple(round(v * 255) for v in rgb)
num = lambda v: f"{v:.2f}".rstrip("0").rstrip(".") if abs(v) >= 0.005 else "0"


def path_of(items, closed):
    d, at = [], None
    for kind, *pts in items:
        if kind == "re":
            r = pts[0]
            d.append(f"M{num(r.x0)} {num(r.y0)}H{num(r.x1)}V{num(r.y1)}H{num(r.x0)}Z"); at = None; continue
        if kind == "qu":
            q = pts[0]
            d.append("M" + "L".join(f"{num(p.x)} {num(p.y)}" for p in (q.ul, q.ur, q.lr, q.ll)) + "Z"); at = None; continue
        start = pts[0]
        if at is None or abs(at.x - start.x) > 1e-3 or abs(at.y - start.y) > 1e-3:
            if d and closed and not d[-1].endswith("Z"):
                d.append("Z")
            d.append(f"M{num(start.x)} {num(start.y)}")
        if kind == "l":
            d.append(f"L{num(pts[1].x)} {num(pts[1].y)}")
        elif kind == "c":
            d.append("C" + " ".join(f"{num(p.x)} {num(p.y)}" for p in pts[1:]))
        at = pts[-1]
    s = "".join(d)
    return s + ("Z" if closed and not s.endswith("Z") else "")


def run(job):
    pdf = SRC / job["pdf"]
    data = pdf.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    if sha != job["sha256"]:
        sys.exit(f"{job['id']}: {pdf.name} is not the PDF this extraction was checked against ({sha})")
    page = pymupdf.open(stream=data, filetype="pdf")[job["page"] - 1]
    rect = pymupdf.Rect(job["rect"])
    excl = set(job.get("excludeFill", []))
    shapes, box = [], None
    for i, dr in enumerate(page.get_drawings()):
        if not dr["rect"].intersects(rect) or i in job.get("skip", []):
            continue
        if "only" in job and i not in job["only"]:
            continue
        if not (rect.contains(dr["rect"]) or job.get("allowOverlap")):
            continue
        if job.get("maxSize") and max(dr["rect"].width, dr["rect"].height) > job["maxSize"]:
            continue
        attrs = []
        if "f" in dr["type"]:
            if hexof(dr["fill"]) in excl:
                continue
            attrs.append(f'fill="{hexof(dr["fill"])}"')
            if dr.get("even_odd"):
                attrs.append('fill-rule="evenodd"')
            if dr.get("fill_opacity", 1) < 0.999:
                attrs.append(f'fill-opacity="{num(dr["fill_opacity"])}"')
        else:
            attrs.append('fill="none"')
        if "s" in dr["type"]:
            attrs.append(f'stroke="{hexof(dr["color"])}" stroke-width="{num(dr["width"])}"')
            if dr.get("lineCap") and max(dr["lineCap"]) > 0:
                attrs.append(f'stroke-linecap="{["butt", "round", "square"][max(dr["lineCap"])]}"')
            if dr.get("lineJoin"):
                attrs.append(f'stroke-linejoin="{["miter", "round", "bevel"][int(dr["lineJoin"])]}"')
            if dr.get("stroke_opacity", 1) < 0.999:
                attrs.append(f'stroke-opacity="{num(dr["stroke_opacity"])}"')
        closed = "f" in dr["type"] or dr.get("closePath")
        shapes.append(f'<path d="{path_of(dr["items"], closed)}" {" ".join(attrs)}/>')
        r = dr["rect"]
        if "s" in dr["type"]:
            r = r + (-dr["width"] / 2, -dr["width"] / 2, dr["width"] / 2, dr["width"] / 2)
        box = r if box is None else box | r
    m = job.get("margin", 0.5)
    vb = (box.x0 - m, box.y0 - m, box.width + 2 * m, box.height + 2 * m)
    scale = job.get("scale", 4)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(num(v) for v in vb)}" '
           f'width="{num(vb[2] * scale)}" height="{num(vb[3] * scale)}">'
           f"<title>{job['title']}</title>" + "".join(shapes) + "</svg>\n")
    out = ROOT / "public" / job["out"]
    out.write_text(svg)
    print(f"{job['id']}: {out.relative_to(ROOT)} {len(shapes)} paths, {len(svg)} bytes, sha256 {hashlib.sha256(svg.encode()).hexdigest()}")


jobs = json.loads((HERE / "jobs.json").read_text())
SRC = Path(sys.argv[1])
want = sys.argv[2:]
for job in jobs:
    if not want or job["id"] in want:
        run(job)
