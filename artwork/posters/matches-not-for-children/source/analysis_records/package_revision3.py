#!/usr/bin/env python3
"""Package already-rendered Revision 3 artwork, reviews and construction sources.

This script never regenerates artwork or invokes the old V2 builders. Run only
after the V3 master, PDF, preview, analysis, compiled reserve and HTML are final:

    python work/revision3/package_revision3.py

It fails before packaging if required inputs are absent or the HTML embeds stale
artwork/metrics. Existing V2 paint, seal, signature and source assets are retained.
"""
from pathlib import Path
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
import argparse
import ast
import base64
import hashlib
import json
import re
import shutil
import zipfile

import fitz
from PIL import Image, ImageDraw, ImageFont


NS = 'http://www.w3.org/2000/svg'
FONT_ROOT = Path('/usr/share/fonts/truetype/dejavu')


def cp(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_ROOT / ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')), size)


def paste_fit(board, path, box):
    image = Image.open(path).convert('RGB')
    image.thumbnail((box[2]-box[0], box[3]-box[1]), Image.Resampling.LANCZOS)
    board.paste(image, (box[0]+(box[2]-box[0]-image.width)//2, box[1]))


def fingerprint(element):
    """Compare visible layer construction without namespace-prefix formatting."""
    def serial(e):
        if e.tag.rsplit('}', 1)[-1] in {'title', 'desc', 'metadata'}:
            return None
        return [e.tag, sorted(e.attrib.items()), (e.text or '').strip(),
                [s for child in e if (s := serial(child)) is not None]]
    return hashlib.sha256(json.dumps(serial(element), sort_keys=True).encode()).hexdigest()


def check_html(path, current, previous, metrics):
    page = path.read_text()
    class Inspect(HTMLParser):
        def __init__(self):
            super().__init__()
            self.images = {}
        def handle_starttag(self, tag, attrs):
            attributes = dict(attrs)
            if tag == 'img' and 'id' in attributes:
                self.images[attributes['id']] = attributes.get('src', '')
    parsed = Inspect()
    parsed.feed(page)
    assets_match = re.search(r'<script id="embedded-assets" type="application/json">([\s\S]*?)</script>', page)
    metrics_match = re.search(r'<script id="white-edge-measurements" type="application/json">([\s\S]*?)</script>', page)
    if not assets_match or not metrics_match:
        raise ValueError('Interactive HTML is missing embedded assets or measurement data.')
    assets = json.loads(assets_match.group(1))
    if json.loads(metrics_match.group(1)) != metrics:
        raise ValueError('Interactive HTML contains stale white-edge measurements.')
    for name, uri, expected in [
        ('revised', parsed.images.get('vector', ''), current / 'BCFS_Matches_Reconstructed.svg'),
        ('clean', assets.get('clean', ''), current / 'BCFS_Matches_Clean.svg'),
        ('previous', assets.get('previous', ''), previous / 'BCFS_Matches_Reconstructed.svg'),
    ]:
        if not uri.startswith('data:') or ',' not in uri:
            raise ValueError(f'Interactive HTML lacks an inline {name} SVG.')
        if base64.b64decode(uri.split(',', 1)[1], validate=True) != expected.read_bytes():
            raise ValueError(f'Interactive HTML contains stale {name} artwork.')
    if '[hidden]{display:none!important}' not in page:
        raise ValueError('Interactive HTML is missing its hidden-element override.')


def validate_vectors(out, prior):
    validation = {'revision': 3, 'svg': {}, 'unchanged_from_revision2': {}}
    for path in sorted(out.rglob('*.svg')):
        root = ET.parse(path).getroot()
        counts, external = {}, []
        for element in root.iter():
            name = element.tag.rsplit('}', 1)[-1]
            counts[name] = counts.get(name, 0) + 1
            for key, value in element.attrib.items():
                if key.rsplit('}', 1)[-1] in {'href', 'src'} and not value.startswith('#'):
                    external.append(value)
                for target in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)', value):
                    if not target.strip().startswith('#'):
                        external.append(target)
            if name == 'style':
                text = element.text or ''
                if '@import' in text:
                    external.append('@import')
                for target in re.findall(r'url\(\s*[\"\']?([^\)\"\']+)', text):
                    if not target.strip().startswith('#'):
                        external.append(target)
        entry = {'bytes': path.stat().st_size, 'path_objects': counts.get('path', 0),
                 'embedded_images': counts.get('image', 0), 'live_text': counts.get('text', 0),
                 'filters': counts.get('filter', 0), 'external_references': len(external)}
        if any(entry[k] for k in ('embedded_images', 'live_text', 'filters', 'external_references')):
            raise ValueError(f'Non-vector or externally dependent SVG: {path}: {entry}')
        validation['svg'][path.relative_to(out).as_posix()] = entry

    for filename in ('BCFS_Matches_Reconstructed.svg', 'BCFS_Matches_Clean.svg'):
        old, new = ET.parse(prior / filename).getroot(), ET.parse(out / filename).getroot()
        unchanged = {}
        for layer_id in ('painted-background', 'matchstick-illustration', 'headline-lettering',
                         'forest-service-oval', 'footer-lettering', 'centennial-caption', 'publication-marks'):
            a = old.find(f'.//{{{NS}}}g[@id="{layer_id}"]')
            b = new.find(f'.//{{{NS}}}g[@id="{layer_id}"]')
            unchanged[layer_id] = a is not None and b is not None and fingerprint(a) == fingerprint(b)
        if not all(unchanged.values()):
            raise ValueError(f'Revision 3 was scoped to white edges, but other layers changed: {filename}: {unchanged}')
        validation['unchanged_from_revision2'][filename] = unchanged

    with fitz.open(out / 'BCFS_Matches_Reconstructed.pdf') as pdf:
        validation['pdf'] = {'pages': len(pdf),
                             'embedded_images': sum(len(page.get_images(full=True)) for page in pdf),
                             'page_size_points': [pdf[0].rect.width, pdf[0].rect.height]}
    if validation['pdf']['pages'] != 1 or validation['pdf']['embedded_images']:
        raise ValueError('Final PDF must have one page and zero embedded bitmap images.')
    preview = Image.open(out / 'BCFS_Matches_Preview.png')
    if preview.size != (2000, 2800):
        raise ValueError(f'Expected 2000x2800 preview, found {preview.size}.')
    validation['preview'] = {'width': 2000, 'height': 2800, 'format': 'PNG'}
    return validation


def report_text(metrics, residue_included=False):
    regions = metrics['regions']
    old = regions['All visible illustration reserve']['previous']
    new = regions['All visible illustration reserve']['revised']
    area_rows, boundary_rows = [], []
    regressions = []
    for name, region in regions.items():
        a, b = region['previous'], region['revised']
        area_rows.append(f"| {name} | {a['intersection_over_union']:.2%} | {b['intersection_over_union']:.2%} | {a['mean_symmetric_edge_distance_pixels']:.2f} px | {b['mean_symmetric_edge_distance_pixels']:.2f} px |")
        boundary_rows.append(f"| {name} | {a['boundary_within_1px']['f1']:.1%} | {b['boundary_within_1px']['f1']:.1%} | {a['boundary_within_2px']['f1']:.1%} | {b['boundary_within_2px']['f1']:.1%} |")
        if b['mean_symmetric_edge_distance_pixels'] > a['mean_symmetric_edge_distance_pixels'] + 0.005 or b['boundary_within_2px']['f1'] < a['boundary_within_2px']['f1'] - 0.0005:
            regressions.append(name)
    tradeoff = ('Some measures are mixed in ' + ', '.join(regressions) + '. The tables retain those outcomes rather than presenting the revision as uniformly better at every tolerance.'
                if regressions else 'All listed regions have a lower mean boundary distance and a higher boundary F1 within two pixels under this fixed comparison. That still does not establish every tiny edge feature as historically correct.')
    residue_note = ('A sparse group of manually drawn pale amber residue marks is also included inside the reserve, clipped to its geometry and placed beneath the black illustration. These marks describe the clearly visible deposits studied near the child’s right leg and the upright foot. They do not change the reserve-mask geometry or its boundary scores.'
                    if residue_included else '')
    return f'''# BC Forest Service poster — Revision 3

## Result and scope

Revision 3 continues the white-edge work after the enlarged V2 edges still looked unfinished. The change is confined to the pale illustration reserve. The painted background, black matchstick drawing and ties, headline, seal, signature and other lettering retain their Revision 2 construction.

{residue_note}

On the same fixed photograph mask, mean white-boundary distance is **{new['mean_symmetric_edge_distance_pixels']:.2f} px**, compared with **{old['mean_symmetric_edge_distance_pixels']:.2f} px** in V2. Boundary F1 within two normalized pixels is **{new['boundary_within_2px']['f1']:.1%}**, compared with **{old['boundary_within_2px']['f1']:.1%}**. Reserve-area IoU is **{new['intersection_over_union']:.2%}**, compared with **{old['intersection_over_union']:.2%}**. These values describe fit to the registered photograph; none is a historical-authenticity or whole-poster fidelity score.

## Why the earlier area score was insufficient

V2 already achieved {old['intersection_over_union']:.1%} white-reserve IoU. A broad white shape can overlap most of the photographed reserve while retaining visible polygonal corners, stiff side runs or oversized local notches. Those defects occupy little area, so a high area score can coexist with an unfinished appearance when enlarged.

This pass therefore used close photo/vector comparisons to reconstruct recognizable local shapes, then checked both boundary position and area overlap. It did not apply a blanket smoothing operation to the old contours. The new boundaries include specific lobes, recesses, narrow returns and changes in width where the photograph supports them.

## What changed in the contours

| Region | Revision 3 work |
| --- | --- |
| Upper beam and triangular opening | More specific top-edge lobes, shallow recesses and lower paint cut-ins. The edge inside the triangular opening has a less faceted profile. |
| Diagonal brace | Local shoulders and broken paint-edge shapes replace long stepped transitions. A small number of source-visible flecks are constructed separately within the path geometry. |
| Thread and child | The thread column has subtler local width changes. The head, shoulders, arms, crotch, legs and foot reserve include deliberate small recesses and rounded brush ends. |
| Upright | Asymmetric shoulder steps, the broken taper beside the middle head, the narrow right-hand notch, the lower left return and the near-horizontal bottom shelf are reconstructed individually. |

The construction uses manually specified Bézier geometry, plus a few deliberately placed source-supported flecks. Photograph masks are used for separate review; their contours do not generate the vector artwork. The compiled `source/reserves_v3.py` contains the complete current reserve and reads no photograph or diagnostic mask.

## Common-reference measurements

Both V2 and V3 are evaluated on the **same 1000 × 1400 reference plane**, with the same estimated perspective transformation, fixed photographic mask and seal exclusion. The metrics below come from `review/White_Edge_Measurements.json` in this package.

### Area and boundary distance

| Region | V2 IoU | V3 IoU | V2 mean edge distance | V3 mean edge distance |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(area_rows)}

The full-reserve 95th-percentile boundary distance is {new['edge_distance_p95_pixels']:.2f} px in V3 and {old['edge_distance_p95_pixels']:.2f} px in V2. Excess white area is {new['extra_white_pixels']:,} pixels versus {old['extra_white_pixels']:,}; missing white area is {new['missing_white_pixels']:,} pixels versus {old['missing_white_pixels']:,}. Region boxes overlap, so regional pixel counts must not be summed.

### Boundary agreement at close tolerances

| Region | V2 F1 within 1 px | V3 F1 within 1 px | V2 F1 within 2 px | V3 F1 within 2 px |
| --- | ---: | ---: | ---: | ---: |
{chr(10).join(boundary_rows)}

At each tolerance, precision is the fraction of the vector boundary lying within that distance of the reference boundary; recall measures the converse. F1 is their harmonic mean. This makes a small local edge displacement more visible in the evaluation than area IoU alone. A “two-pixel” result refers to the normalized comparison plane, not millimetres on an original print.

{tradeoff}

## Overlay method and limits

The fixed reference mask uses pale/dark photographic classification within the illustration region, a one-pixel closing operation, components selected at fixed figure locations and filling of enclosed holes smaller than 50 pixels. The large painted opening is retained. The candidate reserve is rasterized at 1000 × 1400 and its alpha coverage is thresholded at 127/255. The seal footprint, expanded to radii 74 × 90 normalized pixels, is excluded: the photograph cannot establish the hidden reserve beneath it.

In the overlay, **teal marks white missing from the reconstruction** and **magenta marks white extending beyond the reference mask**. Boundary distance is the pooled symmetric nearest-boundary distance. The same definitions are applied to both revisions.

The photograph includes print wear, camera blur and colour fringe. Tiny isolated slivers can therefore reflect the mask threshold or estimated registration as well as an imperfect vector edge. The larger connected discrepancies are more useful editing targets. The contours remain an interpretation of the visible painted edge, and fine translucent yellow residue is not fully recreated as holes in the white reserve: doing that would expose stronger paint underneath and exaggerate its contrast.

## How to inspect the result

Start with `BCFS_White_Edge_Details.png` for the upper knot and child-head regions from the supplied screenshots. `BCFS_Contour_Refinement.png` expands the comparison to the diagonal opening, child legs and upright shoulder. `BCFS_White_Edge_Overlay.png` and the offline `BCFS_Interactive_Review.html` provide the common-reference diagnostics.

The HTML offers V2, V3 textured and V3 clean artwork, wipe/blend comparison, white-edge diagnostics, photo/vector-only views, and fit/150%/200%/300%/400% zoom. It includes its image and SVG assets. Its JavaScript was syntax-checked; browser interaction was not exercised in this environment. The static boards can be inspected independently.

Additional component crops and notes are in `review/edge_components/`. They isolate one contributor's changes while holding other contours at V2; their regional measurements are supporting analysis rather than substitutes for the final merged metrics above.

## What remains from Revision 2

The more varied vector paint, continuous lower red edge, fitted seal lettering and manually drawn signature remain in place. Their construction and separate limitations are documented in `review/history/revision2/Revision_2_Report.md` and the retained paint/detail review files. No new paint, seal or lettering fidelity claim is made by this edge-only revision.

The **5:7 ratio** remains an estimate from a partly cropped photograph. The 1000 × 1400 coordinate plane is a working registration, not a verified physical print size. Colours match the supplied photograph's appearance and have not been calibrated to original inks. URW Bookman Demi remains a fitted visual substitute for the seal lettering; its historical identity is unconfirmed. The apparent signature reading “J.J. ANDRE” and artist attribution remain unconfirmed.

## Construction and validation records

- `source/reserves_v3.py` and `source/reserves_v3.svg`: independent compiled reserve, ready for assembly.
- `source/upper_reserves.py`, `source/child_reserves.py` and `source/upright_reserve.py`: editable contour sources and their component SVGs.
- `source/rebuild_poster.py`: assembles current reserves with retained V2 paint/seal/signature assets and the existing drawing/lettering.
- `source/analyze_white_edges.py`: portable rerun of the common-reference evaluation; requires the package's fixed masks, normalized photograph, preview and Inkscape.
- `review/diagnostics/`: reference, V2 and V3 masks for reproduction.
- `review/Vector_Validation.json`: structural checks of delivered SVGs and the exported PDF, plus unchanged-layer checks against V2.

The SVG checks reject embedded images, live text, filters and external references. The one-page PDF is checked for zero embedded bitmap images. Review PNGs and the photograph remain raster evidence outside the vector artwork.
'''


def readme_text(metrics, residue_included=False):
    a = metrics['regions']['All visible illustration reserve']['previous']
    b = metrics['regions']['All visible illustration reserve']['revised']
    residue_note = ('A sparse residue group is included inside the reserve, clipped to its boundary and beneath the black ink. Its manually drawn pale amber marks are separate from the underlying V2 paint field; the boundary measurements do not score these interior marks.\n\n'
                    if residue_included else '')
    return f'''# BC Forest Service — MATCHES ARE NOT FOR CHILDREN!!

## Revision 3 — continued white-edge refinement

This editable vector reconstruction now has a further pass on the pale illustration reserve. The top beam, diagonal opening, suspended thread, child and right upright have more specific curved paint edges, small recesses and changes in width. Revision 3 changes the white reserve; the background, black illustration and ties, headline, seal, signature and other lettering retain Revision 2 artwork.

{residue_note}The paths are constructed geometry. The photograph was not automatically traced to produce the artwork. Pixel masks are used separately for diagnostic comparison.

## Start here

| File | Purpose |
| --- | --- |
| `BCFS_Matches_Reconstructed.svg` | Current complete textured vector poster with separate editable layers |
| `BCFS_Matches_Clean.svg` | Same V3 reserve and drawing with simplified paint |
| `BCFS_Matches_Reconstructed.pdf` | One-page vector PDF for placement or print preparation |
| `BCFS_Matches_Preview.png` | 2000 × 2800 raster preview |
| `BCFS_Interactive_Review.html` | Offline V2/V3/clean comparison, wipe, blend, diagnostics and zoom |
| `BCFS_Reconstruction_Comparison.png` | Registered photograph, V2 and V3 full-poster comparison |
| `BCFS_White_Edge_Details.png` | Upper knot and child-head close comparisons |
| `BCFS_Contour_Refinement.png` | Diagonal opening, child legs and upright shoulder close comparisons |
| `BCFS_White_Edge_Overlay.png` | V2/V3 diagnostic overlay with colour key and measurements |
| `review/Revision_3_Report.md` | Current findings, method, exact scope and remaining limits |
| `review/White_Edge_Measurements.json` | Authoritative merged V2/V3 metrics |
| `review/history/revision2/` | Preserved V2 report, metrics and reference artwork |
| `BCFS_White_Reserve.svg` | Complete V3 white reserve on a transparent artboard |
| `BCFS_White_Edge_Residue.svg` | Sparse pale pigment deposits clipped to the reserve; separate editable component |
| `BCFS_Paint_Background.svg` | Retained V2 textured paint component |
| `BCFS_Matchstick_Illustration.svg` | Separate shafts, heads, highlights, thread and ties |
| `BCFS_Headline.svg` | Custom headline outlines |
| `BCFS_Forest_Service_Oval.svg` | Retained transparent V2 seal |
| `BCFS_Centennial_Mark.svg` | Reconstructed centennial symbol |
| `source/` | Current construction scripts, component vectors and original supplied photograph |

## What the measurements mean

The full visible reserve's mean boundary distance changes from **{a['mean_symmetric_edge_distance_pixels']:.2f} to {b['mean_symmetric_edge_distance_pixels']:.2f} px**. Boundary F1 within two pixels changes from **{a['boundary_within_2px']['f1']:.1%} to {b['boundary_within_2px']['f1']:.1%}**; area IoU changes from **{a['intersection_over_union']:.2%} to {b['intersection_over_union']:.2%}**. All refer to the same 1000 × 1400 registered photograph and fixed mask.

A high area IoU can hide small but visible facets or misplaced corners. This pass therefore uses enlarged visual comparisons and boundary measures alongside area overlap. These figures are photo-mask agreement, not whole-poster fidelity or historical-authenticity percentages. See the V3 report for one- and two-pixel boundary F1 by region.

In the overlays, **teal means white missing from the vector** and **magenta means excess white**. The seal-covered lower post is excluded. Regional boxes overlap and their counts must not be summed. `review/BCFS_Alignment_Review.png` is the current white-edge review; `review/Previous_Ink_Alignment.png` retains earlier drawing/lettering analysis.

## Editing and limitations

Open either SVG master in a vector editor. The main layers are paint, white reserve, matchstick illustration, headline, seal, footer, centennial captions and publication marks. Lettering is outlined; a few drawn details remain editable strokes. Use the clean version for layout or recolouring and the textured version for the finished appearance.

The 5:7 ratio is estimated from the photograph, whose top paper edge is partly cropped. Original physical dimensions and calibrated printing colours are unverified. The PDF page is a scalable export canvas and contains no bleed or printer-specific colour profile. Fine print grain, translucent residue, small hidden details and some edge flecks remain interpreted. Seal lettering uses fitted URW Bookman Demi outlines as a visual substitute; the historical face is unconfirmed. The apparent signature reading “J.J. ANDRE” and attribution are unconfirmed.

The review HTML is self-contained. JavaScript syntax was checked; browser interaction was not exercised in this environment. Static comparison boards provide the same visual evidence independently.

## Regenerate the current artwork

The delivered SVGs need no Python or fonts to open. To rebuild them from the included final components:

```bash
python3 -m pip install -r source/requirements.txt
python3 source/reserves_v3.py
python3 source/rebuild_poster.py
```

`reserves_v3.py` is independent and complete: it reads no photo, mask or previous reserve. The poster builder uses that SVG plus the retained V2 paint, seal and signature SVGs. It does not load the photograph. It uses the DejaVu Sans Bold and DejaVu Serif Bold paths declared near its start for small outlined lettering; adjust those paths on another system. Regeneration overwrites the poster SVGs, so preserve direct SVG edits first.

To edit and reassemble the three reserve components before rebuilding:

```bash
python3 source/upper_reserves.py
python3 source/child_reserves.py
python3 source/upright_reserve.py
python3 source/assemble_reserves.py
python3 source/rebuild_poster.py
```

The retained `reserves_v2.py`/`.svg` are historical sources and are not used by the current poster builder. Paint and seal generation sources remain included for provenance; they do not need to be rerun for this revision.

Export the regenerated SVG with Inkscape if needed:

```bash
inkscape BCFS_Matches_Reconstructed.svg --export-type=png --export-width=2000 --export-filename=BCFS_Matches_Preview.png
inkscape BCFS_Matches_Reconstructed.svg --export-type=pdf --export-filename=BCFS_Matches_Reconstructed.pdf
python3 source/analyze_white_edges.py
```

The portable analyzer reads the current master, retained V2 preview, normalized photo and fixed masks in this package. It requires Inkscape and rewrites the current diagnostics. Individual contributors' analysis scripts are retained in `source/analysis_records/`; their original workspace paths are documented and they are not the portable entry point.

## Validation and provenance

`review/Vector_Validation.json` records SVG parsing checks for embedded images, live text, filters and external references, PDF checks for a single page with zero embedded bitmap images, and checks that non-reserve layers match V2. The supplied photograph is retained as `source/Supplied_Photograph.jpg`; it is not embedded in the poster SVG or PDF. Current raster reviews are reference evidence and previews, not vector artwork.
'''


def portable_analyzer(revision):
    analysis = (revision / 'analyze_edges.py').read_text()
    replacements = {
        "ROOT=Path(__file__).resolve().parents[2]": "ROOT=Path(__file__).resolve().parent.parent",
        "REV=ROOT/'work/revision3'": "REV=ROOT/'review'/'diagnostics'",
        "OUT=ROOT/'output/BC_Forest_Service_Matches'": "OUT=ROOT",
        "prior=REV/'prior'": "prior=ROOT/'review'/'history'/'revision2'",
        "prior/'review/Reference_Perspective_Normalized.png'": "ROOT/'review/Reference_Perspective_Normalized.png'",
        "prior/'review/diagnostics/reference-reserve-mask-root.png'": "ROOT/'review/diagnostics/reference-reserve-mask-root.png'",
        "prior/'review/diagnostics/revised-reserve-mask.png'": "ROOT/'review/diagnostics/previous-reserve-mask.png'",
        "prior/'review/White_Edge_Measurements.json'": "prior/'White_Edge_Measurements.json'",
        "prior/'BCFS_Matches_Preview.png'": "ROOT/'review/Previous_Reconstruction.png'",
    }
    for before, after in replacements.items():
        if before not in analysis:
            raise ValueError(f'Analyzer portability patch needs review; missing expression: {before}')
        analysis = analysis.replace(before, after)
    ast.parse(analysis)
    return analysis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.workspace.resolve()
    work, revision = root / 'work', root / 'work/revision3'
    out = root / 'output/BC_Forest_Service_Matches'
    prior = revision / 'prior'
    review, source = out / 'review', out / 'source'
    history, diagnostics = review / 'history/revision2', review / 'diagnostics'

    required = [work / 'reference-rectified.png', work / 'rebuild_poster.py',
                revision / 'reserves_v3.py', revision / 'reserves_v3.svg',
                revision / 'White_Edge_Measurements.json', revision / 'revised-reserve-mask.png',
                revision / 'BCFS_Interactive_Review.html', revision / 'analyze_edges.py',
                revision / 'assemble_reserves.py',
                prior / 'BCFS_Matches_Reconstructed.svg', prior / 'BCFS_Matches_Clean.svg',
                prior / 'BCFS_Matches_Preview.png', prior / 'review/Revision_2_Report.md',
                prior / 'review/White_Edge_Measurements.json',
                prior / 'review/diagnostics/reference-reserve-mask-root.png',
                prior / 'review/diagnostics/revised-reserve-mask.png']
    for name in ['BCFS_Matches_Reconstructed.svg', 'BCFS_Matches_Clean.svg',
                 'BCFS_Matches_Reconstructed.pdf', 'BCFS_Matches_Preview.png',
                 'BCFS_White_Reserve.svg', 'BCFS_White_Edge_Details.png',
                 'BCFS_Contour_Refinement.png', 'BCFS_White_Edge_Overlay.png']:
        required.append(out / name)
    for name in ['paint_v2.svg', 'paint_v2_clean.svg', 'emblem_v2.svg',
                 'emblem_v2_isolated.svg', 'signature_v2.svg', 'headline.py',
                 'headline.svg', 'Supplied_Photograph.jpg', 'requirements.txt']:
        required.append(source / name)
    for stem in ['upper_reserves', 'child_reserves', 'upright_reserve']:
        required.extend([revision / f'{stem}.py', revision / f'{stem}.svg'])
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise FileNotFoundError('V3 inputs are not ready; no packaging performed:\n' + '\n'.join(missing))
    metrics = json.loads((revision / 'White_Edge_Measurements.json').read_text())
    if metrics.get('revision') != 3 or metrics.get('previous_revision') != 2:
        raise ValueError('Expected final Revision 3 versus Revision 2 measurements.')
    for region in metrics['regions'].values():
        for key in ['previous', 'revised']:
            for tolerance in [1, 2]:
                assert 'f1' in region[key][f'boundary_within_{tolerance}px']
    check_html(revision / 'BCFS_Interactive_Review.html', out, prior, metrics)
    analyzer = portable_analyzer(revision)
    current_master = ET.parse(out / 'BCFS_Matches_Reconstructed.svg').getroot()
    previous_master = ET.parse(prior / 'BCFS_Matches_Reconstructed.svg').getroot()
    previous_ids = {element.get('id') for element in previous_master.iter()}
    residue_included = any('residue' in element.get('id', '').lower()
                           and element.get('id') not in previous_ids
                           for element in current_master.iter())

    for directory in [review, source, history, diagnostics]:
        directory.mkdir(parents=True, exist_ok=True)

    # V2 history comes from the immutable snapshot, never current overwritten files.
    for original, name in [
        (prior / 'README.md', 'README.md'),
        (prior / 'review/Revision_2_Report.md', 'Revision_2_Report.md'),
        (prior / 'review/White_Edge_Measurements.json', 'White_Edge_Measurements.json'),
        (prior / 'review/Vector_Validation.json', 'Vector_Validation.json'),
        (prior / 'BCFS_Matches_Reconstructed.svg', 'BCFS_Matches_Reconstructed.svg'),
        (prior / 'BCFS_White_Reserve.svg', 'BCFS_White_Reserve.svg'),
        (prior / 'BCFS_White_Edge_Overlay.png', 'BCFS_White_Edge_Overlay.png'),
    ]:
        if original.exists():
            cp(original, history / name)
    cp(prior / 'BCFS_Matches_Preview.png', review / 'Previous_Reconstruction.png')
    cp(work / 'reference-rectified.png', review / 'Reference_Perspective_Normalized.png')
    cp(out / 'BCFS_White_Edge_Overlay.png', review / 'BCFS_Alignment_Review.png')
    cp(revision / 'White_Edge_Measurements.json', review / 'White_Edge_Measurements.json')
    for source_path, name in [
        (prior / 'review/diagnostics/reference-reserve-mask-root.png', 'reference-reserve-mask-root.png'),
        (prior / 'review/diagnostics/revised-reserve-mask.png', 'previous-reserve-mask.png'),
        (revision / 'revised-reserve-mask.png', 'revised-reserve-mask.png'),
    ]:
        cp(source_path, diagnostics / name)
    for name in ['old-white-overlay.png', 'new-white-overlay.png']:
        if (revision / name).exists():
            cp(revision / name, diagnostics / name)

    # Keep current painter, seal and signature assets untouched; replace only the
    # current assembly script and add independent V3 reserve construction sources.
    cp(work / 'rebuild_poster.py', source / 'rebuild_poster.py')
    for name in ['reserves_v3.py', 'reserves_v3.svg', 'assemble_reserves.py']:
        cp(revision / name, source / name)
    for stem in ['upper_reserves', 'child_reserves', 'upright_reserve']:
        for extension in ['py', 'svg']:
            name = f'{stem}.{extension}'
            # Match the final compiled reserve's paper colour in editable source copies.
            (source / name).write_text((revision / name).read_text().replace('#e6f1ed', '#e7f3f2'))
    for name in ['edge_residue.py', 'edge_residue.svg']:
        if (revision / name).exists():
            cp(revision / name, source / name)
    (source / 'analyze_white_edges.py').write_text(analyzer)
    records = source / 'analysis_records'
    records.mkdir(exist_ok=True)
    for name in ['analyze_edges.py', 'upper_reserves_qa.py', 'child_evaluate.py',
                 'review_upright.py', 'build_review_html.py', 'package_revision3.py']:
        path = revision / name
        if path.exists():
            cp(path, records / name)
    (records / 'README.md').write_text('''# Analysis records\n\nThese scripts preserve the original workspace analysis and packaging workflow. Their relative paths refer to `work/revision3`, `work/revision2`, and the workspace output directory; they are not portable entry points in this archive. Use `../analyze_white_edges.py` from the package root to reproduce the merged final measurements and review boards. Use the independent `../reserves_v3.py` and `../rebuild_poster.py` to rebuild artwork.\n\nComponent comparison boards isolate the component being revised while retaining V2 geometry elsewhere. They supplement the final merged report and must not be mistaken for the full V3 output.\n''')

    component_review = review / 'edge_components'
    component_review.mkdir(exist_ok=True)
    for name in ['child_notes.md', 'child_metrics.json', 'upright_notes.md', 'upright_metrics.json',
                 'child-comparison.png', 'child-overlay-comparison.png',
                 'thread_detail-comparison.png', 'head_detail-comparison.png',
                 'arm_detail-comparison.png', 'leg_detail-comparison.png',
                 'upright-upper-comparison.png', 'upright-middle-comparison.png',
                 'upright-lower-comparison.png', 'upright-overlay-top.png',
                 'upright-overlay-middle.png', 'upright-overlay-bottom.png',
                 'upper_notes.md', 'upper_reserves_notes.md', 'upper-reserves-notes.md']:
        if (revision / name).exists():
            cp(revision / name, component_review / name)
    upper_analysis = revision / 'upper-analysis'
    if upper_analysis.exists():
        for path in sorted(upper_analysis.iterdir()):
            if path.is_file() and (path.name.endswith('-photo-v2-v3.png') or path.name.endswith('-overlay-v2-v3.png') or path.suffix in {'.md', '.json'}):
                cp(path, component_review / 'upper' / path.name)
    for pattern in ['edge-residue*.md', 'edge-residue*.png', 'edge_residue*.md', 'edge_residue*.png']:
        for path in revision.glob(pattern):
            cp(path, component_review / 'residue' / path.name)
    if (revision / 'edge_residue.py').exists():
        (component_review / 'residue').mkdir(exist_ok=True)
        (component_review / 'residue/STATUS.md').write_text(
            '# Interior residue study\n\n' +
            ('Included in the final master as a sparse clipped group beneath the black ink. The reserve geometry and boundary scores are unchanged by this group.\n'
             if residue_included else 'Supporting prototype only. This residue group is not included in the final master artwork.\n'))
    (component_review / 'README.md').write_text('''# Component review crops\n\nThese source-photo/V2/V3 crops and notes document individual contour revisions. In each contributor's comparison the other components can remain at V2, so these are isolated construction reviews. The current complete artwork, merged overlay and authoritative measurements are at the package root and in `../Revision_3_Report.md` and `../White_Edge_Measurements.json`. Pixel units refer to the 1000 × 1400 registration plane.\n''')

    board = Image.new('RGB', (1860, 1120), '#f5f3ec')
    draw = ImageDraw.Draw(board)
    draw.text((40, 28), 'MATCHES ARE NOT FOR CHILDREN · REVISION 3', font=font(32, True), fill='#1d2424')
    draw.text((40, 78), 'Continued white-edge refinement on the same photographic registration', font=font(22), fill='#53615f')
    for x, label, path in [(40, 'SUPPLIED PHOTO', work / 'reference-rectified.png'),
                           (650, 'REVISION 2', prior / 'BCFS_Matches_Preview.png'),
                           (1260, 'REVISION 3', out / 'BCFS_Matches_Preview.png')]:
        draw.text((x, 127), label, font=font(18, True), fill='#415653')
        paste_fit(board, path, (x, 166, x+560, 950))
    comparison_note = ('White edges and interior residue are refined; the underlying paint and foreground remain V2.'
                       if residue_included else 'Only the pale illustration reserve changes in Revision 3; the paint and foreground remain V2.')
    draw.text((40, 988), comparison_note, font=font(21), fill='#1d2424')
    draw.text((40, 1027), 'These comparison images are raster previews. Use the SVG or PDF for vector artwork.', font=font(19), fill='#53615f')
    board.save(out / 'BCFS_Reconstruction_Comparison.png')

    report = report_text(metrics, residue_included)
    sensitivity_path = revision / 'Main_Contour_Sensitivity.json'
    if sensitivity_path.exists():
        sensitivity = json.loads(sensitivity_path.read_text())
        cp(sensitivity_path, review / sensitivity_path.name)
        upper = sensitivity['regions']['Upper beam and diagonal brace']
        whole = sensitivity['regions']['All visible illustration reserve']
        report += f'''\n## Detached-fleck sensitivity check\n\nThe original connected photographic mask has one connected component. V3 adds three small, source-visible detached paper flecks; those features are not represented by that old mask. The primary tables above deliberately retain the unchanged mask and all V3 geometry, so they count the detached features as excess reserve and include their distance in the boundary average. This helps explain the mixed raw result for the upper region.\n\nA supplementary check retains only the largest four-connected component in each of the reference, V2 and V3 masks. Under that same rule for all three masks, the upper-region mean distance changes from {upper['previous']['mean_symmetric_edge_distance_pixels']:.2f} to {upper['revised']['mean_symmetric_edge_distance_pixels']:.2f} px. The full main contour changes from {whole['previous']['mean_symmetric_edge_distance_pixels']:.2f} to {whole['revised']['mean_symmetric_edge_distance_pixels']:.2f} px. This sensitivity result is separate from the primary comparison and does not replace it. Definitions, component areas and exact values are in `Main_Contour_Sensitivity.json`.\n'''
    (revision / 'Revision_3_Report.md').write_text(report)
    (review / 'Revision_3_Report.md').write_text(report)
    (out / 'README.md').write_text(readme_text(metrics, residue_included))
    cp(revision / 'BCFS_Interactive_Review.html', out / 'BCFS_Interactive_Review.html')
    validation = validate_vectors(out, prior)
    validation['optional_edge_residue_included'] = residue_included
    (review / 'Vector_Validation.json').write_text(json.dumps(validation, indent=2))

    archive = root / 'output/BCFS_Vector_Reconstruction.zip'
    temporary = archive.with_name(archive.stem + '.building.zip')
    with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=8) as zip_out:
        for path in sorted(out.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                zip_out.write(path, Path('BC_Forest_Service_Matches') / path.relative_to(out))
    with zipfile.ZipFile(temporary) as zip_in:
        bad_member = zip_in.testzip()
        if bad_member is not None:
            raise ValueError(f'ZIP CRC verification failed: {bad_member}')
        count = len(zip_in.infolist())
    temporary.replace(archive)
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size,
                      'files': count, 'svg_files_checked': len(validation['svg']),
                      'pdf': validation['pdf'], 'reports': ['README.md', 'review/Revision_3_Report.md']}, indent=2))


if __name__ == '__main__':
    main()
