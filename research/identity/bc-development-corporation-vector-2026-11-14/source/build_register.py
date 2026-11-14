import hashlib, json, re, sys
from pathlib import Path
root = Path('/home/user/PofBC')
pub = root / 'public'
def meta(rel):
    data = (pub / rel).read_bytes()
    return hashlib.sha256(data).hexdigest(), len(data)
def verify(rel):
    t = (pub / rel).read_text()
    return {"genuineVectorVerified": True, "embeddedImages": len(re.findall(r'<image\b', t)),
            "textElements": len(re.findall(r'<text\b', t)),
            "externalResources": re.findall(r'href="(https?:[^"]+)"', t)}
D = 'identity-collected/bc-development-corporation/'
CIPO = 'https://ised-isde.canada.ca/cipo/trademark-search/'
FS_FID = ('A supplied vector reconstruction, not original artwork: the four outlined squares are constructed geometry and every letter a hand-authored outline after the one-bit CIPO specimen '
          '(no automatic tracing). Raster irregularities are regularized; the historical typeface is not identified. Black, as the specimen is; no official colour is recorded. The CIPO specimen is kept as a download.')
def asset(id, label, file, sourcePage, sourceUrl, locator, sourceFile, sourceDate, dateNote, notes, fidelity, downloads, alsoSeen=None, evidence='supplied-vector-reconstruction', publisher='British Columbia Development Corporation'):
    sha, size = meta(D + file)
    a = {"bodyId": "bc-development-corporation", "id": id, "label": label, "file": D + file, "format": "svg",
         "isVector": True, "supplied": True, "reconstruction": True, "publisher": publisher,
         "sourcePage": sourcePage, "sourceUrl": sourceUrl, "sourceLocator": locator, "sourceFile": sourceFile,
         "sourceDate": sourceDate, "observedDate": "2026-11-14", "dateNote": dateNote}
    if alsoSeen: a["alsoSeen"] = alsoSeen
    a.update({"evidenceType": evidence, "notes": notes, "fidelityNote": fidelity, "sha256": sha, "bytes": size,
              "darkBackground": False,
              "downloads": [{"label": l, "file": D + f, "sha256": meta(D + f)[0]} for l, f in downloads],
              "verification": verify(D + file)})
    return a
def cipo(n, label, file, kind, filed, dateNote, notes):
    return asset(f'bcdc-four-square-{file}', label, f'bcdc-four-square-{file}-rebuilt.svg',
                 CIPO + str(n), CIPO + f'media/{n}.png',
                 f'CIPO application {n:07d}, {kind} specimen', f'Canadian Intellectual Property Office, application {n:07d}',
                 filed, dateNote, notes, FS_FID, [(f'Download CIPO {n:07d} specimen (PNG)', f'bcdc-cipo-{n}-specimen.png')])
assets = [
  asset('bcdc-prism-1975', 'British Columbia Development Corporation — Four prisms and four-line name', 'bcdc-prism-1975-rebuilt.svg',
        'https://open.library.ubc.ca/collections/alderstar/items/1.0420232',
        'https://iiif.library.ubc.ca/image/dams.alderstar.1-0420232.0005/full/2500,/0/default.jpg',
        'Aldergrove Star, 17 September 1975, printed page 6: advertisement for BCDC business-management courses in Langley (lower lockup)',
        'Aldergrove Star, 17 September 1975', '1975-09-17',
        'Documented use by 17 September 1975, not its introduction; the designer is not known. The same lockup is in the Aldergrove Star and the Peninsula Times of 14 January 1976, and the emblem, under the full name, is on BCDC’s G.G. Moore Industrial Park sign at Chetwynd photographed in Action for Industry (1979, PDF page 22). The same advertisements also set the emblem small beside an all-capital sans-serif name.',
        'Four outlined prisms turned about a central gap, beside “British Columbia Development Corporation” on four lines of serif type — the corporation’s first known emblem, from its newspaper advertisements of 1975–76.',
        'A supplied vector reconstruction, not original artwork: one idealized three-face prism repeated through four quarter turns, then scaled vertically by 15/14 to the references, built as filled compound paths with transparent faces (no automatic tracing). The name is outlined Nimbus Roman fitted to the scans — an approximation, not an identification of the original typeface. Black, as printed in newspapers. The 1975 newspaper crop is kept as a download.',
        [('Download 1975 Aldergrove Star crop (PNG)', 'bcdc-prism-1975-aldergrove-star.png')],
        alsoSeen=[{"date": "1976-01-14", "source": "https://open.library.ubc.ca/collections/alderstar/items/1.0420388"},
                  {"date": "1976-01-14", "source": "https://open.library.ubc.ca/collections/xpentimes/items/1.0186178"},
                  {"date": "1979", "source": "https://publications.gc.ca/collections/collection_2024/isde-ised/re22/RE22-37-1979-eng.pdf#page=22"}],
        publisher='British Columbia Development Corporation; newspaper scan, UBC Library Open Collections'),
  cipo(460346, 'The Development Corporation — Serif name over four squares', 'serif-1980', 'trademark', '1980-10-22',
       'The specimen of a trademark filed on 22 October 1980 and registered on 25 June 1982 (TMA270427), claiming use in Canada since at least 31 March 1980 — the owner’s claim, not a verified first use. Cancelled by the owner on 3 November 1989, after BCDC’s assets had passed to BC Enterprise Corporation. Filed the same day as First Capital City’s mark (0460347).',
       '“The Development Corporation” in three lines of light serif capitals above four thin, square-cornered outlined squares: British Columbia Development Corporation’s second identity, registered as its trademark.'),
  cipo(494945, 'The Development Corporation — Four squares', 'symbol-1980', 'trademark', '1982-11-16',
       'The specimen of a trademark for the symbol alone (“Squares Design”), filed on 16 November 1982 and registered on 22 July 1983 (TMA281645), claiming use in Canada since at least 31 March 1980 — the owner’s claim, not a verified first use. Cancelled by the owner on 3 November 1989.',
       'The four thin, square-cornered outlined squares alone, as British Columbia Development Corporation registered them.'),
  cipo(901351, 'The Development Corporation — Bold name over four rounded squares', 'sans-1981', 'official mark', '1981-01-28',
       'The specimen of an official mark requested on 28 January 1981 and advertised on 17 June 1981 (Trade-marks Journal vol. 38, issue 1390); withdrawn on 13 December 1989. An official mark’s dates are its notice, not the design’s first use.',
       '“The Development Corporation” in heavy sans-serif capitals above four rounded, heavier outlined squares, adopted as an official mark by British Columbia Development Corporation.'),
  cipo(901352, 'The Development Corporation — Four rounded squares beside the name', 'horizontal-1981', 'official mark', '1981-03-16',
       'The specimen of an official mark requested on 16 March 1981 and advertised on 2 December 1981 (Trade-marks Journal issue 1414); withdrawn on 13 December 1989. An official mark’s dates are its notice, not the design’s first use.',
       'The rounded four squares to the left of “The Development Corporation” on three lines of heavy sans-serif capitals: the horizontal form of the official mark.'),
]
for a in assets:
    if a['verification']['embeddedImages'] or a['verification']['textElements'] or a['verification']['externalResources']:
        sys.exit('not pure vector: ' + a['id'])
reg = {
  "researchDate": "2026-11-14",
  "summary": "Supplied vector reconstructions of British Columbia Development Corporation’s two earlier identities, before the BC-and-flag mark it used in its 1984–86 annual reports: the four-prism emblem with its four-line name, rebuilt after newspaper advertisements of 1975–76 (source/prism), and the four-square “The Development Corporation” marks in the four arrangements it filed with the Canadian Intellectual Property Office in 1980–82 (source/four-square). Each package’s README is kept as source/*/package-README.md; review/ holds their comparison sheets. Not used: the prism symbol alone and the advertisement layout with the 1975 address (BCDC-symbol.svg and BCDC-historical-address.svg, kept in source/prism), because no source shows the symbol standing alone, and the address is a period advertisement, not part of the mark; and the packages’ white copies, which the gallery’s display copies make for the dark page.",
  "relationship": "The geometric resemblance between the prisms and the squares is suggestive, but no source yet says that one replaced the other, who designed either, or when. The 1985 annual report’s BC-and-flag mark is the Province’s, used by BCDC.",
  "openQuestions": [
    "Designer, commissioning date and any standards manual for either identity. Leads: BCDC annual reports 1976–82 (paper, Ivey Business Library, Western University); BCEC records schedule 170469 — 20000-20 (final branding), ARCS 306-20, 295-30, 400; accessions 93-4720 boxes 1–4 and 90-1769 box 24.",
    "A straight-on printed specimen of the prism emblem: the 1979 Chetwynd sign is photographed in perspective.",
    "BCDC’s full-page advertisement in The Economist’s Canada survey, 12 February 1977 (vol. 262, no. 6963), and its 1977 brochure Land for Industry, both cited by L. M. Thorn’s 1977 UBC thesis (printed pp. 98, 128)."
  ],
  "assets": assets
}
out = root / 'research/identity/bc-development-corporation-vector-2026-11-14/source-register.json'
out.write_text(json.dumps(reg, indent=2, ensure_ascii=False) + '\n')
print('ok', len(assets))
