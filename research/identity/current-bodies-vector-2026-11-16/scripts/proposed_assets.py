"""Write ../proposed-assets.json from the files in public/ (sha256, bytes and viewBox are read
from the files themselves, so the records match what is on disk).

    python -I research/identity/current-bodies-vector-2026-11-16/scripts/proposed_assets.py
"""
import hashlib, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(PKG)))
SEARCH = 'current-bodies-vector-2026-11-16'
OBSERVED = '2026-11-16'

PDF_FIDELITY = ('Official publication, original native vector paths extracted with PyMuPDF (page converted to SVG, '
                'text as glyph outlines); only the shapes inside the logo\'s box kept, in their source colours. '
                'Page photographs, neighbouring text and backgrounds removed. Not a supplied standalone master. '
                'No tracing, type recreation or recolouring.')


def rec(target, data_file, body, a, program=None):
    path = os.path.join(ROOT, 'public', a['file'])
    blob = open(path, 'rb').read()
    a['sha256'] = hashlib.sha256(blob).hexdigest()
    a['bytes'] = len(blob)
    if data_file == 'expandedIdentityData.js':
        a.setdefault('dimensions', {'viewBox': re.search(rb'viewBox="([^"]+)"', blob).group(1).decode()})
        a.setdefault('contentType', 'image/svg+xml')
    a['search'] = SEARCH
    out = {'targetAssetId': target, 'dataFile': data_file, 'bodyId': body}
    if program: out['program'] = program   # collectedData.js keeps BCeID under {"program": "bceid"}, not a body
    out['asset'] = a
    return out


def expanded(**k):
    base = dict(format='svg', isVector=True, supplied=False, reconstruction=False, sourceFile=None,
                observedDate=OBSERVED, dateNote='Publication, archive or observation date only; not a logo adoption date.',
                darkBackground=False)
    base.update(k)
    order = ['id', 'label', 'file', 'format', 'isVector', 'sourcePage', 'sourceUrl', 'resolvedSourceUrl', 'supplied',
             'reconstruction', 'publisher', 'sourceLocator', 'sourceFile', 'sourceDate', 'dateNote', 'observedDate',
             'evidenceType', 'notes', 'fidelityNote', 'darkBackground', 'specimenDate']
    return {key: base[key] for key in order if key in base} | {key: v for key, v in base.items() if key not in order}


records = [
    rec('source-expanded-bc-pension-corporation-website-logo', 'expandedIdentityData.js', 'bc-pension-corporation', expanded(
        id='source-expanded-bc-pension-corporation-wave-2-plan-colour',
        label='BC Pension Corporation — Logo, full colour, Wave 2 Strategic Plan',
        file='identity-expanded/bc-pension-corporation/wave-2-strategic-plan-2024-colour.svg',
        sourcePage='https://www.bcpensioncorp.ca/publications',
        sourceUrl='https://www.bcpensioncorp.ca/documents/1050273/5100587/Wave+2+Strategic+Plan.pdf/4f11ac1b-fbb0-f14b-85a6-6e635f51ba01?t=1712069307100',
        publisher='BC Pension Corporation',
        sourceLocator='Wave 2 Strategic Plan 2024–2027, PDF page 1 (cover), logo left of the Plan 20|30 mark',
        sourceDate='2024-03', specimenDate='2024-03',
        evidenceType='native-pdf-vector-extraction',
        notes='The dot arrow with “BC PENSION” in teal and “CORPORATION” in warm grey, as on the website logo. On the cover it sits beside a rule and the Plan 20|30 mark, which are left out.',
        fidelityNote=PDF_FIDELITY + ' Extracted component of a cover lockup.')),
    rec('source-expanded-etsi-bc-website-logo', 'expandedIdentityData.js', 'etsi-bc', expanded(
        id='source-expanded-etsi-bc-bylaws-2026-full-name-colour',
        label='Economic Trust of the Southern Interior — Full-name logo, colour',
        file='identity-expanded/etsi-bc/bylaws-2026-full-name-colour.svg',
        sourcePage='https://www.etsi-bc.ca/about/key-publications/',
        sourceUrl='https://www.etsi-bc.ca/wp-content/uploads/2026/07/ETSI-BC-Bylaw-and-Board-Policy-Manual-with-AI-and-Cybersecurity-2026.pdf',
        publisher='Economic Trust of the Southern Interior',
        sourceLocator='Bylaws and Board Policies (revised March 2026), PDF page 1 (cover)',
        sourceDate='2026-06', specimenDate='2026-06',
        evidenceType='native-pdf-vector-extraction',
        notes='“etsi BC” with the name “Economic Trust of the Southern Interior” set to its right: the full-name horizontal logo. The website file is the stacked short-name version; this is the same identity in its other official layout, not the same lockup.',
        fidelityNote=PDF_FIDELITY)),
    rec('source-expanded-etsi-bc-website-logo', 'expandedIdentityData.js', 'etsi-bc', expanded(
        id='source-expanded-etsi-bc-rac-terms-2024-full-name-reversed',
        label='Economic Trust of the Southern Interior — Full-name logo, reversed',
        file='identity-expanded/etsi-bc/rac-terms-2024-full-name-reversed.svg',
        sourcePage='https://www.etsi-bc.ca/about/key-publications/',
        sourceUrl='https://www.etsi-bc.ca/wp-content/uploads/2024/09/ETSI-BC-Columbia-Kootenay-RAC-Terms-of-Reference-Amended-2024_06_14.pdf',
        publisher='Economic Trust of the Southern Interior',
        sourceLocator='Columbia-Kootenay Regional Advisory Committee Terms of Reference (amended 2024-06-14), PDF page 1 (cover band)',
        sourceDate='2024-06-14 amendment; PDF 2024-09', specimenDate='2024-09',
        evidenceType='native-pdf-vector-extraction',
        notes='The full-name horizontal logo in white, from the blue cover band. Same lockup as the colour bylaws cover; white like the website’s reversed short-name file.',
        fidelityNote=PDF_FIDELITY, darkBackground=True)),
    rec('source-expanded-metro-vancouver-transit-police-website-logo', 'expandedIdentityData.js', 'metro-vancouver-transit-police', expanded(
        id='source-expanded-metro-vancouver-transit-police-community-report-2025-reversed',
        label='Metro Vancouver Transit Police — Crest and name, reversed',
        file='identity-expanded/metro-vancouver-transit-police/report-to-community-2025-reversed.svg',
        sourcePage='https://transitpolice.ca/',
        sourceUrl='https://transitpolice.ca/wp-content/uploads/_pda/2026/06/2025-Report-to-the-Community.pdf',
        publisher='Metro Vancouver Transit Police',
        sourceLocator='2025 Report to the Community, PDF page 1 (cover), lower right',
        sourceDate='2026-05', specimenDate='2026-05',
        evidenceType='native-pdf-vector-extraction',
        notes='The crest with “METRO VANCOUVER TRANSIT POLICE” beside it, all in white: the same lockup as the website’s Logo-White-Horiz.png.',
        fidelityNote=PDF_FIDELITY, darkBackground=True)),
    rec('source-expanded-e-comm-website-logo', 'expandedIdentityData.js', 'e-comm', expanded(
        id='source-expanded-e-comm-aspire-plan-2019-colour',
        label='E-Comm 9-1-1 — Logo with tagline, colour',
        file='identity-expanded/e-comm/aspire-strategic-plan-2019-colour.svg',
        sourcePage='https://www.ecomm911.ca/',
        sourceUrl='https://www.ecomm911.ca/wp-content/uploads/2019/05/EC_aSPIRE_Report.pdf',
        publisher='E-Comm 9-1-1',
        sourceLocator='(a)SPIRE 2023 Strategic Plan, PDF page 1 (cover), upper left',
        sourceDate='2019-04', specimenDate='2019-04',
        evidenceType='native-pdf-vector-extraction',
        notes='“E-Comm” in dark grey and “9-1-1” in red over “Helping to Save Lives and Protect Property”: the same design as the website logo. Later E-Comm reports (2021–2026) and Word documents carry the logo only as images.',
        fidelityNote=PDF_FIDELITY + ' A photograph behind the logo on the cover is not included.')),
    rec('source-expanded-liquor-distribution-branch-website-logo', 'expandedIdentityData.js', 'liquor-distribution-branch', expanded(
        id='source-expanded-liquor-distribution-branch-wholesale-site-lockup',
        label='BC Liquor Distribution Branch — B.C. logo and name lockup',
        file='identity-expanded/liquor-distribution-branch/ldb-wholesale-site-ldb-lockup.svg',
        sourcePage='https://wholesale.bcldb.com/',
        sourceUrl='https://wholesale.bcldb.com/themes/ldbwo/logo.svg',
        resolvedSourceUrl='https://wholesale.bcldb.com/themes/ldbwo/logo.svg',
        publisher='BC Liquor Distribution Branch',
        sourceLocator='LDB Wholesale Operations website logo (Adobe Illustrator SVG); right-hand part only',
        sourceDate='Undated web asset (server Last-Modified 2022-03-13) observed 2026-11-16',
        dateNote='The observation date and server modification date are not a logo adoption date.',
        evidenceType='official-website-vector',
        notes='The B.C. government logo, a vertical rule and “LIQUOR DISTRIBUTION BRANCH” in crimson: the LDB lockup used on bcldb.com. On the wholesale site it stands to the right of the red “LDB Wholesale Operations” banner, which is left out. Here the B.C. logo is black and the name #C60C46; the bcldb.com PNG shows a grey logo and a brighter red.',
        fidelityNote='Official SVG; the lockup’s own elements kept unchanged (same path data, attributes and colours), the banner elements removed and the viewBox fitted. Extracted component, not a standalone master. No tracing, type recreation or recolouring.')),
    rec('source-expanded-sub-vancouver-convention-centre-website-logo', 'expandedIdentityData.js', 'sub-vancouver-convention-centre', expanded(
        id='source-expanded-sub-vancouver-convention-centre-sustainability-toolkit-reversed',
        label='Vancouver Convention Centre — Logo, one colour reversed',
        file='identity-expanded/sub-vancouver-convention-centre/sustainability-toolkit-2026-reversed.svg',
        sourcePage='https://www.vancouverconventioncentre.com/about-us/sustainability',
        sourceUrl='https://assets.vancouverconventioncentre.com/28042026_sustainability_toolkit_final.pdf',
        publisher='Vancouver Convention Centre',
        sourceLocator='Sustainability Toolkit (last updated 2026-08-20), PDF page 16 (back cover), lower left',
        sourceDate='2026-08-20', specimenDate='2026-08-20',
        evidenceType='native-pdf-vector-extraction',
        notes='“VANCOUVER” with its splash and “CONVENTION CENTRE” in flat white. Same design as the website logo, whose letters carry a blue water photograph; this one-colour version has no photograph.',
        fidelityNote=PDF_FIDELITY, darkBackground=True)),
    rec('source-expanded-simon-fraser-university-website-logo', 'expandedIdentityData.js', 'simon-fraser-university', expanded(
        id='source-expanded-simon-fraser-university-powerpoint-horizontal-colour',
        label='Simon Fraser University — Horizontal logo, colour',
        file='identity-expanded/simon-fraser-university/powerpoint-template-horizontal-colour.svg',
        sourcePage='https://www.sfu.ca/communicators-toolkit/brand/templates/microsoft-office.html',
        sourceUrl='https://www.sfu.ca/content/dam/sfu/communicators-toolkit/brand/templates/microsoft-office/SFU-PowerPoint-Template-Arial.pptx',
        publisher='Simon Fraser University',
        sourceLocator='Official PowerPoint template, embedded file ppt/media/image4.svg (used by slide layout 2 and slide 8)',
        sourceDate='2025-04 (template modified 2025-04-03)', specimenDate='2025-04',
        evidenceType='official-website-vector',
        notes='The red SFU block with “SIMON FRASER UNIVERSITY” in grey to its right, as on the website logo. The SVG is the one SFU ships inside its brand PowerPoint template.',
        fidelityNote='Embedded SVG kept byte for byte (red #A6192E, grey #54585A). No tracing, type recreation or recolouring.')),
    rec('source-bc-infrastructure-benefits-bcib-mobile-png', 'collectedData.js', 'bc-infrastructure-benefits', {
        'id': 'vector-bcib-2026-short-reversed-source-vector',
        'label': 'BC Infrastructure Benefits — Helmet and BCIB, reversed, 2025/26 report',
        'file': 'identity-collected/bc-infrastructure-benefits/bcib-2026-short-reversed-source-vector.svg',
        'format': 'svg', 'isVector': True, 'supplied': False, 'reconstruction': False,
        'publisher': 'BC Infrastructure Benefits',
        'sourcePage': 'https://bcib.ca/',
        'sourceUrl': 'https://bcib.ca/wp-content/uploads/BCIB_Building-Opportunity-Here-report-F25-26.pdf',
        'sourceLocator': 'PDF page 1',
        'sourceFile': None, 'sourceDate': '2025/26 reporting period; PDF 2026-09',
        'dateNote': 'Publication/capture date or observation, not an adoption date.',
        'observedDate': OBSERVED, 'evidenceType': 'native-pdf-vector-extraction',
        'notes': 'The two-tone yellow helmet and white “BCIB”: the short form the website uses as its mobile logo. On the cover it is followed by “Building Opportunity Here” and the Respectful Onsite Initiative mark, which are left out.',
        'fidelityNote': 'Official publication, original native vector paths extracted; not a supplied standalone master. Helmet and letter paths kept with their source colours; the tagline, separator, neighbouring mark and cover photograph removed. Extracted component of the cover lockup. No tracing, type recreation, or recolouring.',
        'darkBackground': True}),
    rec('bceid-reversed', 'collectedData.js', None, {
        'id': 'bceid-reversed-rebuilt',
        'label': 'BCeID — Wordmark, reversed (rebuilt)',
        'file': 'identity-collected/bceid/bceid-reversed-rebuilt.svg',
        'format': 'svg', 'isVector': True, 'supplied': False, 'reconstruction': True,
        'publisher': 'Province of British Columbia (BCeID)',
        'sourcePage': 'https://www.bceid.ca/',
        'sourceUrl': 'https://www.bceid.ca/assets/images/bceid_rev@2x.png',
        'sourceLocator': 'Rebuilt over the website’s 2× reverse logo (220 × 58)',
        'sourceFile': None, 'sourceDate': None,
        'dateNote': 'Rebuilt in 2026 from an undated web image; no adoption date.',
        'observedDate': OBSERVED, 'evidenceType': 'vector-reconstruction',
        'notes': '“BCeID” in Garamond capitals with an italic e in gold, white for a dark ground, redrawn as outlines over the website image. No vector original was found: the website, its guides and forms carry the wordmark only as images.',
        'fidelityNote': 'Vector reconstruction. Letters set in EB Garamond (SIL Open Font License) and converted to outlines: capitals at weight 400, the e in EB Garamond Italic at weight 600. The original cut of Garamond is not verified. Each letter is scaled to its height in the source image and placed in its measured box; overlap with the source is 0.79 for the capitals and 0.65 for the e (IoU). Colours sampled from the image: white and #E3A82B. No live text, no embedded image.',
        'darkBackground': True}, program='bceid'),
    rec('source-expanded-compass-needle-symbol', 'expandedIdentityData.js', 'compass', expanded(
        id='rebuild-expanded-compass-needle-symbol',
        label='Compass — Needle symbol (rebuilt)',
        file='identity-expanded/compass/needle-symbol-rebuilt.svg',
        reconstruction=True,
        sourcePage='https://www.translink.ca/compasscard',
        sourceUrl='https://www.translink.ca/-/media/translink/icons/content-pages/handydart/compass_needle_upperright-arrow.png',
        publisher='TransLink',
        sourceLocator='Rebuilt over TransLink’s 561 × 561 needle-symbol PNG',
        sourceDate='Undated web asset observed 2026-11-15',
        dateNote='Rebuilt in 2026 from an undated web image; no adoption date.',
        evidenceType='vector-reconstruction',
        notes='The blue needle — a circle drawn to a point at the upper right — with a white C. No vector original was found on translink.ca, compasscard.ca or in TransLink PDFs checked.',
        fidelityNote='Vector reconstruction from geometry fitted to the 561 px PNG: the needle is one large circle joined by its tangents to a small rounded tip; the C is a ring cut by two horizontal lines (measured from the image). Overlap with the source: 0.998 for the needle, 0.987 for the C (IoU). Colours sampled: #0099CC, white. No tracing, no embedded image.')),
    rec('source-expanded-compass-website-logo', 'expandedIdentityData.js', 'compass', expanded(
        id='rebuild-expanded-compass-c-symbol',
        label='Compass — C symbol (rebuilt)',
        file='identity-expanded/compass/c-symbol-rebuilt.svg',
        reconstruction=True,
        sourcePage='https://www.compasscard.ca/',
        sourceUrl='https://www.compasscard.ca/images/sprite-s599e3523b9.png',
        publisher='TransLink',
        sourceLocator='Same geometry as the rebuilt needle symbol, coloured as the compasscard.ca sprite (81 × 80)',
        sourceDate='Undated source observed 2026-11-15',
        dateNote='Rebuilt in 2026 from undated web images; no adoption date.',
        evidenceType='vector-reconstruction',
        notes='White needle with a blue C, as the website sprite shows it. It is the same shape as the needle symbol with the colours swapped; checked against the 81 × 80 sprite crop.',
        fidelityNote='Vector reconstruction; geometry fitted to TransLink’s 561 px needle PNG (see the rebuilt needle symbol) and checked against the sprite crop: overlap 0.997 for the needle, 0.990 for the C (IoU). Colours sampled from the sprite: white, #009DDC. No tracing, no embedded image.')),
]
json.dump(records, open(os.path.join(PKG, 'proposed-assets.json'), 'w'), indent=2, ensure_ascii=False)
print(len(records), 'records')
