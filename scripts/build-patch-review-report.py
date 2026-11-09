#!/usr/bin/env python3
"""Create a self-contained visual patch review from the durable evidence index.

The report embeds source crops and baseline/candidate previews once per byte hash.
Baseline previews come from the recorded Patcher Git commit; candidate previews
come from --patcher and must match that repository's current manifest. No source
images are fetched and no fidelity scores or review decisions are generated.

Requires Pillow, already used by build-patch-review.py. Example:
  python scripts/build-patch-review-report.py --patcher ../patcher \
    --output /absolute/path/PofBC_Patch_Review_2026-11-08.html
"""
import argparse
import base64
import hashlib
import html
import io
import json
import re
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import quote

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
ATLAS_URL = 'https://drive.google.com/file/d/1FttYbiCfmrQW4TbvcDD7lpVG9Y-gRzs4/view'
STATUS_LABELS = {
    'reconstruct': 'Needs reconstruction',
    'refine': 'Needs refinement',
    'retain': 'Reviewed · retain',
    'source-limited': 'Limited source',
    'interpretation': 'Interpretation',
}
STATUS_ORDER = ['reconstruct', 'refine', 'retain', 'source-limited', 'interpretation']


def esc(value):
    return html.escape(str(value), quote=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def child(root, relative):
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes its root: {relative}')
    return path


def git_bytes(repo, ref, path):
    if not re.fullmatch(r'[0-9a-f]{40}', ref):
        raise ValueError('The report requires a full pinned Git commit.')
    return subprocess.run(
        ['git', '-C', str(repo), 'show', f'{ref}:{path}'],
        check=True, capture_output=True,
    ).stdout


def safe_url(value):
    if value and not value.startswith(('https://', 'http://')):
        raise ValueError(f'Unsupported external URL: {value}')
    return value


def link(url, label, css=''):
    if not url:
        return ''
    return f'<a class="{esc(css)}" href="{esc(safe_url(url))}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'


def list_html(values, css=''):
    if isinstance(values, str):
        values = [values]
    return '<ul class="' + esc(css) + '">' + ''.join(f'<li>{esc(v)}</li>' for v in values or []) + '</ul>'


def source_kind(source):
    medium = source.get('medium', '').lower()
    if source.get('sourceKind') == 'vector':
        return 'Vector reference'
    if 'printed depiction' in medium:
        return 'Printed illustration'
    if 'digital' in medium:
        return 'Digital artwork'
    if source.get('page'):
        return 'Document graphic'
    if 'printed emblem' in medium:
        return 'Printed emblem'
    if 'decal' in medium:
        return 'Photographed decal'
    if 'painted' in medium:
        return 'Photographed painted emblem'
    if source.get('sourceKind') == 'photo':
        return 'Patch photograph' if 'cloth' in medium or 'patch photograph' in medium else 'Photographic reference'
    return 'Raster reference'


def dimension_text(source):
    unit = 'reference units' if source.get('sourceKind') == 'vector' else 'source pixels'
    value = f"{source['width']:g} × {source['height']:g} {unit}"
    display = source.get('displayPixels')
    if display and list(display) != [source['width'], source['height']]:
        value += f" · embedded at {display[0]} × {display[1]} px"
    if source.get('page'):
        value += f" · page {source['page']}"
    return value


class Assets:
    """A single data URL per unique image, referenced by accessible SVG uses."""
    def __init__(self):
        self.by_hash = {}

    def add(self, data, expected=None):
        digest = sha(data)
        if expected and digest != expected:
            raise ValueError(f'Image bytes do not match the evidence hash: {digest} != {expected}')
        if digest not in self.by_hash:
            with Image.open(io.BytesIO(data)) as im:
                width, height = im.size
                mime = Image.MIME[im.format]
            self.by_hash[digest] = {
                'id': 'asset-' + digest[:24], 'width': width, 'height': height,
                'uri': f'data:{mime};base64,' + base64.b64encode(data).decode('ascii'),
            }
        return self.by_hash[digest]

    def defs(self):
        symbols = []
        for asset in self.by_hash.values():
            symbols.append(
                f'<symbol id="{asset["id"]}" viewBox="0 0 {asset["width"]} {asset["height"]}">'
                f'<image width="{asset["width"]}" height="{asset["height"]}" href="{asset["uri"]}" preserveAspectRatio="xMidYMid meet"/></symbol>'
            )
        return '<svg xmlns="http://www.w3.org/2000/svg" aria-hidden="true" width="0" height="0" class="asset-definitions"><defs>' + ''.join(symbols) + '</defs></svg>'


def art(asset, label, css=''):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="art {esc(css)}" viewBox="0 0 {asset["width"]} {asset["height"]}" '
        f'preserveAspectRatio="xMidYMid meet" role="img" aria-label="{esc(label)}">'
        f'<title>{esc(label)}</title><use href="#{asset["id"]}"/></svg>'
    )


CSS = r'''
:root{color-scheme:light;--paper:#f6f3eb;--surface:#fffdf8;--ink:#183044;--muted:#5e6c73;--line:#d7d9d2;--gold:#ad8136;--gold-pale:#f1e7cf;--blue-pale:#e9f0f3;--red:#8a3e35;--green:#386654;--radius:16px}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:120px}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}a{color:inherit;text-underline-offset:3px;text-decoration-thickness:1px}a:hover{color:#6e4c16}button,input,select{font:inherit}button,select{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid #b88a39;outline-offset:4px}button{color:inherit}.wrap{width:min(1400px,calc(100% - 64px));margin:auto}.masthead{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:22px 0;border-bottom:1px solid var(--line);font-size:12px;letter-spacing:.12em;text-transform:uppercase}.brand{display:flex;align-items:center;gap:10px;font-weight:750}.brand-mark{display:inline-grid;place-items:center;width:28px;height:28px;border:1px solid var(--gold);border-radius:50%;color:var(--gold);font-size:18px}.masthead a{letter-spacing:.02em;text-transform:none}.hero{padding:68px 0 40px;display:grid;grid-template-columns:minmax(0,1.4fr) minmax(280px,.7fr);gap:60px;align-items:end}.eyebrow{font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:#866326;margin:0 0 16px}h1{font-family:Georgia,"Times New Roman",serif;font-weight:500;font-size:clamp(40px,5.5vw,72px);line-height:1.06;letter-spacing:-.045em;max-width:900px;margin:0 0 24px}h2{font-size:27px;line-height:1.25;letter-spacing:-.025em;margin:0 0 16px}h3{font-size:19px;line-height:1.35;margin:0 0 10px}h4{font-size:13px;text-transform:uppercase;letter-spacing:.08em;margin:0 0 9px}.hero-lede{font-size:19px;line-height:1.6;max-width:780px;margin:0}.hero-note{border-left:2px solid var(--gold);padding-left:22px;color:var(--muted);font-size:14px}.hero-note strong{color:var(--ink)}.hero-note p{margin:0 0 14px}.hero-note p:last-child{margin:0}.stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:26px 0;margin:0 0 44px}.stat{padding:0 28px;border-left:1px solid var(--line)}.stat:first-child{padding-left:0;border-left:0}.stat-number{display:block;font-family:Georgia,serif;font-size:44px;line-height:1.1;letter-spacing:-.035em}.stat-label{display:block;margin-top:8px;font-size:13px;color:var(--muted);line-height:1.4}.overview{display:grid;grid-template-columns:1.45fr 1fr;gap:48px;margin-bottom:48px}.finding{padding:17px 0;border-top:1px solid var(--line)}.finding h3{font-size:17px;margin-bottom:7px}.finding p{font-size:14px;color:var(--muted);margin:0}.finding a{color:var(--ink)}.status-table{width:100%;border-collapse:collapse;font-size:13px}.status-table td,.status-table th{padding:13px 0;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}.status-table th{font-weight:650}.status-table .count{width:36px;text-align:right;font-size:20px;font-variant-numeric:tabular-nums}.status-definition{display:block;color:var(--muted);font-weight:400;margin-top:4px}.candidate-overview{padding:24px 28px;border:1px solid #c8d4cc;background:#eff4ef;border-radius:var(--radius);margin-bottom:44px}.candidate-overview p{font-size:14px;color:var(--muted);margin:0 0 14px}.candidate-links{display:flex;flex-wrap:wrap;gap:8px}.candidate-links a{font-size:12px;font-weight:650;border:1px solid #b8cabd;padding:6px 10px;border-radius:6px;background:#f8fbf6;text-decoration:none}.method{padding:24px 0;border-top:1px solid var(--line);margin-bottom:26px}.method-grid{display:grid;grid-template-columns:1.5fr 1fr;gap:40px}.method p{font-size:14px;color:var(--muted);margin:0 0 12px}.method details{font-size:13px;color:var(--muted)}summary{cursor:pointer;color:var(--ink);font-weight:650}.provenance-list{padding-left:18px}.provenance-list li{margin:7px 0}.digest{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:11px;overflow-wrap:anywhere;color:var(--muted)}.collection-heading{display:flex;align-items:baseline;justify-content:space-between;gap:18px;padding-top:30px}.collection-heading p{font-size:13px;color:var(--muted);margin:0}.filters{position:sticky;top:0;z-index:5;display:grid;grid-template-columns:minmax(200px,1.6fr) minmax(180px,1fr) minmax(170px,.8fr) auto;align-items:end;gap:12px;padding:17px 20px;margin:12px -20px 16px;background:rgba(246,243,235,.97);border-bottom:1px solid var(--line);backdrop-filter:blur(8px)}.filters label{display:grid;gap:5px;font-size:11px;font-weight:650;text-transform:uppercase;letter-spacing:.08em}.filters input,.filters select{width:100%;height:44px;border:1px solid #c5cbc8;background:var(--surface);border-radius:7px;padding:8px 10px;color:var(--ink);font-size:13px;letter-spacing:normal;text-transform:none}.filters button{height:44px;border:1px solid #c5cbc8;border-radius:7px;background:transparent;padding:8px 15px;font-size:13px}.js-only{display:none}.has-js .js-only{display:grid}.results-line{font-size:12px;color:var(--muted);margin-bottom:25px}.empty-results{padding:50px 20px;text-align:center;border:1px dashed var(--line);border-radius:var(--radius)}[hidden]{display:none!important}.patch-entry{margin:0 0 32px;background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;scroll-margin-top:115px}.entry-header{padding:23px 26px 21px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;border-bottom:1px solid var(--line)}.entry-meta{display:flex;flex-wrap:wrap;gap:7px 12px;align-items:center;font-size:12px;color:var(--muted);margin-bottom:8px}.entry-id{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-weight:650;color:var(--ink)}.entry-header h3{font-size:21px;line-height:1.35;max-width:1000px;letter-spacing:-.015em;margin:0}.entry-state{display:flex;align-items:flex-start;justify-content:flex-end;gap:8px;flex-wrap:wrap;max-width:260px}.status-badge,.priority-badge,.candidate-badge{font-size:11px;font-weight:700;line-height:1.4;padding:5px 9px;border:1px solid var(--line);border-radius:6px;background:#f1f2ef}.status-reconstruct{color:var(--red);background:#f6ebe5;border-color:#ddc5bd}.status-refine{color:#785621;background:#f5eddb;border-color:#ddd0ad}.status-retain{color:var(--green);background:#edf3ec;border-color:#c8d7c9}.status-source-limited{color:#526778;background:#edf1f3;border-color:#ced8de}.status-interpretation{color:#735e7b;background:#f0ecf3;border-color:#d8ccdd}.priority-badge{border:0;background:transparent;color:var(--muted);font-weight:500}.candidate-badge{color:var(--green);border-color:#c8d7c9;background:#edf3ec}.comparisons{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:1px;background:var(--line)}.comparisons.with-candidate{grid-template-columns:repeat(3,minmax(0,1fr))}.comparison{margin:0;padding:17px 20px 20px;background:#f4f5f1;min-width:0;display:flex;flex-direction:column}.comparison.source-panel{background:#f1f0e9}.comparison.candidate-panel{background:#f1f5ee}.comparison-title{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px;min-height:25px;font-size:11px;text-transform:uppercase;letter-spacing:.09em;font-weight:750;color:#53616a}.comparison-title .revision{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:10px;text-transform:none;letter-spacing:0;color:var(--muted);font-weight:450}.art{display:block;width:100%;height:300px;flex:0 0 300px;overflow:visible}.art>use{pointer-events:none}.art-empty{display:flex;align-items:center;justify-content:center;width:100%;height:300px;padding:28px;border:1px dashed #c8cec9;border-radius:8px;text-align:center;color:var(--muted);font-size:14px;background:rgba(255,255,255,.4)}.comparison figcaption{font-size:12px;line-height:1.6;color:var(--muted);margin-top:15px}.comparison figcaption p{margin:6px 0}.comparison .source-line{color:var(--ink);font-weight:650}.source-selector{margin:0 0 12px;display:grid;gap:5px;font-size:11px;color:var(--muted)}.source-selector select{width:100%;max-width:100%;border:1px solid #c6cec8;border-radius:6px;background:var(--surface);padding:6px 8px;color:var(--ink);font:12px/1.3 system-ui}.source-note{font-size:11px}.source-link{font-size:12px;font-weight:600}.source-note:empty{display:none}.drawing-note{margin:12px 0 0;font-size:11px;line-height:1.55;color:var(--muted)}.entry-review{padding:25px 27px;display:grid;grid-template-columns:1.35fr 1fr;gap:32px}.entry-review ul{padding-left:18px;margin:0;font-size:14px;color:#3e515c}.entry-review li{margin-bottom:8px}.entry-review li:last-child{margin-bottom:0}.entry-review .next-step{font-size:13px;color:var(--muted)}.entry-review .next-step ul{font-size:13px;color:var(--muted)}.candidate-changes{padding:16px 18px;background:#eff4ef;border-left:3px solid #6d9478;margin-top:18px;border-radius:0 7px 7px 0}.candidate-changes h4{color:var(--green);font-size:11px}.candidate-changes ul{font-size:13px}.entry-footer{border-top:1px solid var(--line);padding:16px 27px;font-size:12px;color:var(--muted)}.entry-footer details+details{margin-top:11px}.entry-footer p{margin:8px 0 0}.source-gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(205px,1fr));gap:14px;margin-top:15px}.source-thumbnail{padding:13px;background:#f4f4ee;border:1px solid var(--line);border-radius:8px;min-width:0}.source-thumbnail .art{height:175px;flex-basis:175px}.source-thumbnail p{font-size:11px;margin:8px 0 0}.source-thumbnail .source-line{color:var(--ink);font-weight:650}.unavailable-list{padding-left:18px;font-size:12px}.entry-links{display:flex;gap:15px;flex-wrap:wrap;margin-top:12px}.asset-definitions{position:absolute;overflow:hidden}.end-note{padding:45px 0 60px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}.end-note p{max-width:950px}.end-note strong{color:var(--ink)}.no-script{padding:12px 16px;background:var(--gold-pale);border-radius:8px;font-size:13px;margin:15px 0}.muted{color:var(--muted)}
@media(min-width:1450px){.art,.art-empty{height:345px;flex-basis:345px}}
@media(max-width:1000px){.wrap{width:calc(100% - 40px)}.hero{grid-template-columns:1fr;gap:28px;padding-top:44px}.hero-note{max-width:760px}.overview{grid-template-columns:1fr;gap:30px}.entry-header{grid-template-columns:1fr;gap:12px}.entry-state{justify-content:flex-start;max-width:none}.entry-review{grid-template-columns:1fr;gap:23px}.filters{grid-template-columns:1fr 1fr}.filters label:first-child{grid-column:1/-1}.filters button{align-self:end}.comparisons.with-candidate{grid-template-columns:repeat(2,minmax(0,1fr))}.candidate-panel{grid-column:1/-1}.candidate-panel .art{height:300px}.method-grid{grid-template-columns:1fr;gap:16px}html{scroll-padding-top:180px}.patch-entry{scroll-margin-top:190px}}
@media(max-width:640px){.wrap{width:calc(100% - 28px)}.masthead{font-size:10px;gap:12px}.masthead>a{display:none}.hero{padding-top:35px}.hero-lede{font-size:17px}.stats{grid-template-columns:1fr 1fr;gap:24px 0}.stat{padding:0 18px}.stat:nth-child(3){border-left:0;padding-left:0}.stat-number{font-size:36px}.overview{margin-bottom:30px}.filters{position:static;margin-inline:0;padding:14px 0;grid-template-columns:1fr}.filters label:first-child{grid-column:auto}.collection-heading{display:block}.collection-heading p{margin-top:5px}.comparisons,.comparisons.with-candidate{grid-template-columns:1fr}.candidate-panel{grid-column:auto}.entry-header{padding:19px}.entry-header h3{font-size:19px}.entry-review{padding:21px 19px}.entry-footer{padding:16px 19px}.comparison{padding:16px 18px}.candidate-overview{padding:20px}.source-gallery{grid-template-columns:1fr}.art,.art-empty{height:300px;flex-basis:300px}.patch-entry{scroll-margin-top:16px}html{scroll-padding-top:16px}.hero-note{font-size:13px}}
@media print{body{background:white;font-size:11px}.wrap{width:100%}.masthead,.filters,.js-only,.source-selector{display:none!important}.hero{padding-top:15px}.hero h1{font-size:37px}.stats{padding:15px 0;margin-bottom:20px}.stat-number{font-size:28px}.overview{gap:22px}.patch-entry{break-inside:avoid;border-radius:0;margin-bottom:18px}.entry-header{padding:12px 15px}.entry-header h3{font-size:16px}.entry-review{padding:15px;gap:20px}.entry-review ul,.entry-review .next-step ul{font-size:11px}.art,.art-empty{height:190px;flex-basis:190px}.comparison{padding:12px}.comparison figcaption{font-size:10px}.entry-footer{padding:10px 15px}.end-note{padding:20px 0}a{text-decoration:none}.candidate-panel{grid-column:auto}.comparisons.with-candidate{grid-template-columns:repeat(3,minmax(0,1fr))}}
'''


JS = r'''
(() => {
  const data = JSON.parse(document.getElementById('review-data').textContent);
  const rows = [...document.querySelectorAll('.patch-entry')];
  const search = document.getElementById('filter-search');
  const org = document.getElementById('filter-org');
  const status = document.getElementById('filter-status');
  const count = document.getElementById('result-count');
  const empty = document.getElementById('empty-results');
  function filter() {
    const words = search.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const row of rows) {
      const meta = data[row.dataset.id];
      const match = (!org.value || row.dataset.org === org.value) &&
        (!status.value || row.dataset.status === status.value) &&
        words.every(word => meta.search.includes(word));
      row.hidden = !match;
      if (match) visible++;
    }
    count.textContent = `Showing ${visible} of ${rows.length} variants`;
    empty.hidden = visible !== 0;
  }
  search.addEventListener('input', filter);
  org.addEventListener('change', filter);
  status.addEventListener('change', filter);
  document.getElementById('clear-filters').addEventListener('click', () => {
    search.value = ''; org.value = ''; status.value = ''; filter(); search.focus();
  });
  for (const selector of document.querySelectorAll('.source-selector select')) {
    selector.addEventListener('change', () => {
      const row = selector.closest('.patch-entry');
      const source = data[row.dataset.id].sources[Number(selector.value)];
      const panel = row.querySelector('.source-panel');
      const graphic = panel.querySelector('.source-art');
      graphic.setAttribute('viewBox', `0 0 ${source.asset.width} ${source.asset.height}`);
      graphic.querySelector('use').setAttribute('href', '#' + source.asset.id);
      const label = `${data[row.dataset.id].label}, source occurrence ${source.occurrenceId}`;
      graphic.setAttribute('aria-label', label);
      graphic.querySelector('title').textContent = label;
      panel.querySelector('.selected-source-id').textContent = `${source.occurrenceId} · ${source.kind}`;
      panel.querySelector('.selected-source-size').textContent = source.dimensions;
      panel.querySelector('.selected-source-note').textContent = source.note || '';
      const sourceLink = panel.querySelector('.selected-source-link');
      if (source.url) {
        sourceLink.href = source.url; sourceLink.hidden = false;
      } else {
        sourceLink.removeAttribute('href'); sourceLink.hidden = true;
      }
    });
  }
  for (const anchor of document.querySelectorAll('a[href^="#patch-"]')) {
    anchor.addEventListener('click', () => {
      const target = document.getElementById(anchor.getAttribute('href').slice(1));
      if (target && target.hidden) { search.value = ''; org.value = ''; status.value = ''; filter(); }
    });
  }
  document.documentElement.classList.add('has-js');
  filter();
})();
'''


def build(args):
    if not args.output.is_absolute():
        raise ValueError('--output must be an absolute file path.')
    index = read_json(args.index)
    if index.get('version') != 1 or not isinstance(index.get('patches'), list):
        raise ValueError('Expected version 1 of the patch review index.')
    entries = index['patches']
    if len({p['id'] for p in entries}) != len(entries):
        raise ValueError('Duplicate patch IDs in the index.')
    if any(p['status'] not in STATUS_LABELS for p in entries):
        raise ValueError('Every report entry must have an explicit supported review status.')
    patcher = args.patcher.resolve()
    baseline_ref = index['baseline']['patcher']
    baseline_manifest = json.loads(git_bytes(patcher, baseline_ref, 'library/manifest.json'))
    current_manifest = read_json(patcher / 'library/manifest.json')
    old = {p['id']: p for o in baseline_manifest['orgs'] for p in o['patches']}
    current = {p['id']: p for o in current_manifest['orgs'] for p in o['patches']}
    assets = Assets()
    metadata = {}
    articles = []
    source_ids = set()
    candidate_count = 0
    by_status = Counter(p['status'] for p in entries)
    organizations = {p['orgId']: p['orgName'] for p in entries}
    card_ids = {p.get('group') or p['id'] for p in entries}
    review_date = date.fromisoformat(index['reviewedAt'])
    for row in entries:
        patch_id = row['id']
        baseline_patch = old[patch_id]
        baseline_hash = row.get('baselineSvgSha256') or row['reviewedSvgSha256']
        if baseline_patch['sha256'] != baseline_hash:
            raise ValueError(f'{patch_id}: baseline SVG hash does not match the pinned manifest.')
        baseline_preview = assets.add(git_bytes(patcher, baseline_ref, 'library/' + baseline_patch['preview']))
        candidate = None
        if row.get('candidateChanges'):
            candidate_count += 1
            candidate_patch = current[patch_id]
            if candidate_patch['sha256'] != row['currentSvgSha256'] or row['reviewedSvgSha256'] != row['currentSvgSha256']:
                raise ValueError(f'{patch_id}: candidate drawing has changed since the recorded review.')
            candidate = assets.add(child(patcher / 'library', candidate_patch['preview']).read_bytes())
        sources = []
        for source in row['sources']:
            data = child(ROOT / 'public', source['cropUrl']).read_bytes()
            asset = assets.add(data, source['cropSha256'])
            if [asset['width'], asset['height']] != source['displayPixels']:
                raise ValueError(f'{patch_id}/{source["occurrenceId"]}: embedded crop dimensions do not match the index.')
            safe_url(source.get('url'))
            source_ids.add(source['occurrenceId'])
            sources.append({
                **source, 'asset': {k: asset[k] for k in ('id', 'width', 'height')},
                'kind': source_kind(source), 'dimensions': dimension_text(source),
            })
        meta = {
            'label': row['label'],
            'search': ' '.join([patch_id, row['label'], row['orgName'], row.get('variant') or '', row['status'],
                                *row['findings'], *row.get('candidateChanges', [])]).lower(),
            'sources': sources,
        }
        metadata[patch_id] = meta
        status = row['status']
        state = f'<span class="status-badge status-{esc(status)}">{esc(STATUS_LABELS[status])}</span>'
        state += f'<span class="priority-badge">{esc(row["priority"].capitalize())} priority</span>'
        if candidate:
            state += '<span class="candidate-badge">Partial correction prepared</span>'
        first = sources[0] if sources else None
        selector = ''
        if len(sources) > 1:
            options = ''.join(f'<option value="{n}">{esc(s["occurrenceId"])} · {esc(s["kind"])} · {s["width"]:g} × {s["height"]:g}</option>' for n, s in enumerate(sources))
            selector = f'<label class="source-selector js-only">Source occurrence<select aria-label="Source occurrence for {esc(patch_id)}">{options}</select></label>'
        source_art = art(first['asset'], f'{row["label"]}, source occurrence {first["occurrenceId"]}', 'source-art') if first else '<div class="art-empty">No source crop is available for this variant.<br>The evidence gap remains part of this review.</div>'
        if first:
            source_caption = (
                f'<p class="source-line selected-source-id">{esc(first["occurrenceId"])} · {esc(first["kind"])}</p>'
                f'<p class="selected-source-size">{esc(first["dimensions"])}</p>'
                f'<p class="source-note selected-source-note">{esc(first.get("note", ""))}</p>'
                f'<a class="source-link selected-source-link" {"href=" + chr(34) + esc(first["url"]) + chr(34) if first.get("url") else "hidden"} target="_blank" rel="noopener noreferrer">Open full source ↗</a>'
            )
        else:
            source_caption = '<p>Generated colourways and missing references cannot be accepted as specimen matches from the drawing alone.</p>'
        source_panel = f'<figure class="comparison source-panel"><div class="comparison-title"><span>Source reference</span><span class="revision">{len(sources)} available</span></div>{selector}{source_art}<figcaption>{source_caption}</figcaption></figure>'
        baseline_panel = (
            '<figure class="comparison baseline-panel"><div class="comparison-title"><span>Baseline drawing</span>'
            f'<span class="revision">{baseline_ref[:8]}</span></div>{art(baseline_preview, row["label"] + ", baseline drawing")}'
            '<figcaption><p>Vector artwork preview from the pinned baseline. Its aspect ratio is preserved.</p>'
            f'<p class="digest">SVG SHA-256: {esc(baseline_hash)}</p></figcaption></figure>'
        )
        candidate_panel = ''
        if candidate:
            candidate_panel = (
                '<figure class="comparison candidate-panel"><div class="comparison-title"><span>Partial correction prepared</span></div>'
                f'{art(candidate, row["label"] + ", partial correction prepared")}'
                '<figcaption><p>This candidate addresses the changes listed below. The remaining review status still applies.</p>'
                f'<p class="digest">SVG SHA-256: {esc(row["currentSvgSha256"])}</p></figcaption></figure>'
            )
        changes = ''
        if candidate:
            changes = '<div class="candidate-changes"><h4>Prepared changes</h4>' + list_html(row['candidateChanges']) + '</div>'
        baseline_notes = ''
        if row.get('baselineFindings'):
            baseline_notes = '<details><summary>Original baseline findings</summary>' + list_html(row['baselineFindings']) + '</details>'
        gallery_items = []
        for source in sources:
            gallery_items.append(
                f'<div class="source-thumbnail">{art(source["asset"], row["label"] + ", " + source["occurrenceId"])}'
                f'<p class="source-line">{esc(source["occurrenceId"])} · {esc(source["kind"])}</p><p>{esc(source["dimensions"])}</p>'
                f'<p>{esc(source.get("note", ""))}</p><p>{link(source.get("url"), "Open full source ↗")}</p>'
                f'<p class="digest">Source SHA-256: {esc(source["sourceFileSha256"])}</p>'
                f'<p class="digest">Crop SHA-256: {esc(source["cropSha256"])}</p></div>'
            )
        gallery = ''
        if gallery_items:
            gallery = f'<details><summary>All {len(sources)} source occurrence{"s" if len(sources) != 1 else ""} and their provenance</summary><div class="source-gallery">' + ''.join(gallery_items) + '</div></details>'
        unavailable = ''
        if row.get('unavailableSources'):
            bits = []
            for s in row['unavailableSources']:
                page = f' · page {s["page"]}' if s.get('page') else ''
                bits.append(f'<li><strong>{esc(s["occurrenceId"])}</strong>{esc(page)} — {esc(s["reason"])}. {link(s.get("url"), "Source record ↗")}</li>')
            unavailable = '<details><summary>Linked occurrences without an available crop</summary><ul class="unavailable-list">' + ''.join(bits) + '</ul></details>'
        artwork_url = f'https://github.com/ahzs645/patcher/blob/{baseline_ref}/library/{quote(baseline_patch["svg"], safe="/")}'
        live_url = 'https://projects.ahmadjalil.com/PofBC/?view=patches&patch=' + quote(patch_id, safe='')
        articles.append(
            f'<article class="patch-entry" id="patch-{esc(patch_id)}" data-id="{esc(patch_id)}" data-org="{esc(row["orgId"])}" data-status="{esc(status)}">'
            f'<header class="entry-header"><div><div class="entry-meta"><span class="entry-id">{esc(patch_id)}</span><span>{esc(row["orgName"])}</span>'
            f'<span>{esc(row["medium"])}</span></div><h3>{esc(row["label"])}</h3></div><div class="entry-state">{state}</div></header>'
            f'<div class="comparisons{" with-candidate" if candidate else ""}">{source_panel}{baseline_panel}{candidate_panel}</div>'
            f'<div class="entry-review"><section><h4>Review findings</h4>{list_html(row["findings"])}{changes}</section>'
            f'<section class="next-step"><h4>Next refinement</h4>{list_html(row["proposedFix"])}</section></div>'
            f'<footer class="entry-footer"><details><summary>Evidence and artwork limitations</summary><p>{esc(row["evidenceLimitations"])}</p><p>{esc(row["limitations"])}</p></details>'
            f'{baseline_notes}{gallery}{unavailable}<div class="entry-links">{link(live_url, "Open gallery entry ↗")}{link(artwork_url, "Pinned baseline artwork ↗")}</div></footer></article>'
        )
    summary = index['summary']
    actual = {'variants': len(entries), 'cards': len(card_ids), 'organizations': len(organizations), 'sourceCrops': len(source_ids), 'partialRefinements': candidate_count}
    if any(summary[k] != value for k, value in actual.items()) or dict(by_status) != summary['byStatus']:
        raise ValueError(f'Report counts do not agree with the evidence index: {actual}')
    needed = by_status['refine'] + by_status['reconstruct']
    org_options = ''.join(f'<option value="{esc(k)}">{esc(v)}</option>' for k, v in sorted(organizations.items(), key=lambda item: item[1]))
    status_options = ''.join(f'<option value="{s}">{esc(STATUS_LABELS[s])} ({by_status[s]})</option>' for s in STATUS_ORDER)
    status_table = ''.join(f'<tr><th><span>{esc(STATUS_LABELS[s])}</span><span class="status-definition">{esc(index["statusDefinitions"][s])}</span></th><td class="count">{by_status[s]}</td></tr>' for s in STATUS_ORDER)
    candidate_links = ''.join(f'<a href="#patch-{esc(p["id"])}">{esc(p["id"])} · {esc(p.get("variant") or p["label"].split("—")[-1].strip())}</a>' for p in entries if p.get('candidateChanges'))
    pofbc_url = 'https://github.com/ahzs645/PofBC/tree/' + index['baseline']['pofbc']
    patcher_url = 'https://github.com/ahzs645/patcher/tree/' + baseline_ref
    data_json = json.dumps(metadata, ensure_ascii=False, separators=(',', ':')).replace('<', r'\u003c').replace('>', r'\u003e').replace('&', r'\u0026')
    document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>PofBC — Patch source review · {esc(index['reviewedAt'])}</title><style>{CSS}</style></head>
<body>{assets.defs()}<div class="wrap">
<nav class="masthead" aria-label="Report"><span class="brand"><span class="brand-mark" aria-hidden="true">✳</span>PofBC / Visual reference review</span>{link('https://projects.ahmadjalil.com/PofBC/?view=patches', 'Open the live patch gallery ↗')}</nav>
<header class="hero"><div><p class="eyebrow">{review_date.strftime('%d %B %Y')} · Full collection review</p><h1>The patch collection,<br>against its sources.</h1><p class="hero-lede"><strong>{needed} of {len(entries)} variants need refinement or reconstruction.</strong> The most useful improvements are edition-specific symbols, lettering, proportions and spacing. This report brings the evidence beside every drawing.</p></div><aside class="hero-note"><p><strong>{summary['cards']} gallery cards · {summary['organizations']} organizations</strong><br>Variant groups are expanded here so each drawing has its own review.</p><p>The photographs, printed illustrations and digital references remain distinct. Clean geometry and a convincing embroidery simulation do not establish historical fidelity.</p><p><strong>{candidate_count} partial corrections are prepared locally.</strong> Their baseline and candidate drawings appear separately; unresolved work remains visible. These candidates have not been published to the live gallery.</p></aside></header>
<section class="stats" aria-label="Review totals"><div class="stat"><span class="stat-number">{len(entries)}</span><span class="stat-label">individual variants reviewed</span></div><div class="stat"><span class="stat-number">{len(source_ids)}</span><span class="stat-label">embedded source occurrence crops</span></div><div class="stat"><span class="stat-number">{needed}</span><span class="stat-label">need refinement or reconstruction</span></div><div class="stat"><span class="stat-number">{candidate_count}</span><span class="stat-label">partial corrections prepared</span></div></section>
<section class="overview" aria-label="Main findings"><div><p class="eyebrow">What the comparisons show</p><h2>Several recurring problems deserve a shared correction pass.</h2><div class="finding"><h3>Shared artwork sometimes erases the differences between editions.</h3><p>The <a href="#patch-S56-O04">older Sheriff arms</a>, <a href="#patch-FO-yellow-sky-dark">dark Forest Service scene</a> and <a href="#patch-S29-O03">Parks hikers triangle</a> need their own component construction. A new palette alone cannot restore different silhouettes or composition.</p></div><div class="finding"><h3>Lettering changes the character of the whole patch.</h3><p>Flattened title arcs, substitute letter shapes, loose tracking and small lower captions recur across the collection. Compare the <a href="#patch-S56-O02">Sheriff title</a>, <a href="#patch-UP01-O01">Coroners lettering</a> and <a href="#patch-S56-O43">Fire Commissioner layout</a> before changing decorative detail.</p></div><div class="finding"><h3>The weakest sources need a clearer evidence label.</h3><p>Many collector-board crops are only a few dozen pixels across. The <a href="#patch-S56-O47">Traffic Officers centre</a> remains schematic. The <a href="#patch-MC03-O01">Predator Branch source is a printed illustration</a>, and its separate supplied-illustration overlap measurements do not measure historical specimen fidelity.</p></div><div class="finding"><h3>Some existing constructions should be retained.</h3><p>The <a href="#patch-S56-O38">SPCA roundel</a> already has a documented refinement against its supplied source. Native digital references support several Forest Oval editions. Generated colourways remain explicitly labelled interpretations.</p></div></div><div><p class="eyebrow">How to read the decisions</p><h2>Review status is a work decision.</h2><table class="status-table"><caption class="muted" style="text-align:left;font-size:13px;padding-bottom:10px">Counts apply to variants, including related colourways.</caption><tbody>{status_table}</tbody></table></div></section>
<section class="candidate-overview" aria-label="Prepared corrections"><h3>{candidate_count} focused corrections, with the remaining work preserved</h3><p>The candidate panels show a restored mountain-line capture, a more suitable cloth border, and three Conservation Officer divider/lettering adjustments. These are partial corrections; the affected entries retain their refinement status.</p><div class="candidate-links">{candidate_links}</div></section>
<section class="method" aria-label="Evidence method"><div class="method-grid"><div><h3>Comparison method and limits</h3><p>{esc(index['method'])}</p><p>Each image is fitted into a display box while preserving its aspect ratio. Panel size is not a physical-size comparison. The images are not registered or warped into agreement, and no numerical fidelity score is assigned.</p><p>{summary['variantsWithCrops']} variants have an available source crop. {summary['unavailableOccurrences']} linked occurrences remain unavailable or lack individual crop rectangles; they are listed with the affected entries. All {summary['sourceCrops']} crops, {summary['variants']} baseline previews and {candidate_count} candidate previews are embedded for offline reading.</p></div><div><details><summary>Source versions and reproducibility</summary><ul class="provenance-list"><li>{link(pofbc_url, 'PofBC baseline ' + index['baseline']['pofbc'][:8])}</li><li>{link(patcher_url, 'Patcher artwork baseline ' + baseline_ref[:8])}</li><li>{link(ATLAS_URL, 'BC Forestry Patch Atlas source archive')}<p class="digest">Snapshot SHA-256: {esc(index['baseline']['atlasSnapshotSha256'])}</p><p class="digest">Archive SHA-256: {esc(index['baseline'].get('atlasArchiveSha256', 'not recorded'))}</p></li></ul><p>Source and crop hashes are retained in each entry. Baseline previews are read directly from the pinned Git commit. Candidate previews are checked against the current manifest and reviewed drawing hash.</p></details><p style="margin-top:14px">External links are intentional references. The report itself makes no network requests and can be read without JavaScript.</p></div></div></section>
<section aria-labelledby="collection-title"><div class="collection-heading"><h2 id="collection-title">Every variant, with its evidence</h2><p>Source · baseline drawing · prepared candidate where available</p></div><noscript><p class="no-script">All entries are shown. Expand “All source occurrences and their provenance” within any entry to view its alternate references. Search and filters are available when JavaScript is enabled.</p></noscript><div class="filters js-only"><label>Search<input id="filter-search" type="search" placeholder="Patch ID, organization, lettering, scene…" autocomplete="off"></label><label>Organization<select id="filter-org"><option value="">All {len(organizations)} organizations</option>{org_options}</select></label><label>Review status<select id="filter-status"><option value="">All statuses</option>{status_options}</select></label><button id="clear-filters" type="button">Clear filters</button></div><p class="results-line" id="result-count" role="status" aria-live="polite">Showing {len(entries)} of {len(entries)} variants</p><p class="empty-results" id="empty-results" hidden>No variants match these filters.</p>{''.join(articles)}</section>
<footer class="end-note"><h3>What this review establishes</h3><p>It identifies specific visual work against the retained references and makes the source gaps inspectable. <strong>It does not authenticate issue dates, exact historical typefaces, calibrated thread colours, physical dimensions or original manufacturing artwork.</strong> A redesigned interpretation can be developed separately while preserving the specimen-based reconstruction and its evidence.</p><p><strong>Implementation validation:</strong> the patch-focused Vite production bundle passed with 454 emitted assets using the candidate Patcher dependency. Source/crop hashes, dimensions and review coverage were checked. Interactive browser acceptance has not been completed. The corrections and viewer work are prepared locally; this report does not represent a published pull request or a live deployment.</p><p>Prepared {review_date.strftime('%d %B %Y')} · {len(entries)} variants · {len(source_ids)} source crops · {candidate_count} partial corrections. Images remain embedded in this file; source links lead to their recorded locations.</p></footer>
</div><script type="application/json" id="review-data">{data_json}</script><script>{JS}</script></body></html>'''
    encoded = document.encode('utf-8')
    if len(encoded) >= 50 * 1024 * 1024:
        raise ValueError(f'Report exceeds the 50 MiB limit: {len(encoded)} bytes.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(encoded)
    print(json.dumps({
        'output': str(args.output), 'bytes': len(encoded), 'uniqueEmbeddedImages': len(assets.by_hash),
        'sourceCrops': len(source_ids), 'baselinePreviews': len(entries), 'candidatePreviews': candidate_count,
        'variants': len(entries), 'cards': len(card_ids), 'organizations': len(organizations), 'byStatus': dict(by_status),
    }, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, default=ROOT / 'public/patch-review/index.json')
    parser.add_argument('--patcher', type=Path, default=ROOT / 'vendor/patcher')
    parser.add_argument('--output', type=Path, required=True)
    build(parser.parse_args())
