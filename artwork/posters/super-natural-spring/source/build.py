#!/usr/bin/env python3
"""Build the three Super, Natural BC studies from unmodified scene files and native type.
Run from any directory; --exports needs Inkscape and Pillow. Outlined masters need
no installed font. Editable text requires TeX Gyre Termes. The historic font is
unconfirmed. No lettering or photography is traced.
"""
from __future__ import annotations
import argparse, base64, hashlib, html, json, shutil, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
POSTERS=HERE.parent.parent
ROOT=POSTERS.parent.parent
TYPE=json.loads((HERE/'type-glyphs.json').read_text())
ITALIC=json.loads((HERE/'type-glyphs-italic.json').read_text())
KEYS={'spring':'super-natural-spring','ferries':'super-natural-ferries','lake':'super-natural-lake'}
def n(v): return f'{v:.6f}'.rstrip('0').rstrip('.') or '0'
def esc(v): return html.escape(str(v),quote=True)
def image_url(p):
    mime='image/png' if p.suffix.lower()=='.png' else 'image/jpeg'
    return f'data:{mime};base64,'+base64.b64encode(p.read_bytes()).decode('ascii')
def run(text,x,baseline,width,size,tracking=0,fill=None,italic=False,outline=True,id=None,optical=None,**unused):
    table=ITALIC if italic else TYPE
    glyphs,kern=table['glyphs'],table['kerning']; pos=[]; cursor=0; left=float('inf');right=float('-inf')
    for i,ch in enumerate(text):
        if ch not in glyphs: raise ValueError(f'Unknown glyph {ch!r} in {text!r}')
        if i: cursor+=kern.get(text[i-1:i+1],0)+(optical or {}).get(text[i-1:i+1],0)
        g=glyphs[ch];pos.append(cursor)
        if 'box' in g:left=min(left,cursor+g['box'][0]);right=max(right,cursor+g['box'][2])
        cursor+=g['w']+tracking
    sx,sy=width/(right-left),size/1000
    attrs=f' data-text="{esc(text)}" transform="matrix({n(sx)} 0 0 {n(sy)} {n(x-left*sx)} {n(baseline)})"'
    if fill:attrs+=f' fill="{fill}"'
    if id:attrs+=f' id="{id}"'
    if outline:
        letters=''.join(f'<path data-letter="{esc(ch)}" transform="translate({n(p)} 0)" d="{glyphs[ch]["d"]}"/>' for ch,p in zip(text,pos) if 'd' in glyphs[ch])
    else:
        letters=f'<text x="{" ".join(n(p) for p in pos)}" y="0" font-family="TeX Gyre Termes" font-size="1000" font-style="{"italic" if italic else "normal"}" font-kerning="none" xml:space="preserve">{esc(text)}</text>'
    return f'<g{attrs}>{letters}</g>'
def fitted_letters(rows,prefix,outline=True):
    parts=[]
    for i,row in enumerate(rows):
        ch,(x,y,w,h)=row['char'],row['box'];g=TYPE['glyphs'][ch];l,t,r,b=g['box'];sx,sy=w/(r-l),h/(b-t)
        attrs=f'id="{prefix}-letter-{i:03d}" data-letter="{esc(ch)}" transform="matrix({n(sx)} 0 0 {n(sy)} {n(x-l*sx)} {n(y-t*sy)})"'
        if outline:parts.append(f'<path {attrs} d="{g["d"]}"/>')
        else:parts.append(f'<text {attrs} x="0" y="0" font-family="TeX Gyre Termes" font-size="1000">{esc(ch)}</text>')
    return ''.join(parts)
def document(d,package,outline=True,text_only=False,variant=None,gallery=False):
    w,h,top=d['canvas']['width'],d['canvas']['height'],d['canvas']['photoTop'];prefix=d['prefix'];photos=d['photos']
    if variant:photos=[p for p in photos if p['id']==variant]
    elif not gallery:photos=photos[:1]
    meta={k:d[k] for k in ['title','date','credits','sources','uncertainties','reconstruction']}
    meta.update({'kind':'Mixed-media reconstruction: native lettering and raster scene','font':'TeX Gyre Termes; historical font unconfirmed','referenceFraming':d['referenceNote'],'exportSizeInches':[w/100,h/100],'exportSizeNote':'Working size; original printed dimensions unestablished','photoFiles':[p['file'] for p in photos]})
    parts=['<?xml version="1.0" encoding="UTF-8"?>',f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{n(w/100)}in" height="{n(h/100)}in" role="img" aria-labelledby="{prefix}-title {prefix}-description">',f'<title id="{prefix}-title">{esc(d["title"])}</title>',f'<desc id="{prefix}-description">{esc(d["reconstruction"])}</desc>','<metadata>'+esc(json.dumps(meta,ensure_ascii=False))+'</metadata>',f'<defs><clipPath id="{prefix}-photo-window"><rect x="0" y="{top}" width="{w}" height="{h-top}"/></clipPath></defs>']
    if not text_only:
        parts.append(f'<g id="{prefix}-paper"><rect width="{w}" height="{h}" fill="#fbfaf7"/></g>')
        for i,p in enumerate(photos):
            hidden=' display="none"' if i else '';x,y,pw,ph=p['box']
            parts.append(f'<g id="{p["id"]}" clip-path="url(#{prefix}-photo-window)"{hidden}><image x="{n(x)}" y="{n(y)}" width="{n(pw)}" height="{n(ph)}" preserveAspectRatio="{p.get("preserveAspectRatio","xMidYMid slice")}" xlink:href="{image_url(package/p["file"])}"/></g>')
    parts.append(f'<g id="{prefix}-copy" fill="#453b35" aria-label="Travel information">')
    for row in d['copy']:parts.append(run(**row,outline=outline))
    parts.append(run(**d['credit'],outline=outline,italic=True))
    if not text_only and d.get('facsimile'):
        f=d['facsimile'];x,y,fw,fh=f['box']
        parts.append(f'<image id="{prefix}-reply-code-facsimile" x="{x}" y="{y}" width="{fw}" height="{fh}" xlink:href="{image_url(package/f["file"])}"><title>Unresolved reply code from the prior source; not an asserted transcription</title></image>')
    parts.append('</g>');parts.append(f'<g id="{prefix}-wordmark" fill="#332e2b" aria-label="Campaign signature">')
    for row in d['wordmark']:parts.append(run(**row,outline=outline))
    parts.append('</g>');parts.append(f'<g id="{prefix}-headline" fill="#fffdfa" data-text="{esc(d["title"])}">')
    for i,row in enumerate(d['headline']['lines']):
        if 'letters' in row:parts.append(f'<g data-text="{esc(row["text"])}">'+fitted_letters(row['letters'],f'{prefix}-{i}',outline)+'</g>')
        else:parts.append(run(**row,outline=outline,id=f'{prefix}-headline-line-{i+1}'))
    parts.append('</g></svg>');return '\n'.join(parts)+'\n'
def render(source,output,width=None):
    args=['inkscape',str(source),'--export-filename='+str(output)]
    if width:args.append('--export-width='+str(width))
    subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
def build(key,exports=False):
    package=POSTERS/KEYS[key];d=json.loads((package/'source/design.json').read_text());review=package/'review';review.mkdir(exist_ok=True)
    site=ROOT/'src/posters'/KEYS[key];site.mkdir(parents=True,exist_ok=True);stem=d['stem']
    (site/('spring-visitors.svg' if key=='spring' else 'poster.svg')).write_text(document(d,package,gallery=True))
    master=package/(stem+'.svg');master.write_text(document(d,package))
    (package/(stem+'-editable-text.svg')).write_text(document(d,package,outline=False))
    (review/'typography.svg').write_text(document(d,package,text_only=True))
    if len(d['photos'])>1:
        (package/(stem+'-alternate.svg')).write_text(document(d,package,variant=d['photos'][1]['id']))
        (package/(stem+'-alternate-editable-text.svg')).write_text(document(d,package,variant=d['photos'][1]['id'],outline=False))
    if exports:
        from PIL import Image
        render(master,package/(stem+'.pdf'));render(master,review/'reconstruction.png',d['canvas']['width']);render(review/'typography.svg',review/'typography.png',d['canvas']['width'])
        if len(d['photos'])>1:render(package/(stem+'-alternate.svg'),package/(stem+'-alternate.pdf'))
        im=Image.open(review/'reconstruction.png').convert('RGB');im.thumbnail((900,900));im.save(site/'thumbnail.jpg',quality=92)
    record={'id':KEYS[key],'title':d['title'],'viewBox':[0,0,d['canvas']['width'],d['canvas']['height']],'master':str(master.relative_to(ROOT)),'sha256':hashlib.sha256(master.read_bytes()).hexdigest(),'typography':'Native TeX Gyre Termes glyph outlines; original historical typeface unconfirmed','photos':[{'file':p['file'],'sha256':hashlib.sha256((package/p['file']).read_bytes()).hexdigest()} for p in d['photos']]}
    (package/'manifest.json').write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n');print('Built',KEYS[key])
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--only',choices=KEYS);ap.add_argument('--exports',action='store_true');ap.add_argument('--proof',action='store_true',help='Compatibility flag; typography proofs are always written');args=ap.parse_args()
    if args.exports and not shutil.which('inkscape'):raise SystemExit('Inkscape is needed for --exports')
    for key in ([args.only] if args.only else KEYS):build(key,args.exports)
