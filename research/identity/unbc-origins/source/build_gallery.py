#!/usr/bin/env python3
"""Build the self-contained offline SVG catalog. Python standard library only."""
from pathlib import Path
from xml.etree import ElementTree as ET
import json

ROOT = Path(__file__).resolve().parents[1]
NS = '{http://www.w3.org/2000/svg}'

def classify(name):
    if 'interpretive' in name:
        return 'Interpretive artwork', 'Interpretive', 'interpretive'
    if 'reference-' in name:
        return 'Reference alternatives', 'Reference alternative', 'reference'
    if name.startswith('ius-pin') or name == 'ius-enamel-pin.svg':
        kind = 'Component' if name == 'ius-pin-body.svg' else ('Reproduction variant' if 'one-colour' in name else 'Reconstruction')
        return 'Pin artwork', kind, 'standard'
    if any(x in name for x in ['letterhead', 'invitation', 'fundraising-letter', 'membership-card', 'supporter-card', 'supporter-petition']):
        kind = 'Retypeset study' if 'retypeset' in name else ('Source-derived template' if 'template' in name else 'Reconstructed form')
        return 'Stationery and forms', kind, 'standard'
    if name.startswith('ius-print') or name == 'ius-three-bars.svg':
        kind = 'Component' if 'three-bars' in name else ('Reproduction variant' if any(x in name for x in ['black', 'white', 'reversed']) else 'Reconstruction')
        return 'Core identity', kind, 'standard'
    kind = 'Lettering component' if any(x in name for x in ['wording', 'prince-george']) else 'Reconstruction'
    return 'Campaign pieces', kind, 'standard'

assets = []
for path in sorted((ROOT / 'svg').glob('*.svg')):
    content = path.read_text(encoding='utf-8')
    tree = ET.fromstring(content)
    title_node, desc_node = tree.find(NS+'title'), tree.find(NS+'desc')
    title = ''.join(title_node.itertext()).strip() if title_node is not None else path.stem.replace('-', ' ')
    desc = ''.join(desc_node.itertext()).strip() if desc_node is not None else 'Reconstructed vector artwork.'
    category, label, status = classify(path.name)
    assets.append(dict(file=path.name, title=title, description=desc, category=category, label=label, status=status, svg=content, dark=path.name=='ius-print-white.svg'))
order = ['Core identity', 'Pin artwork', 'Campaign pieces', 'Stationery and forms', 'Interpretive artwork', 'Reference alternatives']
assets.sort(key=lambda a: (order.index(a['category']), 0 if a['file']=='ius-print-colour.svg' else 1, a['file']))
# Escape script delimiters and Unicode separators before embedding JSON in HTML.
payload = json.dumps(assets, ensure_ascii=False).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
html = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<title>Interior University Society — Vector catalog</title>
<style>
:root{--paper:#f5f1e7;--ink:#1d1d1b;--orange:#cd783d;--rule:#d9d3c6;--muted:#65635b;--white:#fff;--radius:5px}
*{box-sizing:border-box}body{margin:0;color:var(--ink);background:var(--paper);font-family:Arial,Helvetica,sans-serif;line-height:1.5}button,input,select{font:inherit}button,select{cursor:pointer}button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid var(--orange);outline-offset:3px}button{touch-action:manipulation}main{max-width:1480px;margin:auto;padding:34px 32px 44px}header{border-top:7px solid var(--orange);border-bottom:1px solid var(--ink);padding:27px 0 28px;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px}.eyebrow{font-size:11px;letter-spacing:.16em;font-weight:700;text-transform:uppercase;margin:0 0 13px}h1{font-size:clamp(30px,4.8vw,58px);line-height:1.03;letter-spacing:-.045em;max-width:820px;margin:0 0 17px;font-weight:800}header p{max-width:790px;margin:0;color:var(--muted);font-size:15px}.count{border-left:1px solid var(--rule);padding-left:28px;align-self:center;text-align:right;min-width:130px}.count b{display:block;font-size:64px;line-height:1;font-weight:800;letter-spacing:-.06em}.count span{display:block;margin-top:6px;font-size:11px;letter-spacing:.1em;text-transform:uppercase}.intro{display:flex;align-items:flex-start;gap:12px;margin:22px 0 24px;max-width:1000px;font-size:13px;color:var(--muted)}.intro-mark{flex:0 0 26px;width:26px;height:4px;background:var(--orange);margin-top:8px}.toolbar{display:grid;grid-template-columns:minmax(230px,1fr) 240px auto;gap:12px;align-items:end;padding:0 0 24px;border-bottom:1px solid var(--rule)}label,.control-label{display:block;font-size:10px;text-transform:uppercase;letter-spacing:.12em;font-weight:700;margin-bottom:7px}input,select{width:100%;min-height:44px;background:#fffdf8;border:1px solid #c5c0b4;border-radius:var(--radius);padding:10px 12px;color:var(--ink)}input::placeholder{color:#827e74}.backgrounds{display:flex;gap:0;border:1px solid #c5c0b4;border-radius:var(--radius);overflow:hidden}.backgrounds button{min-height:44px;min-width:54px;padding:9px 13px;background:#fffdf8;border:0;border-right:1px solid #c5c0b4;color:var(--ink);font-size:12px}.backgrounds button:last-child{border-right:0}.backgrounds button[aria-pressed="true"]{background:var(--ink);color:#fff}.results-bar{display:flex;justify-content:space-between;align-items:center;gap:15px;margin:24px 0 17px;font-size:12px;color:var(--muted)}.results-bar p{margin:0}.results-bar span{font-size:11px}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.card{min-width:0;background:#fffdf8;border:1px solid var(--rule);border-radius:var(--radius);overflow:hidden;display:flex;flex-direction:column}.stage{display:flex;align-items:center;justify-content:center;min-width:0;width:100%;height:265px;padding:28px;background:#f3efe4;border:0;border-bottom:1px solid var(--rule);position:relative}.stage:hover::after{content:"View vector";position:absolute;right:12px;bottom:12px;background:var(--ink);color:#fff;font-size:11px;padding:6px 10px;border-radius:3px}.stage img{display:block;width:100%;height:100%;object-fit:contain}.bg-light{background:#fff}.bg-paper{background:#f3efe4}.bg-dark{background:#252521}.card-copy{padding:19px 19px 16px;display:flex;flex-direction:column;flex:1}.tag{align-self:flex-start;padding:3px 7px;border:1px solid #d8d3c8;font-size:9px;letter-spacing:.07em;text-transform:uppercase;font-weight:700;line-height:1.5}.tag.interpretive{color:#713d49;border-color:#d8bec3;background:#f5eaed}.tag.reference{color:#735126;border-color:#dbc8ac;background:#f7efe1}h2{font-size:17px;line-height:1.25;letter-spacing:-.02em;margin:12px 0 7px;font-weight:700}.filename{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere;font-size:10px;color:var(--muted);margin:0 0 15px}.actions{display:flex;gap:8px;margin-top:auto}.action{background:transparent;border:1px solid #bcb6a9;border-radius:3px;min-height:37px;padding:8px 11px;color:var(--ink);font-size:12px}.action.primary{background:var(--ink);color:#fff;border-color:var(--ink)}.action:hover{border-color:var(--orange);box-shadow:inset 0 0 0 1px var(--orange)}.empty{grid-column:1/-1;padding:70px 15px;text-align:center;border:1px dashed #c9c2b4;color:var(--muted)}footer{margin-top:35px;padding-top:20px;border-top:1px solid var(--ink);display:flex;justify-content:space-between;gap:20px;color:var(--muted);font-size:11px}footer p{margin:0}dialog{width:min(1100px,calc(100vw - 28px));max-height:calc(100dvh - 28px);padding:0;border:1px solid #b8b0a0;border-radius:6px;background:var(--paper);color:var(--ink);box-shadow:0 20px 90px #0005}dialog::backdrop{background:#111c}.dialog-head{display:flex;gap:18px;align-items:flex-start;justify-content:space-between;padding:20px 24px;border-bottom:1px solid var(--rule)}.dialog-head h2{margin:0 0 4px;font-size:20px}.dialog-head .filename{margin:0}.close{width:37px;height:37px;border:1px solid #aaa293;background:transparent;border-radius:50%;font-size:22px;line-height:1;flex:0 0 auto}.large-stage{height:min(56vh,620px);padding:32px;display:flex;align-items:center;justify-content:center}.large-stage img{width:100%;height:100%;object-fit:contain}.dialog-bottom{padding:20px 24px 24px;border-top:1px solid var(--rule);display:grid;grid-template-columns:1fr auto;gap:20px;align-items:start}.dialog-bottom p{margin:10px 0 0;font-size:13px;line-height:1.6;color:#53524b;max-width:780px}.dialog-bottom .action{white-space:nowrap}.dialog-bottom small{display:block;font-size:10px;color:var(--muted);margin-top:8px}.visually-hidden{position:absolute;clip:rect(0 0 0 0);clip-path:inset(50%);width:1px;height:1px;overflow:hidden;white-space:nowrap}
@media(min-width:1300px){.stage{height:290px}}@media(max-width:1000px){.toolbar{grid-template-columns:1fr 230px}.preview-control{grid-column:1/-1}.backgrounds{display:inline-flex}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}.stage{height:280px}}@media(max-width:620px){main{padding:18px 16px 30px}header{grid-template-columns:1fr;gap:12px;padding:22px 0}.count{display:none}h1{font-size:39px}.eyebrow{font-size:9px}.intro{font-size:12px;margin:18px 0}.toolbar{grid-template-columns:1fr;gap:14px}.preview-control{grid-column:auto}.backgrounds{display:flex}.backgrounds button{flex:1}.grid{grid-template-columns:1fr;gap:18px}.stage{height:280px}.card-copy{padding:17px}.results-bar span{display:none}footer{display:block}footer p+p{margin-top:8px}.dialog-head{padding:16px}.dialog-head h2{font-size:17px}.large-stage{height:45vh;padding:20px}.dialog-bottom{padding:16px;grid-template-columns:1fr;gap:15px}.dialog-bottom .action{width:100%}.dialog-bottom p{font-size:12px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
</style>
</head>
<body>
<main>
<header><div><p class="eyebrow">Historical identity / Vector catalog</p><h1>Interior University Society</h1><p>Rebuilt marks, campaign pieces and stationery from the supplied photographs and reconstruction references.</p></div><div class="count"><b id="total-count">26</b><span>Vector assets</span></div></header>
<div class="intro"><span class="intro-mark" aria-hidden="true"></span><div>Font choices have been reviewed against the original photographs. Exact historical typefaces, colours and physical dimensions remain unconfirmed. Interpretive artwork and reference alternatives are labelled. Each download is editable SVG artwork; the guide contains the detailed reconstruction notes.</div></div>
<section class="toolbar" aria-label="Catalog controls">
<div><label for="search">Find an asset</label><input id="search" type="search" placeholder="Search marks, buttons, forms…" autocomplete="off"></div>
<div><label for="category">Collection</label><select id="category"><option value="all">All collections</option></select></div>
<div class="preview-control"><span id="background-label" class="control-label">Preview background</span><div class="backgrounds" role="group" aria-labelledby="background-label"><button type="button" data-background="auto" aria-pressed="true">Auto</button><button type="button" data-background="light" aria-pressed="false">Light</button><button type="button" data-background="paper" aria-pressed="false">Paper</button><button type="button" data-background="dark" aria-pressed="false">Dark</button></div></div>
</section>
<div class="results-bar"><p id="results-status" role="status" aria-live="polite"></p><span>Scalable artwork · Outlined lettering · Offline access</span></div>
<section id="catalog" class="grid" aria-label="Vector assets"></section>
<footer><p>Historical reconstruction. These files are not an original standards manual.</p><p>All artwork and SVG downloads are included here. No connection required.</p></footer>
</main>
<dialog id="preview" aria-labelledby="preview-title"><div class="dialog-head"><div><h2 id="preview-title"></h2><p id="preview-file" class="filename"></p></div><button type="button" class="close" id="close-preview" aria-label="Close preview">×</button></div><div id="large-stage" class="large-stage"><img id="large-image" alt=""></div><div class="dialog-bottom"><div><span id="preview-tag" class="tag"></span><p id="preview-description"></p><small>Preview background is not added to the downloaded artwork.</small></div><button type="button" id="download-preview" class="action primary">Download SVG</button></div></dialog>
<script>
'use strict';
const ASSETS = __ASSET_JSON__;
const catalog = document.getElementById('catalog');
const search = document.getElementById('search');
const category = document.getElementById('category');
const modal = document.getElementById('preview');
const status = document.getElementById('results-status');
let background = 'auto';
let activeIndex = -1;
let lastFocus = null;
const urls = ASSETS.map(asset => 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(asset.svg));
const categories = [...new Set(ASSETS.map(asset => asset.category))];
for (const name of categories) { const option = document.createElement('option'); option.value = name; option.textContent = name; category.append(option); }
document.getElementById('total-count').textContent = String(ASSETS.length);
function element(name, className, content) { const node = document.createElement(name); if (className) node.className = className; if (content !== undefined) node.textContent = content; return node; }
function chosenBackground(asset) { return background === 'auto' ? (asset.dark ? 'dark' : 'paper') : background; }
function render() {
  const term = search.value.trim().toLocaleLowerCase();
  const fragment = document.createDocumentFragment();
  let count = 0;
  ASSETS.forEach((asset, index) => {
    if (category.value !== 'all' && asset.category !== category.value) return;
    if (term && ![asset.title, asset.file, asset.description, asset.category, asset.label].join(' ').toLocaleLowerCase().includes(term)) return;
    count++;
    const card = element('article', 'card');
    const stage = element('button', 'stage bg-' + chosenBackground(asset));
    stage.type = 'button'; stage.dataset.action = 'view'; stage.dataset.index = String(index); stage.setAttribute('aria-label', 'Preview ' + asset.title);
    const image = element('img'); image.src = urls[index]; image.alt = asset.title; image.loading = 'lazy'; image.decoding = 'async'; stage.append(image);
    const copy = element('div', 'card-copy');
    copy.append(element('span', 'tag ' + asset.status, asset.label), element('h2', '', asset.title), element('p', 'filename', asset.file));
    const actions = element('div', 'actions');
    for (const [action, label, cls] of [['view', 'View details', 'action'], ['download', 'Download SVG', 'action primary']]) {
      const button = element('button', cls, label); button.type = 'button'; button.dataset.action = action; button.dataset.index = String(index); button.setAttribute('aria-label', label + ': ' + asset.title); actions.append(button);
    }
    copy.append(actions); card.append(stage, copy); fragment.append(card);
  });
  if (!count) fragment.append(element('p', 'empty', 'No matching assets. Try another word or collection.'));
  catalog.replaceChildren(fragment);
  status.textContent = count === ASSETS.length ? 'Showing all ' + count + ' assets' : 'Showing ' + count + ' of ' + ASSETS.length + ' assets';
}
function download(index) {
  const asset = ASSETS[index]; if (!asset) return;
  const url = URL.createObjectURL(new Blob([asset.svg], {type: 'image/svg+xml;charset=utf-8'}));
  const link = document.createElement('a'); link.href = url; link.download = asset.file; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 2000);
}
function show(index) {
  const asset = ASSETS[index]; if (!asset) return;
  activeIndex = index; lastFocus = document.activeElement;
  document.getElementById('preview-title').textContent = asset.title;
  document.getElementById('preview-file').textContent = asset.file;
  const tag = document.getElementById('preview-tag'); tag.className = 'tag ' + asset.status; tag.textContent = asset.label;
  document.getElementById('preview-description').textContent = asset.description;
  const image = document.getElementById('large-image'); image.src = urls[index]; image.alt = asset.title;
  document.getElementById('large-stage').className = 'large-stage bg-' + chosenBackground(asset);
  modal.showModal(); document.getElementById('close-preview').focus();
}
function closePreview() { modal.close(); }
catalog.addEventListener('click', event => { const button = event.target.closest('button[data-action]'); if (!button) return; const index = Number(button.dataset.index); if (button.dataset.action === 'view') show(index); else download(index); });
search.addEventListener('input', render); category.addEventListener('change', render);
document.querySelector('.backgrounds').addEventListener('click', event => { const button = event.target.closest('button[data-background]'); if (!button) return; background = button.dataset.background; document.querySelectorAll('[data-background]').forEach(item => item.setAttribute('aria-pressed', String(item === button))); render(); });
document.getElementById('close-preview').addEventListener('click', closePreview);
document.getElementById('download-preview').addEventListener('click', () => download(activeIndex));
modal.addEventListener('click', event => { if (event.target === modal) { const box = modal.getBoundingClientRect(); if (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom) closePreview(); } });
modal.addEventListener('close', () => { if (lastFocus && document.contains(lastFocus)) lastFocus.focus(); });
render();
</script>
</body>
</html>
'''
(ROOT / 'index.html').write_text(html.replace('__ASSET_JSON__', payload), encoding='utf-8')
print(f'Built index.html with {len(assets)} embedded SVG assets ({(ROOT / "index.html").stat().st_size:,} bytes).')
