#!/usr/bin/env python3
"""Build the offline BCFS revision review. All images and measurements are inline.

Run from any directory:
  python build_review_html.py --workspace /path/to/workspace
Optional --output chooses the HTML destination. No network or browser is used.
"""
import argparse
import base64
import html
import json
from pathlib import Path


def data_url(path: Path, mime: str) -> str:
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.workspace.resolve()
    review = root / "work/revision3"
    final = root / "output/BC_Forest_Service_Matches"
    destination = args.output or review / "BCFS_Interactive_Review.html"
    measurements = json.loads((review / "White_Edge_Measurements.json").read_text())

    rows = []
    for region, values in measurements["regions"].items():
        before, after = values["previous"], values["revised"]
        rows.append(
            f"<tr><th scope='row'>{html.escape(region)}</th>"
            f"<td>{before['intersection_over_union']:.1%}</td>"
            f"<td><strong>{after['intersection_over_union']:.1%}</strong></td>"
            f"<td>{before['mean_symmetric_edge_distance_pixels']:.2f} px</td>"
            f"<td><strong>{after['mean_symmetric_edge_distance_pixels']:.2f} px</strong></td></tr>"
        )

    overall = measurements["regions"]["All visible illustration reserve"]
    old, new = overall["previous"], overall["revised"]

    assets = {
        "previous": data_url(review / "prior/BCFS_Matches_Reconstructed.svg", "image/svg+xml"),
        "clean": data_url(final / "BCFS_Matches_Clean.svg", "image/svg+xml"),
        "oldDiagnostic": data_url(review / "old-white-overlay.png", "image/png"),
    }
    replacements = {
        "@@IOU_BEFORE@@": f"{old['intersection_over_union']:.1%}",
        "@@IOU_AFTER@@": f"{new['intersection_over_union']:.1%}",
        "@@EDGE_BEFORE@@": f"{old['mean_symmetric_edge_distance_pixels']:.2f}",
        "@@EDGE_AFTER@@": f"{new['mean_symmetric_edge_distance_pixels']:.2f}",
        "@@BOUNDARY_BEFORE@@": f"{old['boundary_within_2px']['f1']:.1%}",
        "@@BOUNDARY_AFTER@@": f"{new['boundary_within_2px']['f1']:.1%}",
        "@@PHOTO@@": data_url(root / "work/reference-rectified.png", "image/png"),
        "@@REVISED@@": data_url(final / "BCFS_Matches_Reconstructed.svg", "image/svg+xml"),
        "@@DIAGNOSTIC@@": data_url(review / "new-white-overlay.png", "image/png"),
        "@@ROWS@@": "\n".join(rows),
        "@@ASSETS@@": json.dumps(assets, separators=(",", ":")),
        "@@MEASUREMENTS@@": json.dumps(measurements, separators=(",", ":")).replace("</", "<\\/"),
    }
    page = TEMPLATE
    for marker, value in replacements.items():
        page = page.replace(marker, value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(page, encoding="utf-8")
    print(f"Created {destination} ({destination.stat().st_size:,} bytes)")


TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BC Forest Service — vector revision review</title>
<style>
:root{color-scheme:light;--ink:#202a2b;--muted:#5d6868;--line:#d5dad6;--paper:#fafbf7;--teal:#00b6be;--magenta:#db228e;--accent:#225d56}
*{box-sizing:border-box} [hidden]{display:none!important}
body{margin:0;background:#eef0e9;color:var(--ink);font:16px/1.55 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:1280px;margin:auto;padding:28px 28px 54px}h1,h2,p{margin-top:0}h1{font-size:clamp(1.7rem,3vw,2.5rem);line-height:1.15;letter-spacing:-.035em;margin-bottom:12px}h2{font-size:1.3rem;letter-spacing:-.02em;margin-bottom:14px}
.eyebrow{text-transform:uppercase;letter-spacing:.13em;font-size:.72rem;font-weight:800;color:var(--accent);margin-bottom:10px}.intro{max-width:860px;color:var(--muted);margin-bottom:24px}.card{background:var(--paper);border:1px solid var(--line);border-radius:16px;overflow:hidden;margin-bottom:24px}.controls{padding:18px 20px;border-bottom:1px solid var(--line)}.toolbar{display:flex;align-items:end;gap:14px;flex-wrap:wrap}.field{display:flex;flex-direction:column;gap:6px}.field label,.group-label{font-weight:700;font-size:.78rem;color:var(--muted)}.group-label{display:block;margin-bottom:6px}.buttons{display:flex;gap:5px;flex-wrap:wrap}button,select{font:inherit;font-size:.88rem;border:1px solid #bac4be;border-radius:7px;padding:8px 12px;color:var(--ink);background:#fff;min-height:39px}button{cursor:pointer}button:hover{background:#e8eee7}button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);color:#fff}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #c28a14;outline-offset:3px}select{min-width:145px}.slider-row{display:flex;align-items:center;gap:16px;margin-top:18px;flex-wrap:wrap}.slider-field{flex:1;min-width:240px}.slider-head{display:flex;justify-content:space-between;gap:14px;font-size:.82rem;margin-bottom:3px}.slider-head label{font-weight:700}input[type="range"]{width:100%;accent-color:var(--accent);cursor:ew-resize}input:disabled{cursor:default;opacity:.4}.small{font-size:.82rem;color:var(--muted)}.inspection{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:12px}.inspection button{font-size:.78rem;min-height:32px;padding:5px 10px}.legend{display:flex;gap:20px;flex-wrap:wrap;padding:12px 20px;background:#fff;border-bottom:1px solid var(--line);font-size:.83rem}.swatch{display:inline-block;width:13px;height:13px;border-radius:3px;margin-right:7px;vertical-align:-2px}.teal{background:var(--teal)}.magenta{background:var(--magenta)}
.viewport{height:76vh;min-height:420px;max-height:1080px;overflow:auto;background:#d4d7d0;overscroll-behavior:contain}.canvas-space{position:relative;width:max-content;min-width:100%;min-height:100%;padding:20px;display:flex;justify-content:center;align-items:center}.stage{position:relative;flex:0 0 auto;width:min(520px,70vw);aspect-ratio:5/7;box-shadow:0 3px 18px #1e25252e;isolation:isolate;background:#e7f3f2}.stage img{display:block;position:absolute;inset:0;width:100%;height:100%;user-select:none;max-width:none}.vector{clip-path:inset(0 0 0 50%)}.diagnostic{z-index:3}.wipe-line{position:absolute;z-index:4;top:0;bottom:0;left:50%;width:2px;background:#fff;box-shadow:0 0 0 1px #253d3e50;pointer-events:none}.wipe-line:after{content:"↔";position:absolute;left:-15px;top:50%;width:32px;height:32px;text-align:center;line-height:29px;background:white;color:#202a2b;border:1px solid #7c8d85;border-radius:50%;font-size:20px}.image-label{position:absolute;top:10px;padding:3px 7px;border-radius:4px;color:white;background:#142e2cbd;font-size:11px;z-index:5;pointer-events:none}.label-photo{left:10px}.label-vector{right:10px}.viewer-footer{padding:12px 20px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;font-size:.8rem;color:var(--muted)}#status{font-weight:650;color:var(--ink)}.section{padding:24px 26px}.section>p:last-child{margin-bottom:0}.metrics-intro{max-width:960px}.table-wrap{overflow:auto;border:1px solid var(--line);border-radius:10px;margin:20px 0}table{border-collapse:collapse;width:100%;font-size:.86rem;min-width:700px;text-align:left}caption{padding:13px 14px;font-weight:700;text-align:left;background:#edf2eb}th,td{padding:10px 14px;border-top:1px solid var(--line)}thead th{background:#f3f5ef;color:var(--muted);font-size:.76rem}tbody th{font-weight:500}td{font-variant-numeric:tabular-nums;white-space:nowrap}tbody tr:first-child{background:#edf4ed}tbody tr:first-child th{font-weight:750}.notes-grid{display:grid;grid-template-columns:1fr 1fr;gap:28px}.notes-grid p{font-size:.9rem}.notes-grid h3{font-size:1rem;margin:0 0 8px}details{font-size:.83rem;color:var(--muted);margin-top:15px}summary{cursor:pointer;font-weight:700;color:var(--ink)}details p{margin:10px 0 0}.footnote{margin-bottom:0;font-size:.79rem;color:var(--muted)}noscript p{background:#fff5d7;padding:14px;border:1px solid #d9be6c;border-radius:8px}
@media(max-width:700px){main{padding:20px 12px 36px}.controls,.section{padding:16px}.toolbar{gap:12px}.toolbar>.field:first-child{flex:1}.toolbar select{width:100%}.slider-row{gap:8px}.notes-grid{grid-template-columns:1fr;gap:12px}.viewport{height:70vh;min-height:360px}.canvas-space{padding:12px}.viewer-footer{padding:12px 16px}.legend{padding:10px 16px;gap:8px 16px}}
@media print{.controls,.inspection,.viewer-footer,.legend{display:none!important}.viewport{overflow:visible;height:auto;max-height:none;min-height:0}.canvas-space{padding:0;display:block;width:100%}.stage{width:100%!important;height:auto!important;max-width:700px;margin:auto}.card{break-inside:avoid}.section{padding:14px}main{padding:0}.notes-grid{display:block}}
</style>
</head>
<body><main>
<header>
<p class="eyebrow">British Columbia Forest Service · Revision 3</p>
<h1>Vector reconstruction review</h1>
<p class="intro">Compare the photograph with Revision 2 and the new Revision 3 edge contours. Inspect the diagonal opening, child legs and upright at high magnification, or use the colour-coded white-edge overlay.</p>
</header>
<noscript><p>The static view below shows the photograph on the left and the revised vector on the right. Enable JavaScript to use the comparison controls, diagnostic overlays and zoom. All assets are included in this file.</p></noscript>
<section class="card" aria-label="Interactive artwork comparison">
<div class="controls">
<div class="toolbar">
<div class="field"><label for="edition">Artwork version</label><select id="edition"><option value="revised" selected>Revision 3 · textured</option><option value="previous">Revision 2</option><option value="clean">Revision 3 · clean paint</option></select></div>
<div><span class="group-label" id="mode-label">Comparison</span><div class="buttons" role="group" aria-labelledby="mode-label"><button type="button" data-mode="wipe" aria-pressed="true">Wipe</button><button type="button" data-mode="blend" aria-pressed="false">Blend</button><button type="button" data-mode="white" aria-pressed="false">White edges</button></div></div>
<div class="field"><label for="zoom">Zoom</label><select id="zoom"><option value="1" selected>Fit whole poster</option><option value="1.5">150% of fit</option><option value="2">200% of fit</option><option value="3">300% of fit</option><option value="4">400% of fit</option></select></div>
</div>
<div class="slider-row"><div class="slider-field"><div class="slider-head"><label id="range-label" for="comparison-range">Wipe position</label><output id="range-value" for="comparison-range">Photo 50% · vector 50%</output></div><input id="comparison-range" type="range" min="0" max="100" step="1" value="50" aria-describedby="range-value"></div><div class="buttons" role="group" aria-label="View one source"><button type="button" data-mode="photo" aria-pressed="false">Photo only</button><button type="button" data-mode="vector" aria-pressed="false">Vector only</button></div></div>
<div class="inspection"><span class="small">Inspect:</span><button type="button" data-focus="knot">Upper knot</button><button type="button" data-focus="head">Child head</button><button type="button" data-focus="brace">Diagonal opening</button><button type="button" data-focus="legs">Legs</button><button type="button" data-focus="upright">Lower upright</button><button type="button" data-focus="full">Full poster</button><span class="small">Scroll to move around when enlarged.</span></div>
</div>
<div id="diagnostic-legend" class="legend" hidden><span><i class="swatch teal"></i>Missing white — present in photo only</span><span><i class="swatch magenta"></i>Excess white — present in vector only</span><span id="diagnostic-version">Revised white reserve</span></div>
<div class="viewport" id="viewport" tabindex="0" aria-label="Scrollable poster comparison">
<div class="canvas-space"><div class="stage" id="stage">
<img id="photo" src="@@PHOTO@@" width="1000" height="1400" alt="Perspective-registered photograph of the original poster" draggable="false">
<img id="vector" class="vector" src="@@REVISED@@" width="1000" height="1400" alt="Revised textured vector reconstruction" draggable="false">
<img id="diagnostic" class="diagnostic" src="@@DIAGNOSTIC@@" width="1000" height="1400" alt="Revised white-edge diagnostic: teal is missing white and magenta is excess white" draggable="false" hidden>
<div id="wipe-line" class="wipe-line"></div><span id="label-photo" class="image-label label-photo">Photograph</span><span id="label-vector" class="image-label label-vector">Revised vector</span>
</div></div></div>
<div class="viewer-footer"><span id="status" role="status" aria-live="polite">Revised textured vector · wipe comparison</span><span>Shared reference plane: 1000 × 1400 px · Zoom is relative to fit.</span></div>
</section>
<section class="card section">
<h2>White edges: the measured change</h2>
<p class="metrics-intro">White-reserve area overlap changes from <strong>@@IOU_BEFORE@@ to @@IOU_AFTER@@</strong>. Mean boundary distance changes from <strong>@@EDGE_BEFORE@@ to @@EDGE_AFTER@@ normalized pixels</strong>. The boundary F1 score within a two-pixel tolerance changes from <strong>@@BOUNDARY_BEFORE@@ to @@BOUNDARY_AFTER@@</strong>. These measurements evaluate fit to the same photographic mask; close-up contour appearance is reviewed separately.</p>
<div class="table-wrap"><table><caption>White_Edge_Measurements · rounded from the common reference-mask analysis</caption><thead><tr><th scope="col">Region</th><th scope="col">Previous IoU</th><th scope="col">Revised IoU</th><th scope="col">Previous mean edge</th><th scope="col">Revised mean edge</th></tr></thead><tbody>@@ROWS@@</tbody></table></div>
<p class="small">Higher IoU and lower edge distance indicate closer agreement under the fixed comparison. Boundary F1 combines the fraction of each boundary lying within two pixels of the other. The clean and textured versions share the same white-reserve geometry.</p>
<details><summary>How the comparison was made</summary><p>Both artwork versions use the same estimated perspective registration onto a 1000 × 1400 plane. A photographic pale/dark classification is restricted to the illustration region, closed by one pixel, and cleaned using fixed connected-component locations and small-hole filling. The large painted triangular opening is retained. Rendered reserve alpha is thresholded at 127/255. The oval seal footprint is excluded because it obscures the white post. IoU is shared reserve area divided by combined area; edge distance is the pooled symmetric nearest-boundary distance. Region boxes overlap, so their pixel counts must not be added.</p><p>The reference mask is an evaluation aid. The final white boundaries are manually authored Bézier geometry; the mask did not generate the vector paths. Small remaining overlay slivers can reflect contour differences, wear, blur, threshold selection or estimated registration. Original physical dimensions are unverified.</p></details>
</section>
<section class="card section"><h2>The edge refinement</h2><div class="notes-grid"><div><h3>Rebuilt contour details</h3><p>Revision 3 redraws the top scallops, both sides of the diagonal brace, the suspended thread, the child silhouette and the long upright. Deliberate curved brush lobes and recesses replace long facets and abrupt steps. Small source-visible flecks are separate editable paths.</p><p>The contours are manually constructed. The photograph mask evaluates the finished shapes; it does not generate the vector paths.</p></div><div><h3>Reference limits</h3><p>The paint, black illustration, lettering, seal and signature are carried forward from Revision 2. Original physical dimensions, original ink colours, historical typefaces and the signature attribution remain unverified.</p><p>The 5:7 artboard is estimated from a partly cropped photograph. Fine printing wear and camera blur limit how precisely the physical edge can be recovered. The files contain crisp vector geometry, while the photograph retains its own texture and blur.</p></div></div><p class="footnote">All comparison assets and measurement data are embedded. Download this HTML and open it locally; the SVG deliverables contain the separately editable artwork.</p></section>
</main>
<script id="embedded-assets" type="application/json">@@ASSETS@@</script>
<script id="white-edge-measurements" type="application/json">@@MEASUREMENTS@@</script>
<script>
'use strict';
(() => {
  const byId = (id) => document.getElementById(id);
  const embedded = JSON.parse(byId('embedded-assets').textContent);
  const photo = byId('photo'), vector = byId('vector'), diagnostic = byId('diagnostic');
  const assets = { ...embedded, revised: vector.getAttribute('src'), newDiagnostic: diagnostic.getAttribute('src') };
  const viewport = byId('viewport'), stage = byId('stage'), zoom = byId('zoom');
  const edition = byId('edition'), range = byId('comparison-range');
  const names = { previous: 'Revision 2', revised: 'Revision 3 textured vector', clean: 'Revision 3 clean vector' };
  const state = { mode: 'wipe', edition: 'revised', amount: 50 };
  let activeAsset = 'revised';

  function update() {
    const mode = state.mode, n = state.amount;
    if (activeAsset !== state.edition) {
      vector.src = assets[state.edition];
      activeAsset = state.edition;
    }
    vector.alt = names[state.edition];
    photo.hidden = mode === 'vector';
    vector.hidden = mode === 'photo' || mode === 'white';
    diagnostic.hidden = mode !== 'white';
    byId('diagnostic-legend').hidden = mode !== 'white';
    byId('wipe-line').hidden = mode !== 'wipe';
    byId('label-photo').hidden = mode !== 'wipe' || n < 13;
    byId('label-vector').hidden = mode !== 'wipe' || n > 82;
    byId('label-vector').textContent = state.edition === 'previous' ? 'Previous vector' : state.edition === 'clean' ? 'Clean vector' : 'Revised vector';
    vector.style.clipPath = mode === 'wipe' ? `inset(0 0 0 ${n}%)` : 'none';
    vector.style.opacity = mode === 'blend' ? String(n / 100) : '1';
    byId('wipe-line').style.left = `${n}%`;
    range.disabled = !['wipe', 'blend'].includes(mode);
    byId('range-label').textContent = mode === 'blend' ? 'Vector opacity' : mode === 'wipe' ? 'Wipe position' : 'Comparison slider';
    byId('range-value').textContent = mode === 'wipe' ? `Photo ${n}% · vector ${100 - n}%` : mode === 'blend' ? `${n}% vector` : 'Select Wipe or Blend to adjust';
    document.querySelectorAll('[data-mode]').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.mode === mode)));
    if (mode === 'white') {
      const previous = state.edition === 'previous';
      const target = previous ? assets.oldDiagnostic : assets.newDiagnostic;
      if (diagnostic.getAttribute('src') !== target) diagnostic.src = target;
      diagnostic.alt = `${previous ? 'Previous' : 'Revised'} white-edge diagnostic: teal is missing white and magenta is excess white`;
      byId('diagnostic-version').textContent = previous ? 'Previous white reserve' : 'Revised white reserve · same in clean version';
    }
    const suffix = { wipe: 'wipe comparison', blend: 'blend comparison', white: 'white-edge diagnostic', photo: 'photograph only', vector: 'vector only' }[mode];
    byId('status').textContent = mode === 'photo' ? 'Registered photograph only' : `${names[state.edition]} · ${suffix}`;
  }

  function centerOn(x, y) {
    viewport.scrollLeft = stage.offsetLeft + x * stage.clientWidth - viewport.clientWidth / 2;
    viewport.scrollTop = stage.offsetTop + y * stage.clientHeight - viewport.clientHeight / 2;
  }

  function resize(preserve = true, focus = null) {
    const old = stage.getBoundingClientRect(), frame = viewport.getBoundingClientRect();
    const cx = old.width ? (frame.left + viewport.clientWidth / 2 - old.left) / old.width : .5;
    const cy = old.height ? (frame.top + viewport.clientHeight / 2 - old.top) / old.height : .5;
    const pad = window.innerWidth <= 700 ? 24 : 40;
    const fitWidth = Math.max(100, Math.min(viewport.clientWidth - pad, (viewport.clientHeight - pad) * 5 / 7));
    const width = Math.round(fitWidth * Number(zoom.value));
    stage.style.width = `${width}px`;
    stage.style.height = `${width * 1.4}px`;
    requestAnimationFrame(() => {
      if (focus) centerOn(focus[0], focus[1]);
      else if (preserve && Number(zoom.value) > 1) centerOn(Math.max(0, Math.min(1, cx)), Math.max(0, Math.min(1, cy)));
      else { viewport.scrollTop = 0; viewport.scrollLeft = 0; }
    });
  }

  edition.addEventListener('change', () => { state.edition = edition.value; update(); });
  range.addEventListener('input', () => { state.amount = Number(range.value); update(); });
  document.querySelectorAll('[data-mode]').forEach((button) => button.addEventListener('click', () => { state.mode = button.dataset.mode; update(); }));
  zoom.addEventListener('change', () => resize(true));
  const focusPoints = { knot: [.353, .09], head: [.34, .385], brace: [.67,.19], legs: [.38,.59], upright: [.81,.80] };
  document.querySelectorAll('[data-focus]').forEach((button) => button.addEventListener('click', () => {
    const key = button.dataset.focus;
    zoom.value = key === 'full' ? '1' : '3';
    resize(false, focusPoints[key] || null);
    viewport.focus({ preventScroll: true });
  }));
  if (typeof ResizeObserver === 'function') new ResizeObserver(() => resize(true)).observe(viewport);
  else window.addEventListener('resize', () => resize(true));
  update();
  resize(false);
})();
</script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
