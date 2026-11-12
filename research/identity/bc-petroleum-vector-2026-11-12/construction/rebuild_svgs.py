"""Rebuild the four SVG artwork files from the reusable construction data.
Requires only Python 3's standard library. No fonts or reference images needed.
Run: python construction/rebuild_svgs.py --output rebuilt-artwork
"""
from pathlib import Path
import json, argparse, html

P=Path(__file__).resolve().parent
cfg=json.loads((P/"emblem_geometry.json").read_text())
glyphs=json.loads((P/"bcpc_glyphs.json").read_text())["glyphs"]
layout=json.loads((P/"bcpc_type_layout.json").read_text())
parser=argparse.ArgumentParser()
parser.add_argument("--output",type=Path,default=P.parent/"rebuilt-artwork")
args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)

def root(vb,content,title,w,h):
    v=" ".join(map(str,vb))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{v}" width="{w}" height="{h}">'
            f'<title>{html.escape(title)}</title>'
            '<desc>Reconstructed from supplied monochrome BCPC report scans. '
            'Custom letter outlines; exact original font unconfirmed. All artwork is vector geometry.</desc>'
            f'{content}</svg>')

for suffix,colour in [("black","#000000"),("white","#ffffff")]:
    path=f'<path fill="{colour}" fill-rule="evenodd" d="{cfg["emblem_path"]}"/>'
    (args.output/f"BCPC_emblem_{suffix}.svg").write_text(root(cfg["emblem_viewbox"],path,"BCPC emblem - reconstruction",500,640))
    t=cfg["lockup_emblem_transform"]
    content=f'<g id="emblem" transform="translate({t["x"]} {t["y"]}) scale({t["scale"]})">{path}</g>'
    content+=f'<g id="wordmark" fill="{colour}" fill-rule="evenodd">'
    for line in layout:
        content+=f'<g id="line-{line["text"].lower()}" aria-label="{line["text"]}">'
        for i,g in enumerate(line["placements"]):
            content+=(f'<path id="{line["text"].lower()}-{i+1}-{g["char"]}" '
                      f'transform="translate({g["x"]:.8f} {g["y"]:.8f}) scale({g["sx"]:.10f} {g["sy"]:.10f})" '
                      f'd="{glyphs[g["char"]]["path"]}"/>')
        content+='</g>'
    content+='</g>'
    (args.output/f"BCPC_stacked_logo_{suffix}.svg").write_text(root(cfg["lockup_viewbox"],content,"BCPC stacked logo - reconstruction",732,723))
print("Rebuilt four SVG files in",args.output.resolve())
