#!/usr/bin/env python3
"""Rebuild the outlined v2 SVGs. Standard library only; no font files needed."""
from pathlib import Path
import argparse,json,html

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--out',type=Path,default=Path('rebuilt-svg'))
 args=p.parse_args();args.out.mkdir(parents=True,exist_ok=True)
 model=json.loads(Path(__file__).with_name('construction-v2.json').read_text())
 for v in model['variants']:
  x,y=v['origin_in_source_coordinates'];w,h=v['size']
  for name,color in [('black','#000000'),('white','#FFFFFF')]:
   a=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.6f}" height="{h:.6f}" viewBox="{x:.6f} {y:.6f} {w:.6f} {h:.6f}" fill="{color}">',f'<title>{html.escape(v["label"])} — v2 reconstruction candidate</title>']
   for row in v['rows']:
    a.append(f'<g id="{row["id"]}" data-text="{html.escape(row["text"])}">')
    for g in row['glyphs']:
     mat=' '.join(f'{z:.9f}' for z in g['matrix'])
     a.append(f'<path data-character="{g["character"]}" transform="matrix({mat})" d="{g["normalized_path"]}"/>')
    a.append('</g>')
   a.append('</svg>')
   f=args.out/f'{v["id"]}-v2-{name}.svg';f.write_text('\n'.join(a));print(f)
if __name__=='__main__':main()
