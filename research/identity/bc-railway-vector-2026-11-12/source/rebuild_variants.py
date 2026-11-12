#!/usr/bin/env python3
"""Rebuild the main and letterhead SVGs. Python 3 standard library only."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent

def svg(variant):
    w, h = variant['canvas']
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:g}" height="{h:g}" viewBox="0 0 {w:g} {h:g}" role="img" aria-labelledby="title description">',
        f'<title id="title">{escape(variant["title"])}</title>',
        f'<desc id="description">{escape(variant["description"])}</desc>',
        '<metadata>' + escape(json.dumps({'font':variant['font'],'source':variant['source'],'method':variant['method']},ensure_ascii=False)) + '</metadata>']
    for row,word in enumerate(variant['words']):
        lines.append(f'<g id="line-{row+1}-{word.lower()}" aria-label="{word}">')
        for g in [g for g in variant['letters'] if g['row']==row]:
            lines.append(f'<path id="line-{row+1}-letter-{g["index"]+1}-{g["char"]}" aria-label="{g["char"]}" fill="{g["fill"]}" d="{g["path"]}"/>')
        lines.append('</g>')
    lines.append('</svg>')
    return '\n'.join(lines)+'\n'

def main():
    model=json.loads((HERE/'bcrc_variants_geometry.json').read_text())
    for variant in model['variants']:
        name=variant['filename']+'.svg'
        (HERE/name).write_text(svg(variant),encoding='utf-8')
        print(name)

if __name__=='__main__':
    main()
