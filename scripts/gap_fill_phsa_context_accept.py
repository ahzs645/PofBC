#!/usr/bin/env python3
"""Record root's personal nine-original PHSA period/definition/control review."""
import hashlib
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/gap-fill-2026-11-02'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def main():
    replay_path = BASE / 'reviews/phsa-context-root/original-context-pixel-replay.json'
    assert sha(replay_path.read_bytes()) == 'd221e1b8562fa07cd5ad1fdf3bf0a59c7a20e6b660ff948c427b941dc92ce6eb'
    replay = json.loads(replay_path.read_bytes())
    inventory_path = ROOT / replay['sourceInventory']['path']
    assert sha(inventory_path.read_bytes()) == replay['sourceInventory']['sha256']
    sources = {s['key']: s for s in json.loads(inventory_path.read_bytes())['sources']}
    # Personally read from the original page images, not filled from OCR totals.
    facts = {
        'phsa-2006-07': [41, 151608222, 4448009, 1280],
        'phsa-2007-08': [33, 154793761, 4014218, 1271],
        'phsa-2008-09': [47, 185412331, 5289671, 1544],
        'phsa-2009-10': [53, 217818830, 4433493, None],
        'phsa-2010-11': [52, 237473281, 5486042, 2004],
        'phsa-2011-12': [90, 369888459, 8500874, 3423],
        'phsa-2012-13': [86, 369114727, 8792836, 3351],
        'phsa-2013-14': [93, 425632576, 8642235, 3991],
        'phsa-2014-15': [106, 438199947, 9051748, 4145],
    }
    index = json.loads((BASE / 'phsa_history/context-image-inventory.json').read_bytes())
    records = []
    for key, (page, pay, expense, count) in facts.items():
        source = sources[key]
        definition = next(r for r in index if r['key'] == key and r['physicalPage'] == 2)
        header = next(r for r in replay['firstSalaryHeaderSourceStrips'] if r['key'] == key and 'cropBoxOriginalPixels' in r)
        if key == 'phsa-2012-13':
            control = next(r for r in replay['firstSalaryHeaderSourceStrips'] if r['key'] == key and r.get('physicalPage') == 86)
        else:
            control = next(r for r in index if r['key'] == key and r['physicalPage'] == page)
        for reference in [definition, header, control]:
            assert sha((ROOT / reference['path']).read_bytes()) == reference['sha256']
        start = int(key[5:9])
        records.append({'key': key, 'sourceSha256': source['sourceSha256'],
                        'periodEnd': f'{start + 1}-03-31',
                        'periodStart': f'{start}-04-01',
                        'periodStartAssumption': 'Conventional twelve-month fiscal start before the internally printed March31 year-end.',
                        'definitionPagePersonallyViewed': definition,
                        'firstSalaryHeaderPersonallyViewed': header,
                        'lastSalaryControlPagePersonallyViewed': control,
                        'printedNamedControls': {'remuneration': pay, 'expenses': expense},
                        'controlPhysicalPage': page, 'printedEmployeeNarrativeCount': count,
                        'conflictingNarrativeCount': 1800 if key == 'phsa-2009-10' else None,
                        'conflictingNarrativeCountPeriodEnd': '2009-03-31' if key == 'phsa-2009-10' else None})
    footnote = BASE / 'phsa_history/context-images/phsa-2008-09-p11-130.png'
    source = sources['phsa-2008-09']
    source_path = Path(source['cachePath'])
    assert sha(source_path.read_bytes()) == source['sourceSha256']
    # The producer filename rounds the resolution to130; its actual scale is
    #1.8 pixels/point (129.6dpi). Replay the actual geometry, not the filename.
    assert fitz.open(source_path)[10].get_pixmap(matrix=fitz.Matrix(1.8, 1.8), alpha=False).tobytes('png') == footnote.read_bytes()
    result = {
        'acceptedContextScope': True, 'acceptsNormalizedRows': False,
        'approvedBy': 'root', 'noOutreach': True,
        'originalContextPixelReplay': pin(replay_path), 'sourceInventory': pin(inventory_path),
        'sources': records,
        'personalScope': 'Root personally viewed all nine actual definition pages, nine first-salary-page header strips, nine actual final salary/control pages (2012/13 physical86), and the2008/09 physical11 footnote. All36 archived whole original context PNGs were separately reproduced byte-exact. This accepts source periods, column definitions and literal controls only; the complete row selections require their separate primary and independent reviews.',
        'sharedDefinitions': {
            'threshold': 75000, 'thresholdComparison': 'exceeding as stated; retain actual printed observations',
            'remuneration': 'Money physically received by or paid on behalf of the employee, including salaries/wages, taxable benefits, bonuses, stipends, MOCAP and sessional fees; not an annual base salary rate.',
            'expenses': 'Separate disclosed expenses paid during the period, reimbursed directly and/or paid to third-party suppliers; never added to remuneration.',
            'scope': 'Named threshold payment disclosures, not a complete employee roster.',
        },
        'sourceQualifications': [
            '2006/07 narrative count1280 differs from both complete named-table censuses1267; no missing employee or payment is invented.',
            '2009/10 is assigned to the repeated actual salary-table year-end March31,2010. Its definition page heading and opening paragraph also say2010, but its physical-payment definition and employee-count narrative say2009. Both statements are retained, with no assumed cause. The1800count in that2009paragraph is not adopted as a2010control just because1800table observations were recovered.',
            'Other internally printed year-ends and narrative counts are transcribed literally. Monetary controls and individual rows remain separate evidence; matching a control alone does not prove transcription accuracy.',
            'All blank/dash expenses stay unknown and explicit zero stays zero. No source total authorizes balancing individual cells.',
            'Physical page1 is an added Library catalogue cover in each delivered copy; page citations refer to the exact downloaded PDF. Stored-bitstream and delivered-byte fingerprints differ; this review does not establish a cause or byte identity.',
        ],
        'cranstonFootnotePersonallyViewed': {**pin(footnote), 'physicalPage': 11, 'actualDpi': 129.6,
            'literalName': 'Cranston,Lynda', 'remuneration': 408452, 'expenses': 50569,
            'sourceFootnoteMarker': '*',
            'meaning': 'The source explains higher08/09expenses by professional-development courses and travel associated with Chair duties for health-care-related organizations. The marker is preserved as a footnote, separate from the name; it does not turn expenses into pay.'},
        'reviewCode': pin(Path(__file__)),
    }
    path = BASE / 'reviews/phsa-context-root/root-nine-source-context-acceptance.json'
    assert not path.exists()
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': pin(path), 'sources': len(records)}))


if __name__ == '__main__':
    main()
