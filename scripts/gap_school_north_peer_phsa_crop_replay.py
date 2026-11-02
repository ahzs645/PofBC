"""Verify source-only PHSA peer crop pixels against byte-pinned originals."""
from pathlib import Path
import argparse
import hashlib
import json

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'research/salaries/gap-fill-2026-11-02/school_north/reviews/phsa-history'
AREA = ROOT / 'research/salaries/gap-fill-2026-11-02/phsa_history'
CACHE = Path('/workspace/gap-phsa-history-cache/images')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--adaptive2012', action='store_true')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    packets = [AREA / 'source-only-packets' / (key + suffix) / 'packet.json'
               for key, suffix in [('phsa-2011-12', '-v4'), ('phsa-2012-13', '-v4'), ('phsa-2011-12', '-v4-adaptive-v1')]]
    if args.adaptive2012:
        packets = [AREA / 'source-only-packets/phsa-2012-13-v4-adaptive-v1/packet.json']
    out = []
    for path in packets:
        packet = json.loads(path.read_text())
        prior_page = None
        original = None
        count = 0
        for target in packet['targets']:
            page = target['physicalPage']
            if page != prior_page:
                raster = CACHE / f'{packet["key"]}-p{page:03d}.png'
                assert sha(raster) == target['wholeOriginalPageRasterSha256']
                original = Image.open(raster).convert('RGB')
                prior_page = page
            crop = ROOT / target['sourceCropPath']
            assert sha(crop) == target['sourceCropSha256']
            literal = Image.open(crop).convert('RGB')
            expected = original.crop(target['cropBoxOriginalPixels'])
            assert literal.size == expected.size and literal.tobytes() == expected.tobytes()
            count += 1
        for sheet in packet['contactSheets']:
            assert sha(ROOT / sheet['path']) == sheet['sha256']
        out.append(dict(packetPath=str(path.relative_to(ROOT)), packetSha256=sha(path), exactSourceCrops=count,
                        contactSheetsByteHashesExact=len(packet['contactSheets'])))
    margin = AREA / 'expanded-source-row-margin-review/source-only-packet.json'
    packet = json.loads(margin.read_text())
    expanded = []
    for target in packet['targets']:
        if target['key'] != 'phsa-2012-13':
            continue
        raster = CACHE / f'{target["key"]}-p{target["physicalPage"]:03d}.png'
        assert sha(raster) == target['wholeOriginalPageRasterSha256']
        crop = ROOT / target['expandedSourceCropPath']
        assert sha(crop) == target['expandedSourceCropSha256']
        expected = Image.open(raster).convert('RGB').crop(target['expandedIntegerBox'])
        actual = Image.open(crop).convert('RGB')
        assert expected.size == actual.size and expected.tobytes() == actual.tobytes()
        expanded.append(dict(sequence=target['sequence'], physicalPage=target['physicalPage'],
                             path=target['expandedSourceCropPath'], sha256=target['expandedSourceCropSha256']))
    destination = BASE / ('source-only-adaptive2012-crop-pixel-replay.json' if args.adaptive2012 else 'source-only-crop-pixel-replay.json')
    result = dict(packets=out, expanded2012FullWidthCrops=expanded,
                  originalWholePageRasterReplay='two-source-raw-readers-and-original-raster-replay.json',
                  croppedNameMarginQualification='Original narrow crops retained; expanded original full-width rows2802/3329/3330 personally read separately. No clipped characters inferred.',
                  noOutreach=True)
    if args.check:
        assert json.loads(destination.read_text()) == result
    else:
        assert not destination.exists()
        destination.write_text(json.dumps(result, indent=2) + '\n')
    print(sha(destination))


if __name__ == '__main__':
    main()
