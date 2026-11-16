"""Write proposed-assets.json for this package (run from the repository root)."""
import json, hashlib, os

PKG = 'railway-marks-vector-2026-11-16'
R = 'research/identity/' + PKG
fit = {k: json.load(open(R + '/fit/' + k)) for k in os.listdir(R + '/fit') if k.startswith('m_')}


def runiou(m):
    return ' and '.join('%.2f' % r['meanIoU'] for r in fit[m]['runs'])


C3 = 'https://www.cwrailway.ca/sites/default/files/Cariboo/Cariboo%20-%20Issue%203.pdf'
TRACE = ('The caribou is an automatic outline (potrace, from the 300-dpi illustration upsampled ×4, '
         'specks under 40 px removed) used as drawn, not hand-redrawn; ')
# whole-mark overlap with the binarised source (scripts/overlay.py; scenic: inside the badge only)
OVER = {'m_eq45.json': 0.86, 'm_light.json': 0.91, 'm_bold.json': 0.88, 'm_eqm46.json': 0.88,
        'm_r47.json': 0.84, 'm_oval56.json': 0.87, 'm_ovalred.json': 0.85, 'm_scenic.json': 0.88}

items = [
    dict(t='source-bc-railway-company-bc-railway-company-png', b='bc-railway-company', id='bcrc-website-wordmark-rebuilt',
         f='bc-railway-company/bcrc-website-wordmark-rebuilt.svg',
         label='BC Railway Company — Website wordmark, rebuilt', publisher='British Columbia Railway Company',
         page='https://bcrco.com/', url='https://bcrco.com/wp-content/uploads/2024/10/bcrco_logo-1.png',
         loc='Site logo PNG (236 × 124); fitted to the 485 × 250 version of the same artwork in the Wayback Machine’s 8 July 2022 capture (wp1/wp-content/uploads/2022/03/cropped-bcrco_logo.png)',
         sdate=None, sfile=None, dnote='Website artwork, undated; seen on the site from 2022 to 2026.',
         notes='The BCRC acrostic as the Company’s website shows it: British Columbia Railway Company stepped down on four lines in a heavy humanist italic, initials red and the rest blue.',
         fid='A vector reconstruction, not original artwork: no vector of this lettering was found on bcrco.com or in 63 archived Company PDFs. The 29 letters are Source Sans 3 Italic (weight 800) outlines with one shared widening (about 118%) and added slant (about 4°), each letter placed to the 485-px capture (silhouette overlap about 0.84 there, 0.79 against the 236-px file). Source Sans 3 is a free match in the Myriad manner; the original typeface is not verified. The web image’s thin white edge is left out. Red #E10C14 and blue #29388C are sampled.'),
    dict(t='cariboo-pge-point-ellice-diamond-1929', b='pacific-great-eastern-railway', id='pge-point-ellice-diamond-1929-rebuilt',
         f='pacific-great-eastern-railway/pge-point-ellice-diamond-1929-rebuilt.svg', pg=5,
         label='PGE Point Ellice diamond monogram, rebuilt',
         notes='A tall diamond outline around a ring and an interlaced monoline P, G, E and R, as illustrated for the steam tug Point Ellice.',
         fid='A vector reconstruction, not original artwork: the diamond and ring are fitted to both edges of the printed lines, and the P-G-E-R monogram is drawn by hand as monoline strokes (lines and arcs), checked by overlay (overlap 0.88). No tracing and no type. Near-black, as illustrated; the article’s medium-dark green on white is not applied.'),
    dict(t='cariboo-pge-square-diamond-unshaded-c1934', b='pacific-great-eastern-railway', id='pge-square-diamond-unshaded-c1934-rebuilt',
         f='pacific-great-eastern-railway/pge-square-diamond-unshaded-c1934-rebuilt.svg', pg=5,
         label='PGE square diamond, unshaded, rebuilt',
         notes='A square diamond with an inner diamond broken at the ring, around an interlaced Roman P, G and E, as illustrated for steam crane 6071.',
         fid='A vector reconstruction, not original artwork: the outer diamond, the four corners of the inner diamond and the ring are fitted lines and circles; the interlaced monogram is an automatic outline (potrace, from the illustration upsampled ×4) used as drawn, not hand-redrawn. Overall overlap 0.91. One colour, as illustrated; the article qualifies the colour.'),
    dict(t='cariboo-pge-circular-script-monogram-1935', b='pacific-great-eastern-railway', id='pge-circular-script-monogram-1935-rebuilt',
         f='pacific-great-eastern-railway/pge-circular-script-monogram-1935-rebuilt.svg', pg=6,
         label='PGE circular script monogram, rebuilt',
         notes='Script P, G and E inside a heavy ring and a thin outer circle, as on company passes and menus.',
         fid='A vector reconstruction, not original artwork: the heavy ring and the thin circle are fitted to both edges of each; the script letters are an automatic outline (potrace, from the illustration upsampled ×4) used as drawn, not hand-redrawn. Overlap 0.97. One colour, as illustrated.'),
    dict(t='cariboo-pge-caribou-rolling-stock-1945', b='pacific-great-eastern-railway', id='pge-caribou-rolling-stock-1945-rebuilt',
         f='pacific-great-eastern-railway/pge-caribou-rolling-stock-1945-rebuilt.svg', pg=7, m='m_eq45.json',
         label='PGE early caribou equipment herald, rebuilt',
         notes='PACIFIC GREAT EASTERN RLY in a condensed gothic between two heavy rings, a caribou head in the centre.',
         fid='A vector reconstruction, not original artwork: the rings are fitted circles; the lettering is Oswald Bold outlines, each letter placed and turned to the illustration (mean letter overlap {iou} for the two runs of lettering); Oswald is a free condensed-gothic match and the original lettering is not verified. ' + TRACE + 'overall overlap {all}.'),
    dict(t='cariboo-pge-caribou-corporate-light-1946', b='pacific-great-eastern-railway', id='pge-caribou-corporate-light-1946-rebuilt',
         f='pacific-great-eastern-railway/pge-caribou-corporate-light-1946-rebuilt.svg', pg=7, m='m_light.json',
         label='PGE corporate caribou with light lettering, rebuilt',
         notes='A black disc with a white caribou head in full profile and PACIFIC GREAT EASTERN RLY in light, wide capitals.',
         fid='A vector reconstruction, not original artwork: the disc and white rings are fitted circles; the lettering is Montserrat SemiBold outlines, widened 20–30% and placed letter by letter (mean letter overlap {iou} for the two runs of lettering); the original typeface is not verified. ' + TRACE + 'overall overlap {all}.'),
    dict(t='cariboo-pge-caribou-corporate-bold-1948', b='pacific-great-eastern-railway', id='pge-caribou-corporate-bold-1948-rebuilt',
         f='pacific-great-eastern-railway/pge-caribou-corporate-bold-1948-rebuilt.svg', pg=7, m='m_bold.json',
         label='PGE corporate caribou with bold lettering, rebuilt',
         notes='The corporate caribou disc with its lettering in heavy, wide capitals.',
         fid='A vector reconstruction, not original artwork: the disc and white rings are fitted circles; the lettering is Poppins ExtraBold outlines, widened about 10% and placed letter by letter (mean letter overlap {iou} for the two runs of lettering); Poppins is a free geometric match and the original typeface is not verified. ' + TRACE + 'overall overlap {all}.'),
    dict(t='cariboo-pge-caribou-rolling-stock-mid1946', b='pacific-great-eastern-railway', id='pge-caribou-rolling-stock-mid1946-rebuilt',
         f='pacific-great-eastern-railway/pge-caribou-rolling-stock-mid1946-rebuilt.svg', pg=8, m='m_eqm46.json',
         label='PGE revised caribou equipment herald, rebuilt',
         notes='The equipment herald with the revised caribou head, condensed gothic lettering between two heavy rings.',
         fid='A vector reconstruction, not original artwork, of an illustration its author describes as a tracing: the rings are fitted circles; the lettering is Oswald Bold outlines placed letter by letter (mean letter overlap {iou} for the two runs of lettering); the original lettering is not verified. ' + TRACE + 'overall overlap {all}.'),
    dict(t='cariboo-pge-caribou-passenger-roman-1947', b='pacific-great-eastern-railway', id='pge-caribou-passenger-roman-1947-rebuilt',
         f='pacific-great-eastern-railway/pge-caribou-passenger-roman-1947-rebuilt.svg', pg=8, m='m_r47.json',
         label='PGE Roman-lettered passenger-car caribou, rebuilt',
         notes='The passenger-car herald: a caribou head inside a ring, PACIFIC GREAT EASTERN RLY. in Roman capitals.',
         fid='A vector reconstruction, not original artwork: the rings are fitted circles; the lettering is C059 Bold (a Century Schoolbook-style face) outlines placed letter by letter (mean letter overlap {iou} for the two runs of lettering); the original Roman is not verified. ' + TRACE + 'overall overlap {all}. The handwritten note beside the source is left out.'),
    dict(t='cariboo-pge-caribou-oval-advertising-1956', b='pacific-great-eastern-railway', id='pge-caribou-oval-advertising-1956-rebuilt',
         f='pacific-great-eastern-railway/pge-caribou-oval-advertising-1956-rebuilt.svg', pg=8, m='m_oval56.json',
         label='PGE oval advertising caribou, rebuilt',
         notes='A black oval with a white caribou head and PACIFIC GREAT / EASTERN in heavy, wide capitals.',
         fid='A vector reconstruction, not original artwork: the oval and white ring are fitted ellipses (the source crop clips the oval’s left edge, so its extent there is inferred); the lettering is Poppins Black outlines, widened 30–45% and placed letter by letter (mean letter overlap {iou} for the two runs of lettering); the original typeface is not verified. ' + TRACE + 'overall overlap {all}.'),
    dict(t='source-pacific-great-eastern-railway-pge-brochure-logo-png', b='pacific-great-eastern-railway', id='pge-brochure-logo-rebuilt',
         f='pacific-great-eastern-railway/pge-brochure-logo-rebuilt.svg', m='m_ovalred.json',
         label='Oval caribou mark from Gateway to an Empire, rebuilt', publisher='Pacific Great Eastern Railway; scan hosted by Streamliner Memories',
         page='https://streamlinermemories.info/?p=6712', url='https://streamlinermemories.info/CAN/PGEbro.pdf',
         loc='PDF page 1, re-rendered at 302 dpi (the scan’s own resolution)', sdate=None, sfile=None,
         dnote='Undated original; collector estimates late 1950s or early 1960s.',
         notes='The oval caribou mark in red, with white caribou and lettering, from the cover of Gateway to an Empire.',
         fid='A vector reconstruction, not original artwork: the oval and white ring are fitted ellipses; the lettering is Poppins Black outlines, widened 40–55% and placed letter by letter (mean letter overlap {iou} for the two runs of lettering); the original typeface is not verified. The caribou is an automatic outline (potrace, from the scan’s green channel upsampled ×4) used as drawn; overall overlap {all}. Red #FD2A2F is sampled from the print.'),
    dict(t='source-pacific-great-eastern-railway-pge-scenic-route-brochure-logo-png', b='pacific-great-eastern-railway', id='pge-scenic-route-brochure-logo-rebuilt',
         f='pacific-great-eastern-railway/pge-scenic-route-brochure-logo-rebuilt.svg', m='m_scenic.json',
         label='Circular caribou mark from The Scenic Route of British Columbia, rebuilt', publisher='Pacific Great Eastern Railway; scan hosted by Streamliner Memories',
         page='https://streamlinermemories.info/?p=9750', url='https://streamlinermemories.info/CAN/PGE55.pdf',
         loc='PDF page 1, re-rendered at 302 dpi (the scan’s own resolution)', sdate=None, sfile=None,
         dnote='Undated; the filename PGE55 is not a verified publication date.',
         notes='The corporate caribou disc in yellow on black, from the cover of The Scenic Route of British Columbia; the cover painting around it is left out.',
         fid='A vector reconstruction, not original artwork: the disc and yellow rings are fitted circles; the lettering is Poppins ExtraBold outlines placed letter by letter (mean letter overlap {iou} for the two runs of lettering); the original typeface is not verified. The caribou is an automatic outline (potrace, from the scan’s red channel upsampled ×4) used as drawn; the soft colour scan loses the neck shading. Overlap inside the badge {all}. Yellow #EEA920 and black #1F1A16 are sampled.'),
]

out = []
for it in items:
    p = 'public/identity-collected/' + it['f']
    data = open(p, 'rb').read()
    fid = it['fid']
    if 'm' in it:
        fid = fid.replace('{iou}', runiou(it['m'])).replace('{all}', '%.2f' % OVER[it['m']])
    cariboo = 'pg' in it
    a = dict(
        id=it['id'], label=it['label'], file='identity-collected/' + it['f'], format='svg', isVector=True,
        supplied=False, reconstruction=True,
        publisher=it.get('publisher', 'The Cariboo; Greg M. Kennelly (logo article and livery diagrams)'),
        sourcePage=it.get('page', C3 + '#page=%d' % it['pg'] if cariboo else None),
        sourceUrl=it.get('url', C3),
        sourceLocator=it.get('loc', 'The Cariboo, Issue 3, January 1991, PDF page %d (the registered 300-dpi crop)' % it.get('pg', 0)),
        sourceFile=it.get('sfile', 'The Cariboo, Issue 3, January 1991'),
        sourceDate=it.get('sdate', '1991-01'), observedDate='2026-11-16',
        dateNote=it.get('dnote', 'January 1991 dates the published illustration this follows, not the mark’s introduction or use.'),
        evidenceType='vector-reconstruction', notes=it['notes'], fidelityNote=fid,
        sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), darkBackground=False, search=PKG)
    out.append(dict(targetAssetId=it['t'], dataFile='collectedData.js', bodyId=it['b'], asset=a))
json.dump(out, open(R + '/proposed-assets.json', 'w'), indent=2, ensure_ascii=False)
print(len(out), 'records')
