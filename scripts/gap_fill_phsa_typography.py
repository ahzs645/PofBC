#!/usr/bin/env python3
"""Root's additive personal source typography checks and locked-peer comparison."""
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/gap-fill-2026-11-02'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pin(path):
    return {'path': str(path.relative_to(ROOT)), 'sha256': sha(path.read_bytes())}


def main():
    initial_path = BASE / 'reviews/phsa-2013-primary/initial-personal-source-reading-index.json'
    assert sha(initial_path.read_bytes()) == 'ae34d4cf0095077fc7fcb55a39fda96f99ddeaf0c3438437f2ec8065da4757c6'
    initial = json.loads(initial_path.read_bytes())
    packet_path = BASE / 'phsa_history/source-only-packets/phsa-2013-14-v4-adaptive-typography001/packet.json'
    packet = json.loads(packet_path.read_bytes())
    # All values below were personally read from the actual original crops.
    literal = {
        30: ['Aladi, Jude Ikechukwu', 91710, 250],
        182: ['Baribeau, Isabelle', 97486, 150],
        297: ['Birol, Inanc', 106954, 14294],
        459: ['Cablayan, Roemer R.I.', 91106, None],
        534: ['Chani, Inderpal', 99128, 1660],
        1014: ['Feldman, Irina', 114165, None],
        1136: ['Gagne, Isabelle', 137489, 3888],
        1189: ['Gfeller-Ingledew, Paris-Ann PA', 336048, 8366],
        1553: ['Inglis, Alison Adriana', 76071, 425],
        1555: ['Ingram, Melanie', 84232, None],
        1559: ['Ipsiroglu, Osman', 115527, 24986],
        1561: ['Irwin, Beverly J.', 99792, 1983],
        1723: ['Kennett-Bacon, Helen I.', 89035, None],
        1734: ['Keulen, Aissa Isabelle Kalaw', 75976, None],
        1848: ['Krishnaswamy, Wendy I', 92855, None],
        2348: ['McIlhargey, Allen', 88190, 148],
        2350: ['McIndoe, Sue', 90778, None],
        2351: ['McInnes, Kathryn Elaine', 101270, 293],
        2352: ['McIntosh, Gwyneth Irene', 90803, 1564],
        2353: ['McIntyre, Lorraine', 79931, 1905],
        2354: ['McIntyre, Vanessa C.', 92549, 2491],
        2440: ['Miller, Andrew I.', 113745, 1064],
        2460: ['Minchinton, Andrew I.', 147690, 12632],
        3047: ['Rodgers, Cathy I', 85487, 783],
        3054: ['Roe, Diane I.', 83749, None],
    }
    assert set(literal) == {t['sequence'] for t in packet['targets']}
    result_rows = []
    for target in packet['targets']:
        seq = target['sequence']
        path = ROOT / target['sourceCropPath']
        assert sha(path.read_bytes()) == target['sourceCropSha256']
        raster_path = Path('/workspace/gap-phsa-history-cache/images') / f'phsa-2013-14-p{target["physicalPage"]:03d}.png'
        assert sha(raster_path.read_bytes()) == target['wholeOriginalPageRasterSha256']
        expected = Image.open(raster_path).convert('RGB').crop(target['cropBoxOriginalPixels'])
        actual = Image.open(path).convert('RGB')
        assert actual.size == expected.size and actual.tobytes() == expected.tobytes()
        name, pay, expense = literal[seq]
        result_rows.append({'sequence': seq, 'pdfPage': target['physicalPage'], 'name': name,
                            'remuneration': pay, 'expenses': expense,
                            'sourceCropPath': target['sourceCropPath'],
                            'sourceCropSha256': target['sourceCropSha256']})
    for sheet in packet['contactSheets']:
        assert sha((ROOT / sheet['path']).read_bytes()) == sheet['sha256']
    initial_rows = {r['sequence']: r for r in initial['rows']}
    amendments = []
    for row in result_rows:
        seq = row['sequence']
        if seq in initial_rows:
            for field in ['name', 'remuneration', 'expenses']:
                if initial_rows[seq][field] != row[field]:
                    amendments.append({'sequence': seq, 'field': field,
                                       'first': initial_rows[seq][field], 'sourceReread': row[field]})
    assert not amendments
    final_rows = dict(initial_rows)
    final_rows.update({r['sequence']: r for r in result_rows})
    peer_path = BASE / 'municipal/reviews/phsa-history/phsa-2013-14-peer-final-source-readings.json'
    assert sha(peer_path.read_bytes()) == '63b87eb0b4f3e776f37155a7d95723f4fced28e3e87cf43a96c3d6c6fa441fe4'
    peer = {r['sequence']: r for r in json.loads(peer_path.read_bytes())['rows']}
    comparisons = []
    for seq in sorted(final_rows.keys() & peer.keys()):
        for field in ['name', 'remuneration', 'expenses']:
            if final_rows[seq][field] != peer[seq][field]:
                comparisons.append({'sequence': seq, 'field': field,
                                    'primary': final_rows[seq][field], 'peer': peer[seq][field]})
    result = {
        'key': 'phsa-2013-14', 'reviewer': 'root', 'candidateAware': True,
        'method': 'Root personally read every actual original crop in all three adaptive typography contact sheets, including ten same-source mixed-case calibration rows. Root also freshly rendered and personally inspected the seq2348 original name at600dpi. All25 additional source crops were pixel-replayed. This is candidate-aware primary confirmation, not a blind transcript or personal transcription of all3991rows.',
        'initialPersonalReadings': pin(initial_path), 'sourceOnlyAdaptivePacket': pin(packet_path),
        'contactSheetsPersonallyViewed': [1, 2, 3], 'rows': result_rows,
        'sameSourceTypographyQualification': 'The source uses mixed-case names. Uppercase I is selected in word-initial, internal McI and isolated-initial positions consistently with the actual source typography and ten same-source examples. In this sans-serif scan some uppercase-I/lowercase-l glyphs are visually identical; this conventional case rendering does not recover original Unicode, establish a person identity, or silently expand a name. Two actual vertical strokes after Mc are retained in McIlhargey; no extra dotted i is inserted. Monetary values and page citations are unaffected.',
        'fresh600dpiNameCrop': {'path': str((BASE / 'reviews/phsa-2013-primary/seq2348-name-original600dpi.png').relative_to(ROOT)),
                                'sha256': sha((BASE / 'reviews/phsa-2013-primary/seq2348-name-original600dpi.png').read_bytes()),
                                'physicalPage': 56, 'clipBoxPdfPoints': [48, 187.44, 180, 204.72]},
        'initialReadingAmendments': amendments,
        'lockedMunicipalPeerFinalReadings': pin(peer_path),
        'primaryAndPeerCommonRows': len(final_rows.keys() & peer.keys()),
        'primaryAndPeerFieldDisagreements': comparisons,
        'combinedPrimaryRows': [final_rows[s] for s in sorted(final_rows)],
        'noOutreach': True, 'reviewCode': pin(Path(__file__)),
    }
    path = BASE / 'reviews/phsa-2013-primary/additive-typography-source-review.json'
    assert not path.exists()
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'receipt': pin(path), 'primaryRows': len(final_rows), 'peerDisagreements': comparisons}))


if __name__ == '__main__':
    main()
