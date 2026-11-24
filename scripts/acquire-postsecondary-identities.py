#!/usr/bin/env python3
"""Stage source images, then archive only explicitly approved, hash-matched specimens."""
import datetime
import hashlib
import io
import json
import sys
import urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research/identity/postsecondary-2026-11-24"
REGISTRY = json.loads((RESEARCH / "source-register.json").read_text())
CANDIDATES = {a["id"]: (r, a) for r in REGISTRY["records"] for a in r["artworkCandidates"]}
LIMIT = 20 * 1024 * 1024

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def inspect(data):
    if len(data) > LIMIT:
        raise ValueError("Image exceeds size limit")
    with Image.open(io.BytesIO(data)) as im:
        if im.format not in ("PNG", "JPEG"):
            raise ValueError("Only original PNG/JPEG specimens accepted by this importer")
        fmt = {"PNG": "png", "JPEG": "jpg"}[im.format]
        width, height = im.size
        im.verify()
    return fmt, width, height

def digest(data):
    return hashlib.sha256(data).hexdigest()

def stage(folder):
    folder.mkdir(parents=True, exist_ok=True)
    if (folder / "review.json").exists():
        raise ValueError("Review already exists; use a new staging directory")
    review = []
    for aid, (_, a) in CANDIDATES.items():
        try:
            req = urllib.request.Request(a["sourceUrl"], headers={"User-Agent": "PofBC identity research/1.0"})
            with urllib.request.urlopen(req, timeout=30) as response:
                if not response.geturl().startswith("https://"):
                    raise ValueError("Non-HTTPS redirect")
                data = response.read(LIMIT + 1)
            fmt, w, h = inspect(data)
            (folder / (aid + "." + fmt)).write_bytes(data)
            review.append({"id": aid, "sha256": digest(data), "format": fmt, "width": w, "height": h,
                           "observedDate": datetime.date.today().isoformat(), "approved": False})
        except Exception as exc:
            print(aid, str(exc), file=sys.stderr)
    write_json(folder / "review.json", review)
    print(f"Staged {len(review)} of {len(CANDIDATES)} candidates; none approved.")

def accept(folder):
    path = RESEARCH / "assets-manifest.json"
    manifest = json.loads(path.read_text())
    bodies = {b["id"]: b for b in manifest["bodies"]}
    pending = []
    seen = set()
    for review in json.loads((folder / "review.json").read_text()):
        if review.get("approved") is not True:
            continue
        aid = review["id"]
        if aid in seen:
            raise ValueError("Duplicate reviewed ID: " + aid)
        seen.add(aid)
        r, a = CANDIDATES[aid]
        if review["format"] not in ("png", "jpg"):
            raise ValueError("Unexpected reviewed format")
        data = (folder / (aid + "." + review["format"])).read_bytes()
        fmt, w, h = inspect(data)
        if (digest(data), fmt, w, h) != (review["sha256"], review["format"], review["width"], review["height"]):
            raise ValueError("Reviewed bytes changed: " + aid)
        observed = datetime.date.fromisoformat(review["observedDate"]).isoformat()
        file = f'identity-postsecondary/{r["id"]}/{aid}.{fmt}'
        dest = ROOT / "public" / file
        if dest.exists() and dest.read_bytes() != data:
            raise ValueError("Existing archived bytes differ: " + aid)
        body = bodies.setdefault(r["id"], {"id": r["id"], "name": r["name"], "kind": r["kind"],
                              "current": r["current"], "graphNode": None, "status": "asset-collected", "assets": []})
        existing = next((x for x in body["assets"] if x["id"] == aid), None)
        if existing:
            if existing["sha256"] != digest(data) or not dest.exists():
                raise ValueError("Existing manifest entry conflicts or is missing: " + aid)
            continue
        asset = {"id": aid, "label": a["label"], "file": file, "sourceFile": file, "format": fmt,
                 "bytes": len(data), "sha256": digest(data), "width": w, "height": h,
                 "isVector": False, "supplied": False, "reconstruction": False,
                 "sourceUrl": a["sourceUrl"], "sourcePage": a["sourcePage"], "publisher": a["publisher"],
                 "sourceLocator": a["label"], "observedDate": observed,
                 "fidelityNote": "Original downloaded raster, unmodified; visually reviewed before acceptance.",
                 "evidenceType": "published-raster", "notes": a["note"], "dateNote": a["note"]}
        if a.get("publicationDate"):
            asset["sourceDate"] = a["publicationDate"]
        if a.get("sourceReproduction"):
            asset["sourceReproduction"] = True
            asset["historicalDateLabel"] = a["historicalDateLabel"]
            asset["sourceDate"] = "Undated retrospective publication"
        body["assets"].append(asset)
        pending.append((dest, data))
    for dest, data in pending:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    manifest["bodies"] = list(bodies.values())
    write_json(path, manifest)
    print(f"Accepted {len(pending)} reviewed assets. Regenerate identity modules before committing.")

if __name__ == "__main__":
    if len(sys.argv) != 3 or sys.argv[1] not in ("stage", "accept"):
        raise SystemExit("Usage: acquire-postsecondary-identities.py {stage|accept} STAGING_DIR")
    {"stage": stage, "accept": accept}[sys.argv[1]](Path(sys.argv[2]).resolve())
