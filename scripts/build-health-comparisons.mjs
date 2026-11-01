// Render actual checked-in geometries. No basemap, API key or external JS needed.
import { readFileSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { resolve, dirname } from 'node:path'
import { Resvg } from '@resvg/resvg-js'
import { forSphericalDrawing, prepareMap } from '../src/health/mapGeometry.js'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const directory = resolve(root, 'public/health-geography')
const read = (file) => JSON.parse(readFileSync(resolve(directory, file), 'utf8'))
const report = read('estimates-index.json')
const catalogue = read('catalogue.json')
const projection = prepareMap(read('display-ha.geojson'))
const xml = (text) => String(text).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;')
const layerNames = { lha: 'Proposed modern LHA combination', hsda: 'Closest single service delivery area', ha: 'Closest single health authority', schoolDistricts: 'Closest single school district', regionalDistricts: 'Closest single regional district', municipalities: 'Closest single municipality' }
const labels = { boards: 'Regional boards', councils: 'Councils and related labels', societies: 'Service societies' }
function drawable(feature) {
  const normalized = forSphericalDrawing({ type: 'Feature', ...feature })
  const path = projection.path(normalized)
  // V8/Node versions can differ by ~1e-12 in projected screen coordinates.
  // Stabilize display extents without changing geographic data or scores.
  const bounds = projection.path.bounds(normalized).map((point) => point.map((value) => Number(value.toFixed(6))))
  if (!path || /NaN|Infinity/.test(path) || !bounds.flat().every(Number.isFinite)) throw new Error(`Invalid drawable: ${feature.properties.code}`)
  return { code: String(feature.properties.code), name: feature.properties.name, path, bounds }
}
const source = new Map(read('source-drawn-estimates.geojson').features.map((feature) => [String(feature.properties.code), drawable(feature)]))
const current = Object.fromEntries(Object.entries({ ...read('boundary-comparison.json').datasets, ...Object.fromEntries(report.extraLayers.map((layer) => [layer.id, layer])) }).map(([layer, dataset]) => [layer, read(dataset.file).features.map(drawable)]))
const context = projection.features.map((feature) => projection.path(feature)).join('')
const rows = report.assessments.map((area) => {
  const candidates = Object.fromEntries(Object.keys(layerNames).map((layer) => {
    const match = area.currentBoundaryScreening[layer][0]
    return [layer, layer === 'lha'
      ? { codes: area.modernLhaCodes.map(String), metrics: area.sourceDrawingVsModernCandidate, name: `Modern LHAs ${area.modernLhaCodes.join(' + ')}` }
      : match ? { codes: [String(match.code)], metrics: match, name: `${match.name} (${match.code})` } : null]
  }))
  const original = catalogue.areas.find((entry) => entry.id === area.areaId)
  return { id: area.areaId, name: area.name, group: area.mapId, number: area.legendNumber, method: area.method,
    reason: area.reason, definition: area.definition, remaining: area.remaining, sourceUrl: original.sourceUrl,
    source: source.get(area.areaId), candidates }
})
const reviews = Object.fromEntries(Object.entries(report.alignmentReviews ?? {}).map(([id, review]) => [id, {
  ...review, exportCollection: review.workingAlignment?.enabled ? read(review.workingAlignment.downloadFile) : null,
  supersededComparison: { ...review.supersededComparison, source: drawable({ properties: { code: id, name: 'Withdrawn incomplete trace' }, geometry: review.supersededComparison.geometry }) },
  steps: review.steps.map((step) => ({ ...step, source: drawable({ properties: { code: id, name: 'Unadopted northward-shift preview' }, geometry: step.geometry }) })),
}]))
const sourceInset = 'data:image/png;base64,' + readFileSync(resolve(directory, 'vancouver-richmond-source-detail.png')).toString('base64')
const dataset = { context, current, rows, reviews, sourceInset, reviewedOn: report.reviewedOn }

function extent(row, layer, width, height) {
  const candidate = row.candidates[layer]
  const shapes = [row.source, ...(candidate ? current[layer].filter((feature) => candidate.codes.includes(feature.code)) : [])]
  const xmin = Math.min(...shapes.map((feature) => feature.bounds[0][0]))
  const ymin = Math.min(...shapes.map((feature) => feature.bounds[0][1]))
  const xmax = Math.max(...shapes.map((feature) => feature.bounds[1][0]))
  const ymax = Math.max(...shapes.map((feature) => feature.bounds[1][1]))
  const scale = Math.min((width - 30) / Math.max(xmax - xmin, 2), (height - 26) / Math.max(ymax - ymin, 2))
  return { scale, x: width / 2 - scale * (xmin + xmax) / 2, y: height / 2 - scale * (ymin + ymax) / 2 }
}
function staticMap(row, layer, x, y, width, height, id, sharedView = null) {
  const view = sharedView ?? extent(row, layer, width, height)
  const selected = current[layer].filter((feature) => row.candidates[layer].codes.includes(feature.code))
  return `<defs><clipPath id="${id}"><rect x="${x}" y="${y}" width="${width}" height="${height}" rx="8"/></clipPath></defs>
    <g clip-path="url(#${id})"><rect x="${x}" y="${y}" width="${width}" height="${height}" fill="#edf2f3"/>
    <g transform="translate(${x + view.x} ${y + view.y}) scale(${view.scale})">
      <path d="${context}" fill="#f5f4ee" stroke="#d0d3cc" stroke-width="${.7 / view.scale}"/>
      ${selected.map((feature) => `<path d="${feature.path}" fill="#2393a5" fill-opacity=".16" stroke="#087c91" stroke-dasharray="${6 / view.scale} ${4 / view.scale}" stroke-width="${1.9 / view.scale}"/>`).join('')}
      <path d="${row.source.path}" fill="#b33378" fill-opacity=".1" stroke="#ad256d" stroke-width="${2 / view.scale}"/>
    </g><text x="${x + width - 15}" y="${y + 22}" text-anchor="end" fill="#61716f" font-size="11">N ↑</text></g>`
}
const examples = [
  ['peace-liard-community-health-services-society', 'lha', 'Close broad-scale fit', 'Three modern LHAs closely follow the source drawing.'],
  ['east-kootenay-community-health-services-society', 'lha', 'Close broad-scale fit', 'A predefined LHA combination is a useful working proxy.'],
  ['boundary-health-council', 'schoolDistricts', 'School-district reference', 'Boundary School District 51 closely resembles the drawing.'],
  ['quesnel-and-district-community-health-council', 'schoolDistricts', 'School-district reference', 'Quesnel School District 28 helps check the council edges.'],
  ['snow-country-health-council', 'lha', 'Substantial mismatch', 'The modern combination is much larger than the drawing.'],
  ['vancouver-richmond-health-board', 'lha', 'Original registration; working view adjusts north', 'The app applies a separate provisional 5 km north adjustment.'],
]
const cards = examples.map(([id, layer, label, note], index) => {
  const row = rows.find((entry) => entry.id === id)
  const x = 32 + (index % 2) * 630, y = 177 + Math.floor(index / 2) * 402
  const candidate = row.candidates[layer]
  return `<g><rect x="${x}" y="${y}" width="606" height="382" rx="12" fill="white" stroke="#d8dedc"/>
    <text x="${x + 18}" y="${y + 28}" font-size="19" font-weight="700" fill="#183b35">${xml(row.name)}</text>
    <text x="${x + 585}" y="${y + 28}" text-anchor="end" font-size="21" font-weight="700" fill="#183b35">${Math.round(candidate.metrics.iou * 100)}%</text>
    <text x="${x + 18}" y="${y + 49}" font-size="11" fill="#596e68">${xml(label)} · ${layer === 'schoolDistricts' ? 'current school district' : 'current LHA combination'}</text>
    ${staticMap(row, layer, x + 12, y + 61, 582, 270, `map-${index}`)}
    <text x="${x + 18}" y="${y + 353}" font-size="11.5" fill="#344f47">${xml(note)}</text>
    <text x="${x + 18}" y="${y + 370}" font-size="10" fill="#708078">${xml(candidate.name)}</text>
  </g>`
}).join('')
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1294" height="1475" viewBox="0 0 1294 1475">
  <rect width="1294" height="1475" fill="#f6f7f3"/>
  <g font-family="DejaVu Sans, sans-serif">
  <text x="32" y="35" font-size="11" font-weight="700" letter-spacing="1.5" fill="#55716a">POFBC · HISTORICAL HEALTH BOUNDARIES</text>
  <text x="32" y="75" font-size="30" font-weight="700" fill="#173b35">Where the drawings and current boundaries agree</text>
  <text x="32" y="103" font-size="13" fill="#4e665f">Six examples from the 1997/98 administrative maps, aligned to current BC reference geometry.</text>
  <line x1="33" x2="70" y1="132" y2="132" stroke="#ad256d" stroke-width="3"/><text x="80" y="137" font-size="12" fill="#344f47">Registered historical drawing</text>
  <line x1="350" x2="387" y1="132" y2="132" stroke="#087c91" stroke-width="3" stroke-dasharray="7 4"/><text x="397" y="137" font-size="12" fill="#344f47">Current comparison boundary</text>
  <text x="32" y="159" font-size="11" fill="#667a72">Percentages are drawing intersection-over-union, not legal verification or registration accuracy. Scale varies by area.</text>
  ${cards}
  <text x="32" y="1412" font-size="11" fill="#455e55">Three physical controls per main map. Insets remain unregistered. Source traces show approximate land display, not marine jurisdiction.</text>
  <text x="32" y="1433" font-size="11" fill="#455e55">Original Ministry maps: BC Auditor General, March 1998. Current BC data: Open Government Licence – British Columbia.</text>
  <text x="32" y="1454" font-size="11" fill="#455e55">The downloadable comparison viewer includes all 52 labels, six current boundary types, definitions and explicit estimate choices.</text>
  </g></svg>`
writeFileSync(resolve(directory, 'comparison-examples.svg'), svg)
// Keep deterministic vector/HTML checks independent of runner-installed fonts.
if (!process.argv.includes('--no-png')) writeFileSync(resolve(directory, 'comparison-examples.png'), new Resvg(svg, { font: { loadSystemFonts: true } }).render().asPng())

// Preserve the error and membership correction alongside the provisional working shift.
const reviewedRow = rows.find((row) => reviews[row.id])
const review = reviews[reviewedRow.id]
const northPreview = review.steps.find((step) => step.northShiftMetres === 5000)
const coastBefore = (review.physicalCheck.scenarios[0].p95Metres / 1000).toFixed(1)
const coastAfter = (review.physicalCheck.scenarios[1].p95Metres / 1000).toFixed(1)
const reviewShapes = [review.supersededComparison.source, reviewedRow.source, northPreview.source]
const sharedReviewView = extent({ ...reviewedRow, source: { bounds: [
  [Math.min(...reviewShapes.map((shape) => shape.bounds[0][0])), Math.min(...reviewShapes.map((shape) => shape.bounds[0][1]))],
  [Math.max(...reviewShapes.map((shape) => shape.bounds[1][0])), Math.max(...reviewShapes.map((shape) => shape.bounds[1][1]))],
] } }, 'lha', 405, 310)
const reviewCards = [
  ['Previous trace — withdrawn', review.supersededComparison.source, review.supersededComparison.metrics, 'Richmond was omitted; modern-land clipping hid mismatch.'],
  ['Both source components', reviewedRow.source, reviewedRow.candidates.lha.metrics, 'Vancouver + Richmond; original registration retained.'],
  ['Working trace: 5 km north', northPreview.source, northPreview.metricsByLayer.lha, 'Applied provisional local display; legal limits unverified.'],
].map(([label, source, metrics, note], index) => {
  const x = 22 + index * 425
  return `<text x="${x}" y="132" font-size="16" font-weight="700" fill="#173b35">${xml(label)}</text>
    <text x="${x}" y="157" font-size="18" font-weight="700" fill="#173b35">${Math.round(metrics.iou * 100)}% drawing overlap</text>
    ${staticMap({ ...reviewedRow, source }, 'lha', x, 173, 405, 310, `review-${index}`, sharedReviewView)}
    <text x="${x}" y="505" font-size="10" fill="#455e55">${xml(note)}</text>`
}).join('')
const reviewSvg = `<svg xmlns="http://www.w3.org/2000/svg" width="1294" height="588" viewBox="0 0 1294 588"><rect width="1294" height="588" fill="#f6f7f3"/><g font-family="DejaVu Sans, sans-serif">
  <text x="22" y="37" font-size="26" font-weight="700" fill="#173b35">Vancouver/Richmond: source correction and northward-shift review</text>
  <text x="22" y="64" font-size="12" fill="#4e665f">The published inset labels both Vancouver and Richmond as 9. The former trace omitted Richmond.</text>
  <line x1="22" x2="59" y1="90" y2="90" stroke="#ad256d" stroke-width="3"/><text x="69" y="95" font-size="12" fill="#344f47">Historical trace</text>
  <line x1="250" x2="287" y1="90" y2="90" stroke="#087c91" stroke-width="3" stroke-dasharray="7 4"/><text x="297" y="95" font-size="12" fill="#344f47">Modern Vancouver + Richmond LHAs</text>
  ${reviewCards}
  <text x="22" y="546" font-size="12" fill="#455e55">The working view now applies this provisional local adjustment. Original registration and source evidence are retained.</text>
  <text x="22" y="568" font-size="12" fill="#455e55">Bowen Island held-out shoreline check: P95 separation falls from ${coastBefore} to ${coastAfter} km with the same northward preview.</text>
  </g></svg>`
writeFileSync(resolve(directory, 'vancouver-richmond-alignment-review.svg'), reviewSvg)
if (!process.argv.includes('--no-png')) writeFileSync(resolve(directory, 'vancouver-richmond-alignment-review.png'), new Resvg(reviewSvg, { font: { loadSystemFonts: true } }).render().asPng())

const groups = Object.entries(labels).map(([id, label]) => `<optgroup label="${label}">${rows.filter((row) => row.group === id).map((row) => `<option value="${row.id}">${row.number}. ${xml(row.name)}</option>`).join('')}</optgroup>`).join('')
const serialized = JSON.stringify(dataset).replaceAll('<', '\\u003c')
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PofBC — 52 boundary comparisons</title>
<style>
:root{font-family:system-ui,sans-serif;color:#183b35;background:#f6f7f3;font-size:15px;line-height:1.55}*{box-sizing:border-box}[hidden]{display:none!important}body{margin:0}main{max-width:1500px;padding:28px;margin:auto}h1{font-size:clamp(25px,3vw,42px);letter-spacing:-.035em;line-height:1.15;margin:10px 0 12px}h2{font-size:24px;margin:8px 0}h3{font-size:15px;margin:0;padding:13px 16px;border-bottom:1px solid #dde3dd}.kicker{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#55716a;font-weight:700}.intro{max-width:1000px;color:#526a61}.controls{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:24px 0 16px}label{font-size:12px;font-weight:650;display:grid;gap:6px}select{font:inherit;font-size:14px;background:white;color:inherit;min-height:44px;border:1px solid #bac7c0;border-radius:7px;padding:8px;width:100%;min-width:0}.quick{display:flex;gap:6px;flex-wrap:wrap}button{font:inherit;font-size:12px;background:white;border:1px solid #c4d0c8;border-radius:6px;color:inherit;padding:8px 12px;min-height:38px;cursor:pointer}button:hover,button[aria-pressed="true"]{background:#dfece5}.score{display:flex;gap:22px;align-items:baseline;flex-wrap:wrap;margin:22px 0 5px}.score strong{font-size:30px;letter-spacing:-.04em}.score small{color:#567164}#overlay-controls{display:flex;flex-wrap:wrap;gap:8px 18px;padding:12px;border:1px solid #c9d4cb;margin-top:12px}#overlay-controls label{display:inline-flex;align-items:center;gap:6px}#overlay-controls legend{font-size:12px;padding:0 5px}.legend{display:flex;gap:20px;flex-wrap:wrap;font-size:12px;margin:15px 0}.legend span{display:flex;align-items:center;gap:7px}.swatch{width:28px;display:inline-block;border-top:3px solid #ad256d}.swatch.modern{border-color:#087c91;border-top-style:dashed}.maps{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}.map{background:white;border:1px solid #d7dfd9;border-radius:9px;overflow:hidden}.map svg{width:100%;height:360px;background:#edf2f3;display:block}.map footer{padding:9px 15px;font-size:12px;min-height:58px;color:#526d60}.notice{padding:13px 17px;border-left:3px solid #a36636;background:#f2ebe0;color:#534937;font-size:13px;margin:18px 0}.notes{display:grid;grid-template-columns:1fr 1fr;gap:18px;margin-top:22px}.notes>section{background:white;border:1px solid #d7dfd9;padding:18px;border-radius:9px;min-width:0;overflow-wrap:anywhere}.notes h3{padding:0 0 10px}a{color:#186959;text-underline-offset:3px}details{border-top:1px solid #d8dfd9;padding-top:12px;margin-top:16px}summary{cursor:pointer;font-weight:600;font-size:13px}.small{font-size:12px;color:#5f7469}.method{font-size:13px}p{margin:12px 0}.empty{fill:#66796f;font-size:12px}*:focus-visible{outline:3px solid #b66d31;outline-offset:3px}@media(max-width:850px){main{padding:18px}.maps{grid-template-columns:1fr}.map svg{height:340px}.notes{grid-template-columns:1fr}.controls{grid-template-columns:1fr}.score{gap:10px}.score strong{font-size:26px}}@media print{.controls,.quick{display:none}.maps{grid-template-columns:repeat(3,1fr)}.map svg{height:250px}.notes{display:block}main{padding:0}}
</style></head><body><main>
<div class="kicker">PofBC · historical atlas · comparison viewer</div><h1>See the boundary comparisons</h1>
<p class="intro">Compare every administrative map label with current health, municipal, regional-district and school-district boundaries. Each row of maps shares one extent: the historical drawing, the current candidate, and their overlay.</p>
<div class="controls"><label>Historical area<select id="area">${groups}</select></label><label>Current reference<select id="reference">${Object.entries(layerNames).map(([id, label]) => `<option value="${id}">${label}</option>`).join('')}</select></label></div>
<div class="quick" aria-label="Example comparisons">${examples.map(([id, layer]) => `<button type="button" data-area="${id}" data-reference="${layer}">${xml(rows.find((row) => row.id === id).name)}</button>`).join('')}</div>
<section id="alignment-controls" hidden class="notice"><label for="north-shift">Local northward alignment · provisional <input id="north-shift" type="range" min="0" max="10000" step="1000" value="0" /></label><p id="shift-label"></p><button type="button" id="preview-north">Show original alignment (0 km)</button> <button type="button" id="reset-shift">Reset to working alignment</button><p class="small">The working view applies a 5 km northward local display adjustment. The earlier 29% result is withdrawn: it omitted Richmond and clipped the source to modern land. Both components are retained, and the original global registration remains available. Other slider positions are exploratory scenarios.</p><fieldset id="overlay-controls"><legend>Layers in the overlay panel</legend><label><input type="checkbox" id="show-reference" checked />Current reference boundaries</label><label><input type="checkbox" id="show-original" />Original trace</label><label><input type="checkbox" id="show-adjusted" checked />Adjusted trace</label></fieldset><p><a id="export-alignment" download>Download reference map + original and adjusted traces ↓</a></p><a href="${catalogue.areas.find((area) => area.id === reviewedRow.id).sourceUrl}" target="_blank" rel="noreferrer">Check the original inset with both printed 9s ↗</a></section>
<div class="score" aria-live="polite"><strong id="score"></strong><span id="candidate"></span><small id="coverage"></small></div>
<p class="small">Drawing overlap = intersection ÷ union of the two shapes. It does not establish legal identity or positional accuracy. Scores were calculated in BC Albers; these maps use a common conformal display projection.</p>
<div class="legend"><span><i class="swatch"></i>Original registered trace</span><span><i class="swatch modern"></i>Current reference map</span><span id="adjusted-legend" hidden><i class="swatch" style="border-color:#a44c08"></i>Provisional adjusted trace</span></div>
<div class="maps"><section class="map"><h3>1 · Original trace</h3><svg id="historical" role="img"></svg><footer>Source-drawn approximation from the original global registration, before any local adjustment.</footer></section><section class="map"><h3>2 · Current reference map</h3><svg id="current" role="img"></svg><footer id="current-caption"></footer></section><section class="map"><h3 id="overlay-heading">3 · Overlay</h3><svg id="overlay" role="img"></svg><footer id="overlay-caption">The outlines separate where the drawings differ. All three panels share the same extent.</footer></section></div>
<figure id="source-evidence" hidden style="max-width:520px;margin:20px 0"><img style="width:100%;height:auto;display:block" src="${sourceInset}" alt="Original published inset showing both Vancouver and Richmond labelled 9" /><figcaption class="small">Original source inset; retained as published, with Vancouver and Richmond both labelled 9.</figcaption></figure>
<p class="notice" id="specific-limit"></p>
<div class="notes"><section><h3>Chosen working estimate</h3><p class="method" id="method"></p><p id="reason"></p><p><a id="original" target="_blank" rel="noreferrer">Open the original published map ↗</a></p><p class="small" id="remaining"></p></section><section><h3>What defines this territory?</h3><div id="definition"></div><p class="small">Society service areas, the 1997/98 map, later 2001 descriptions and modern statistical geography are different evidence. Keep their dates and purposes separate.</p></section></div>
<details><summary>Registration, source dates and uncertainty</summary><p>Three physical control points per main-map page support a preliminary affine fit in BC Albers. They provide no independent registration accuracy. Comparisons retain the full source footprint without clipping it to modern land; marine jurisdiction is unresolved. The selected modern edges were not used to fit the maps or extract the council traces.</p><p>Southern insets and the separate twenty-region statistical map are not registered. Coarse metropolitan source detail limits the Vancouver/Richmond comparison. Current municipalities and school districts may differ from their historical versions. Individual-feature screening is distinct from comparing a whole modern LHA combination. The working Vancouver/Richmond trace applies a provisional 5 km northward local display adjustment. Other slider positions are sensitivity scenarios; the original global registration controls remain unchanged.</p><p>Original Ministry of Health cartography: BC Auditor General, March 1998. Current BC data retain the Open Government Licence – British Columbia. Data and results are embedded in this file; it works offline. No historical legal boundary is verified.</p></details>
</main><script id="data" type="application/json">${serialized}</script><script>
const data=JSON.parse(document.getElementById('data').textContent);
const area=document.getElementById('area'), reference=document.getElementById('reference'), northShift=document.getElementById('north-shift');
const referenceVisible=document.getElementById('show-reference'),originalVisible=document.getElementById('show-original'),adjustedVisible=document.getElementById('show-adjusted');
const exportUrls=Object.fromEntries(Object.entries(data.reviews).filter(([,review])=>review.exportCollection).map(([id,review])=>[id,URL.createObjectURL(new Blob([JSON.stringify(review.exportCollection)],{type:'application/geo+json'}))]));
const methods={'modern-single':'Predefined modern area','modern-combination':'Combination of predefined modern areas','source-drawn':'Historical source-drawing approximation'};
const esc=text=>String(text).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
function render(){
 const row=data.rows.find(row=>row.id===area.value), layer=reference.value, candidate=row.candidates[layer];
 const review=data.reviews[row.id], shift=review?Number(northShift.value):0, step=review?.steps.find(step=>step.northShiftMetres===shift);
 const source=step?.source??row.source, metrics=step?.metricsByLayer[layer]??candidate?.metrics;
 const workingShift=review?.workingAlignment?.enabled?review.workingAlignment.northShiftMetres:0, isWorking=Boolean(review)&&shift===workingShift;
 document.getElementById('alignment-controls').hidden=!review;
 document.getElementById('adjusted-legend').hidden=!review;
 document.getElementById('source-evidence').hidden=!review;
 document.getElementById('overlay-heading').textContent=review?'3 · Working trace + reference':'3 · Overlay';
 document.getElementById('overlay-caption').textContent=review?'Orange: locally adjusted trace. Magenta: original trace when enabled. Teal: current reference. The three maps share one extent.':'The outlines separate where the drawings differ. All three panels share the same extent.';
 if(review){const link=document.getElementById('export-alignment');link.href=exportUrls[row.id];link.download=review.workingAlignment.downloadFile;}
 const check=review?.physicalCheck;
 document.getElementById('shift-label').textContent=(isWorking?'Working alignment: '+shift/1000+' km north. Applied provisional local display. Original global registration retained.':'Scenario: '+shift/1000+' km north. The stored working alignment remains '+workingShift/1000+' km north.')+(check?' Held-out Bowen Island shoreline check: a 5 km northward scenario lowers P95 separation from '+(check.scenarios[0].p95Metres/1000).toFixed(1)+' to '+(check.scenarios[1].p95Metres/1000).toFixed(1)+' km. This includes shoreline generalization; it is not registration RMSE.':'');
 const modern=candidate?data.current[layer].filter(feature=>candidate.codes.includes(feature.code)):[];
 const shapes=[row.source,source,...modern], xmin=Math.min(...shapes.map(f=>f.bounds[0][0])), ymin=Math.min(...shapes.map(f=>f.bounds[0][1])), xmax=Math.max(...shapes.map(f=>f.bounds[1][0])), ymax=Math.max(...shapes.map(f=>f.bounds[1][1]));
 const w=Math.max(xmax-xmin,2)*1.13, h=Math.max(ymax-ymin,2)*1.13, cx=(xmin+xmax)/2, cy=(ymin+ymax)/2;
 const background='<path d="'+data.context+'" fill="#f5f4ee" stroke="#d0d3cc" stroke-width=".65" vector-effect="non-scaling-stroke"/>';
 const old='<path class="original-trace" d="'+row.source.path+'" fill="#b33378" fill-opacity=".12" stroke="#ad256d" stroke-width="1.8" vector-effect="non-scaling-stroke"/>';
 const adjusted='<path class="adjusted-trace" d="'+source.path+'" fill="#c17522" fill-opacity=".18" stroke="#a44c08" stroke-width="2" vector-effect="non-scaling-stroke"/>';
 const now=modern.map(f=>'<path class="reference-boundary" d="'+f.path+'" fill="#2393a5" fill-opacity=".18" stroke="#087c91" stroke-dasharray="6 4" stroke-width="1.8" vector-effect="non-scaling-stroke"/>').join('');
 const overlay=review?(referenceVisible.checked?now:'')+(originalVisible.checked?old:'')+(adjustedVisible.checked?adjusted:''):now+old;
 for(const [id,paths] of [['historical',old],['current',now],['overlay',overlay]]){
  const svg=document.getElementById(id);svg.setAttribute('viewBox',[cx-w/2,cy-h/2,w,h].join(' '));svg.setAttribute('aria-label',row.name+': '+id+' boundary comparison');svg.innerHTML=background+paths;
 }
 document.getElementById('score').textContent=candidate?Math.round(metrics.iou*100)+'% drawing overlap'+(review?(isWorking?' · working trace':shift?' · preview':' · original trace'):''):'No intersecting current feature';
 document.getElementById('candidate').textContent=candidate?candidate.name:'';
 document.getElementById('coverage').textContent=candidate?'Source covered: '+Math.round(metrics.sourceCovered*100)+'% · candidate covered: '+Math.round(metrics.candidateCovered*100)+'%':'';
 document.getElementById('current-caption').textContent=candidate?candidate.name:'No intersecting feature was found in this layer.';
 const metropolitan=['vancouver-richmond-health-board','capital-health-region','south-fraser-health-region','north-shore-health-region'].includes(row.id);
 document.getElementById('specific-limit').textContent=review?'A provisional 5 km northward adjustment is applied to the working trace. The earlier 29% comparison is withdrawn. The reference map, original trace and source evidence remain available. Independent coastal controls, inset registration and legal-boundary verification remain outstanding.':metropolitan?'Main-map detail is limited here. A low score can reflect omitted inset detail and registration uncertainty; it cannot settle whether modern boundaries match the historical legal territory.':row.id==='snow-country-health-council'?'The modern LHA combination is considerably larger than the historical drawing. The working estimate follows the source drawing, bounded by the independently documented 57th parallel. Watershed and cadastral reconstruction remain outstanding.':'This is a cartographic comparison. High overlap supports an approximate display candidate; it does not verify an unchanged historical legal boundary.';
 document.getElementById('method').textContent=methods[row.method]+' · historical legal boundary unverified';
 document.getElementById('reason').textContent=row.reason;
 document.getElementById('original').href=row.sourceUrl;
 document.getElementById('remaining').textContent='Still needed: '+row.remaining;
 const d=row.definition;
 document.getElementById('definition').innerHTML=d?'<p><a href="'+esc(d.sourceUrl)+'" target="_blank" rel="noreferrer">'+esc(d.heading)+' ↗</a></p><p class="small">'+esc(d.dateContext)+'</p><p>'+esc(d.summary)+'</p>'+(d.namedWaterFeatures?.length?'<p class="small"><b>Water features to trace:</b> '+esc(d.namedWaterFeatures.join('; '))+'.</p>':'')+(d.relatedEntityOnly?'<p class="notice">This describes a related statutory council. Identity with the source map’s Nisga’a authority label remains unresolved.</p>':''):'<p>The society’s operative service-area agreement and geographic schedules are still needed. Its map supports a provisional drawing only.</p>';
 document.querySelectorAll('.quick button').forEach(button=>button.setAttribute('aria-pressed',button.dataset.area===row.id&&button.dataset.reference===layer));
 try{history.replaceState(null,'','#'+row.id+'/'+layer+(review?'/'+shift:''))}catch{}
}
const [requestedArea,requestedLayer,requestedShift]=location.hash.slice(1).split('/');
area.value=data.rows.some(row=>row.id===requestedArea)?requestedArea:'peace-liard-community-health-services-society';
if(Object.keys(data.current).includes(requestedLayer))reference.value=requestedLayer;
const defaultShift=()=>{northShift.value=data.reviews[area.value]?.workingAlignment?.northShiftMetres??0};defaultShift();
if(requestedShift!==undefined&&data.reviews[area.value]?.steps.some(step=>step.northShiftMetres===Number(requestedShift)))northShift.value=requestedShift;
area.addEventListener('change',()=>{defaultShift();render()});reference.addEventListener('change',render);northShift.addEventListener('input',render);
[referenceVisible,originalVisible,adjustedVisible].forEach(control=>control.addEventListener('change',render));
document.getElementById('preview-north').addEventListener('click',()=>{northShift.value=0;render()});document.getElementById('reset-shift').addEventListener('click',()=>{defaultShift();render()});
document.querySelectorAll('.quick button').forEach(button=>button.addEventListener('click',()=>{area.value=button.dataset.area;reference.value=button.dataset.reference;defaultShift();render()}));render();
</script></body></html>`
writeFileSync(resolve(directory, 'comparisons.html'), html)
console.log(`Rendered six comparison examples and an offline viewer for ${rows.length} historical labels / ${Object.keys(current).length} reference layers.`)
