"""Extract the vector artwork inside one rectangle of one PDF page to a clean SVG.

    python -I pdfvec.py SOURCE.pdf PAGE x0 y0 x1 y1 OUT.svg [--drop-fill=#rrggbb,...] [--keep-bg]

Method (no tracing, no recolouring):
1. The page is copied into a scratch document, and everything outside the rectangle is removed with
   MuPDF redactions (text and images outside removed; any line art that touches the outside removed,
   which also drops page-size backgrounds and panels).
2. MuPDF converts the page to SVG with text as glyph outlines; the glyph <use> references are
   inlined as plain <path> elements so the file needs no fonts and no <use>.
3. Raster <image> elements are dropped (and reported). Optional --drop-fill removes leaf shapes of a
   given fill (e.g. a panel colour wholly inside the rectangle).
4. The viewBox is fitted to the rendered extent of what remains.
"""
import copy, re, subprocess, sys, json, hashlib, os, tempfile
import xml.etree.ElementTree as ET
import pymupdf

NS = 'http://www.w3.org/2000/svg'; XL = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', NS); ET.register_namespace('xlink', XL)
RENDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render.cjs')


TOK = re.compile(r'[MLCHVZQSTAmlchvzqsta]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?')


def parse_tf(t):
    """Compose an SVG transform attribute into a 6-tuple matrix."""
    m = (1, 0, 0, 1, 0, 0)
    for name, args in re.findall(r'(\w+)\s*\(([^)]*)\)', t or ''):
        v = [float(x) for x in re.findall(r'-?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', args)]
        if name == 'matrix': n = tuple(v)
        elif name == 'translate': n = (1, 0, 0, 1, v[0], v[1] if len(v) > 1 else 0)
        elif name == 'scale': n = (v[0], 0, 0, v[1] if len(v) > 1 else v[0], 0, 0)
        else: raise ValueError(name)
        m = mul(m, n)
    return m


def mul(m, n):
    a, b, c, d, e, f = m; A, B, C, D, E, F = n
    return (a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D, a * E + c * F + e, b * E + d * F + f)


def path_points(d):
    pts, cmd, x, y, nums = [], None, 0, 0, []
    toks = TOK.findall(d)
    i = 0
    def take(k):
        nonlocal i
        v = [float(t) for t in toks[i:i + k]]; i += k; return v
    while i < len(toks):
        t = toks[i]
        if t.isalpha(): cmd = t; i += 1
        if cmd in 'Zz': continue
        if cmd in 'ML': x, y = take(2); pts.append((x, y))
        elif cmd == 'H': x, = take(1); pts.append((x, y))
        elif cmd == 'V': y, = take(1); pts.append((x, y))
        elif cmd == 'C':
            v = take(6); pts += [(v[0], v[1]), (v[2], v[3]), (v[4], v[5])]; x, y = v[4], v[5]
        elif cmd == 'Q':
            v = take(4); pts += [(v[0], v[1]), (v[2], v[3])]; x, y = v[2], v[3]
        else: raise ValueError('path command ' + cmd)
    return pts


def leaf_bbox(el, parent):
    m = parse_tf(el.get('transform'))
    p = parent.get(el)
    while p is not None:
        m = mul(parse_tf(p.get('transform')), m); p = parent.get(p)
    pts = path_points(el.get('d', ''))
    if not pts: return None
    a, b, c, d, e, f = m
    tp = [(a * x + c * y + e, b * x + d * y + f) for x, y in pts]
    return pymupdf.Rect(min(p[0] for p in tp), min(p[1] for p in tp), max(p[0] for p in tp), max(p[1] for p in tp))


def extract(src, pageno, rect, out, drop_fills=(), pad=0.5, keep_bg=False):
    doc = pymupdf.open(src)
    doc.select([pageno - 1])
    page = doc[0]
    rect = pymupdf.Rect(rect)
    pr = page.rect
    outside = [pymupdf.Rect(pr.x0 - 5, pr.y0 - 5, pr.x1 + 5, rect.y0), pymupdf.Rect(pr.x0 - 5, rect.y1, pr.x1 + 5, pr.y1 + 5),
               pymupdf.Rect(pr.x0 - 5, rect.y0, rect.x0, rect.y1), pymupdf.Rect(rect.x1, rect.y0, pr.x1 + 5, rect.y1)]
    for r in outside:
        if not r.is_empty:
            page.add_redact_annot(r & pr if not (r & pr).is_empty else r)
    page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE,
                          graphics=(pymupdf.PDF_REDACT_LINE_ART_NONE if keep_bg else pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_TOUCHED),
                          text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    images_inside = [i['bbox'] for i in page.get_image_info()]
    svg = page.get_svg_image(text_as_path=True)
    root = ET.fromstring(svg)
    parent = {c: p for p in root.iter() for c in p}
    ids = {e.get('id'): e for e in root.iter() if e.get('id')}
    dropped_images = 0
    for img in list(root.iter(f'{{{NS}}}image')):
        parent[img].remove(img); dropped_images += 1
    # inline <use>
    for use in list(root.iter(f'{{{NS}}}use')):
        ref = (use.get(f'{{{XL}}}href') or use.get('href'))[1:]
        target = ids[ref]
        g = ET.Element(f'{{{NS}}}g')
        tr = []
        if use.get('transform'): tr.append(use.get('transform'))
        if use.get('x') or use.get('y'): tr.append(f"translate({use.get('x', '0')} {use.get('y', '0')})")
        if tr: g.set('transform', ' '.join(tr))
        for k, v in use.attrib.items():
            if k in ('transform', 'x', 'y', f'{{{XL}}}href', 'href') or k.startswith('data-'): continue
            g.set(k, v)
        kids = list(target) if target.tag in (f'{{{NS}}}symbol', f'{{{NS}}}g') else [target]
        for k in kids:
            c = copy.deepcopy(k); c.attrib.pop('id', None); g.append(c)
        p = parent[use]; p.insert(list(p).index(use), g); p.remove(use)
    # drop symbol defs no longer needed
    for defs in root.iter(f'{{{NS}}}defs'):
        for d in list(defs):
            if d.tag == f'{{{NS}}}symbol' or (d.get('id') or '').startswith('font_'):
                defs.remove(d)
    parent = {c: p for p in root.iter() for c in p}
    # keep only leaf shapes lying inside the rectangle (drops off-page and clipped-away leftovers)
    outside_leaves = 0
    for el in list(root.iter(f'{{{NS}}}path')):
        q, in_defs = parent.get(el), False
        while q is not None:
            in_defs |= q.tag in (f'{{{NS}}}defs', f'{{{NS}}}clipPath', f'{{{NS}}}mask', f'{{{NS}}}pattern'); q = parent.get(q)
        if el not in parent or in_defs:
            continue
        bb = leaf_bbox(el, parent)
        if bb is None or not (rect + (-0.5, -0.5, 0.5, 0.5)).contains(bb):
            parent[el].remove(el); outside_leaves += 1
    if drop_fills:
        for el in list(root.iter()):
            if el.tag == f'{{{NS}}}path' and (el.get('fill') or '').lower() in drop_fills and el in parent:
                parent[el].remove(el)
    # prune empty groups
    changed = True
    while changed:
        changed = False
        parent = {c: p for p in root.iter() for c in p}
        for el in list(root.iter(f'{{{NS}}}g')):
            if len(el) == 0 and el in parent:
                parent[el].remove(el); changed = True
    # drop unused defs
    body = ET.tostring(root, encoding='unicode')
    for defs in list(root.iter(f'{{{NS}}}defs')):
        for d in list(defs):
            i = d.get('id')
            if i and body.count(f'#{i})') == 0 and body.count(f'"#{i}"') == 0:
                defs.remove(d)
    for defs in list(root.findall(f'{{{NS}}}defs')):
        if len(defs) == 0: root.remove(defs)
    # fit viewBox by rendering
    W, H = pr.width, pr.height
    root.set('viewBox', f'0 0 {W} {H}'); root.set('width', str(W)); root.set('height', str(H))
    tmp = tempfile.mkdtemp()
    open(f'{tmp}/a.svg', 'wb').write(ET.tostring(root))
    scale = 8
    subprocess.run(['node', RENDER, f'{tmp}/a.svg', f'{tmp}/a.png', str(int(W * scale))], check=True)
    from PIL import Image
    im = Image.open(f'{tmp}/a.png'); bb = im.getchannel('A').getbbox()
    k = im.width / W
    x0, y0, x1, y1 = bb[0] / k - pad, bb[1] / k - pad, bb[2] / k + pad, bb[3] / k + pad
    f = lambda v: f'{v:.3f}'.rstrip('0').rstrip('.')
    root.set('viewBox', f'{f(x0)} {f(y0)} {f(x1 - x0)} {f(y1 - y0)}')
    root.set('width', f(x1 - x0)); root.set('height', f(y1 - y0))
    data = ET.tostring(root, encoding='unicode')
    data = re.sub(r'>\s+<', '><', data)
    data = '<?xml version="1.0" encoding="UTF-8"?>\n' + data + '\n'
    open(out, 'w').write(data)
    s = ET.fromstring(data)
    info = dict(out=out, source=src, sourceSha256=hashlib.sha256(open(src, 'rb').read()).hexdigest(), page=pageno,
                rect=list(rect), viewBox=root.get('viewBox'), paths=len(s.findall(f'.//{{{NS}}}path')),
                images=len(s.findall(f'.//{{{NS}}}image')), texts=len(s.findall(f'.//{{{NS}}}text')),
                uses=len(s.findall(f'.//{{{NS}}}use')), droppedImages=dropped_images, droppedOutsideLeaves=outside_leaves, imagesInRect=[list(map(round, b)) for b in images_inside],
                fills=sorted(set(re.findall(r'fill="(#[0-9a-fA-F]{6})"', data))), bytes=len(data.encode()), sha256=hashlib.sha256(data.encode()).hexdigest())
    return info


if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    opts = dict(x[2:].split('=', 1) if '=' in x else (x[2:], '1') for x in sys.argv[1:] if x.startswith('--'))
    drops = tuple(opts.get('drop-fill', '').lower().split(',')) if opts.get('drop-fill') else ()
    print(json.dumps(extract(a[0], int(a[1]), tuple(map(float, a[2:6])), a[6], drops, keep_bg='keep-bg' in opts), indent=1))
