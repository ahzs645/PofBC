"""Reproduce fixed-scope footer diagnostics from arbitrary artifact paths.

This is a local ivory/negative-space comparison, separate from the poster's
fixed tree-ink analysis. It does not optimize registration or create geometry.
"""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi


def load_image(path, canvas):
    image = Image.open(path).convert('RGB')
    if image.size != tuple(canvas):
        image = image.resize(tuple(canvas), Image.Resampling.LANCZOS)
    return image


def classify(image, scope, ivory_b=None):
    a = np.asarray(image).astype(int)
    ivory = scope['classifiers']['ivory']
    b = ivory['b_min_exclusive'] if ivory_b is None else ivory_b
    return {
        'ivory': (a[:, :, 0] > ivory['r_min_exclusive'])
        & (a[:, :, 1] > ivory['g_min_exclusive'])
        & (a[:, :, 2] > b)
        & ((a.max(2) - a.min(2)) < ivory['chroma_max_exclusive']),
        'dark': a.max(2) < scope['classifiers']['dark']['max_channel_exclusive'],
    }


def metrics(reference, candidate):
    shared = int((reference & candidate).sum())
    missing = int((reference & ~candidate).sum())
    extra = int((candidate & ~reference).sum())
    union = shared + missing + extra
    ea = reference ^ ndi.binary_erosion(reference)
    eb = candidate ^ ndi.binary_erosion(candidate)
    distance = None
    if ea.any() and eb.any():
        da = ndi.distance_transform_edt(~ea)
        db = ndi.distance_transform_edt(~eb)
        distance = float((db[ea].mean() + da[eb].mean()) / 2)
    return {
        'iou': float(shared / union) if union else 1.0,
        'shared_px': shared,
        'missing_px': missing,
        'extra_px': extra,
        'mean_symmetric_boundary_px': distance,
    }


def review_font():
    try:
        return ImageFont.truetype('DejaVuSans.ttf', 18)
    except OSError:
        return ImageFont.load_default()


def analyze(reference_path, candidate_path, scope_path, output_dir, baseline_path=None, label='Candidate'):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    scope = json.loads(Path(scope_path).read_text())
    reference = load_image(reference_path, scope['canvas'])
    candidate = load_image(candidate_path, scope['canvas'])
    baseline = load_image(baseline_path, scope['canvas']) if baseline_path else None
    rm, cm = classify(reference, scope), classify(candidate, scope)
    bm = classify(baseline, scope) if baseline is not None else None
    result = {
        'diagnostic': scope['diagnostic'],
        'reference': str(Path(reference_path).resolve()),
        'candidate': str(Path(candidate_path).resolve()),
        'baseline': str(Path(baseline_path).resolve()) if baseline_path else None,
        'label': label,
        'scope': scope,
        'regions': {},
    }
    for name, region in scope['regions'].items():
        x0, y0, x1, y1 = region['box']
        sl = np.s_[y0:y1, x0:x1]
        row = {'definition': region}
        for material in ['ivory', 'dark']:
            row[material] = {'candidate': metrics(rm[material][sl], cm[material][sl])}
            if bm is not None:
                row[material]['baseline'] = metrics(rm[material][sl], bm[material][sl])
        row['ivory_sensitivity'] = {
            str(t): metrics(classify(reference, scope, t)['ivory'][sl],
                            classify(candidate, scope, t)['ivory'][sl])['iou']
            for t in scope['ivory_sensitivity_b']
        }
        result['regions'][name] = row
        columns = [(reference, 'Reference')]
        if baseline is not None:
            columns.append((baseline, 'Frozen baseline'))
        columns.append((candidate, label))
        scale = 1.6
        w, h = round((x1-x0)*scale), round((y1-y0)*scale)
        sheet = Image.new('RGB', (len(columns)*w+(len(columns)+1)*12, h+60), (246,243,233))
        draw, font = ImageDraw.Draw(sheet), review_font()
        for i, (image, title) in enumerate(columns):
            x = 12+i*(w+12)
            sheet.paste(image.crop((x0,y0,x1,y1)).resize((w,h), Image.Resampling.LANCZOS), (x,46))
            draw.text((x,10), title, font=font, fill=(30,30,40))
        sheet.save(output_dir/f'{name}_natural.png')
        difference = np.full((y1-y0,x1-x0,3), (246,243,233), np.uint8)
        a,b = rm['ivory'][sl],cm['ivory'][sl]
        difference[a&b] = (36,35,50)
        difference[a&~b] = (0,166,190)
        difference[b&~a] = (219,52,124)
        Image.fromarray(difference).resize((w,h), Image.Resampling.NEAREST).save(output_dir/f'{name}_ivory_difference.png')
    (output_dir/'metrics.json').write_text(json.dumps(result,indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--scope', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--label', default='Candidate')
    args = parser.parse_args()
    result = analyze(args.reference, args.candidate, args.scope, args.output_dir, args.baseline, args.label)
    for name,row in result['regions'].items():
        print(name, {kind:round(row[kind]['candidate']['iou']*100,3) for kind in ['ivory','dark']})


if __name__ == '__main__':
    main()
