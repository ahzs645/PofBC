"""Local yellow-ribbon diagnostics using a scope fixed before revision 5 edits.

The photo is registered once outside this script. These masks are measurements
only; no contours, paths, or artwork are generated from image pixels.
"""
from pathlib import Path
import argparse
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent


def yellow(image, classifier, ratio):
    a = np.asarray(image.convert('RGB'), dtype=float)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return ((r > classifier['red_min']) & (g > classifier['green_min']) &
            (g >= r * ratio) & (b <= r * classifier['blue_red_ratio_max']))


def counts(reference, candidate):
    overlap = int((reference & candidate).sum())
    missing = int((reference & ~candidate).sum())
    extra = int((~reference & candidate).sum())
    union = overlap + missing + extra
    return {'iou_percent': round(100 * overlap / union, 4) if union else 100.,
            'precision_percent': round(100 * overlap / (overlap + extra), 4) if overlap + extra else 100.,
            'recall_percent': round(100 * overlap / (overlap + missing), 4) if overlap + missing else 100.,
            'overlap_pixels': overlap, 'missing_pixels': missing, 'extra_pixels': extra,
            'reference_pixels': overlap + missing, 'candidate_pixels': overlap + extra}


def domain(scope, region):
    width, height = scope['canvas']
    mask = Image.new('1', (width,height), 0)
    draw = ImageDraw.Draw(mask)
    if 'polygon' in region:
        draw.polygon([tuple(p) for p in region['polygon']], fill=1)
    else:
        draw.rectangle((0,0,width-1,height-1), fill=1)
    a=np.asarray(mask, dtype=bool).copy()
    border=scope.get('exclude_outer_canvas_pixels', 0)
    if border:
        a[:border]=False; a[-border:]=False
        a[:,:border]=False; a[:,-border:]=False
    return a


def analyze(reference, candidate, scope):
    result = {'canvas': scope['canvas'], 'registration': scope['registration'],
              'classifier': scope['primary_classifier'], 'regions': {}}
    for ratio in scope['sensitivity_green_red_ratio']:
        ref = yellow(reference, scope['primary_classifier'], ratio)
        cand = yellow(candidate, scope['primary_classifier'], ratio)
        for key, region in scope['regions'].items():
            x0, y0, x1, y1 = region['box']
            valid = domain(scope, region)[y0:y1,x0:x1]
            measured = counts(ref[y0:y1, x0:x1] & valid, cand[y0:y1, x0:x1] & valid)
            entry = result['regions'].setdefault(key, {'name': region['name'], 'box': region['box'], 'sensitivity': {}})
            entry['sensitivity'][str(ratio)] = measured
            if ratio == scope['primary_classifier']['green_red_ratio_min']:
                entry.update(measured)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate_path', type=Path, nargs='?')
    parser.add_argument('--candidate', type=Path)
    parser.add_argument('--reference', type=Path, default=ROOT / 'reference-rectified.png')
    parser.add_argument('--scope', type=Path, default=ROOT / 'v5_flames/regions_before_edits.json')
    parser.add_argument('--output', '--output-dir', dest='output', type=Path, required=True)
    parser.add_argument('--baseline', type=Path, help='Optional previous-delivery render for a three-column comparison sheet')
    parser.add_argument('--label', default='Candidate')
    args = parser.parse_args()
    args.candidate = args.candidate or args.candidate_path
    if args.candidate is None:
        parser.error('provide --candidate PATH or the positional candidate path')
    scope = json.loads(args.scope.read_text())
    size = tuple(scope['canvas'])
    reference = Image.open(args.reference).convert('RGB')
    if reference.size != size:
        raise ValueError('Reference must already use fixed registration')
    candidate = Image.open(args.candidate).convert('RGB')
    if candidate.size != size:
        candidate = candidate.resize(size, Image.Resampling.LANCZOS)
    args.output.mkdir(parents=True, exist_ok=True)
    result = analyze(reference, candidate, scope)
    result['reference_path'] = str(args.reference.resolve())
    result['candidate_path'] = str(args.candidate.resolve())
    result['baseline_path'] = str(args.baseline.resolve()) if args.baseline else None
    result['label'] = args.label
    result['scope_path'] = str(args.scope.resolve())
    result['measurement_domain_notes'] = scope.get('measurement_domain_notes', [])
    result['scope'] = scope
    (args.output / 'metrics.json').write_text(json.dumps(result, indent=2) + '\n')
    classifier = scope['primary_classifier']
    refmask = yellow(reference, classifier, classifier['green_red_ratio_min'])
    candmask = yellow(candidate, classifier, classifier['green_red_ratio_min'])
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
    except OSError:
        font = ImageFont.load_default()
    for key, region in scope['regions'].items():
        x0, y0, x1, y1 = region['context']
        scale = 3
        w, h = (x1-x0)*scale, (y1-y0)*scale
        panel = Image.new('RGB', (2*w+60, h+80), '#f6f3e9')
        draw = ImageDraw.Draw(panel)
        for image, title, x in [(reference, 'Reference', 20), (candidate, args.label, w+40)]:
            panel.paste(image.crop((x0,y0,x1,y1)).resize((w,h), Image.Resampling.NEAREST), (x,42))
            draw.text((x,9), title, font=font, fill='#242332')
            for sy in range(((y0+24)//25)*25, y1, 25):
                py=42+(sy-y0)*scale
                draw.line((x,py,x+w,py), fill='#ffffff60', width=1)
                draw.text((x+3,py+2), str(sy), font=font, fill='white', stroke_width=1, stroke_fill='#242332')
        draw.text((20,h+48), region['name'], font=font, fill='#242332')
        panel.save(args.output / f'{key}_color.png')
        bx0,by0,bx1,by1=region['box']
        valid=domain(scope,region)[by0:by1,bx0:bx1]
        rm=refmask[by0:by1,bx0:bx1] & valid
        cm=candmask[by0:by1,bx0:bx1] & valid
        diff=np.full((*rm.shape,3), (255,244,224), dtype=np.uint8)
        diff[~valid]=(213,213,213)
        diff[rm & cm]=(38,47,61)
        diff[rm & ~cm]=(0,160,195)
        diff[~rm & cm]=(212,54,121)
        Image.fromarray(diff).resize(((bx1-bx0)*4,(by1-by0)*4),Image.Resampling.NEAREST).save(args.output/f'{key}_difference.png')
    if args.baseline:
        baseline = Image.open(args.baseline).convert('RGB')
        if baseline.size != size:
            baseline = baseline.resize(size, Image.Resampling.LANCZOS)
        before = analyze(reference, baseline, scope)
        row_heights = [(r['context'][3]-r['context'][1])*3+94 for r in scope['regions'].values()]
        sheet = Image.new('RGB', (1350, sum(row_heights)+124), '#f6f3e9')
        draw = ImageDraw.Draw(sheet)
        title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 28)
        draw.text((24,18), 'Flame-edge ribbons: reference and constructed vector', font=title_font, fill='#242332')
        draw.text((24,58), 'Same fixed registration. Crop images at 3×. Local yellow-mask IoU uses the pre-edit scope.', font=font, fill='#4b4a4a')
        for x,label in [(24,'Reference photograph'),(466,'Previous delivery'),(908,args.label)]:
            draw.text((x,92), label, font=font, fill='#242332')
        y=124
        for (key,region),height in zip(scope['regions'].items(),row_heights):
            x0,y0,x1,y1=region['context']; w,h=(x1-x0)*3,(y1-y0)*3
            draw.text((24,y+8), region['name'], font=font, fill='#242332')
            for source,x in [(reference,24),(baseline,466),(candidate,908)]:
                sheet.paste(source.crop((x0,y0,x1,y1)).resize((w,h),Image.Resampling.NEAREST),(x,y+38))
            draw.text((24,y+h+44), f'Context x{x0}–{x1}, y{y0}–{y1}', font=font, fill='#4b4a4a')
            draw.text((466,y+h+44), f'Local yellow overlap: {before["regions"][key]["iou_percent"]:.2f}%',font=font,fill='#4b4a4a')
            draw.text((908,y+h+44), f'Local yellow overlap: {result["regions"][key]["iou_percent"]:.2f}%',font=font,fill='#4b4a4a')
            y+=height
        sheet.save(args.output/'flame_details_sheet.png')
    print(json.dumps({k: {f: v[f] for f in ('iou_percent','missing_pixels','extra_pixels')} for k,v in result['regions'].items()}, indent=2))


if __name__ == '__main__':
    main()
