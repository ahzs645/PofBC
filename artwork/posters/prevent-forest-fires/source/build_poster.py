"""Assemble the independent, constructed artwork into layered vector files."""
from pathlib import Path
import xml.etree.ElementTree as ET
from illustration import build_script, YELLOW, PAPER
from flames_v2 import build_flames
from foreground_v2 import build_foreground
from ground_details_v4 import build_ground_details
from canopy import build_canopy
from headline import build_headline
from footer import build_footer

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'artwork'

def layer(id,label,fragment):
    return f'<g id="{id}" inkscape:groupmode="layer" inkscape:label="{label}">{fragment}</g>'

def document(layers):
    return '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="250mm" height="360mm" viewBox="0 0 1000 1440"
     role="img" aria-labelledby="poster-title poster-description">
<title id="poster-title">Prevent Forest Fires — British Columbia Forest Service</title>
<desc id="poster-description">A constructed vector reconstruction from a supplied photograph: yellow sky, dark conifers, orange flames, custom ivory script and dark italic lettering, a burnt woodland foreground, and the slogan Fire destroys timber and payrolls. All artwork and lettering are editable vector paths. No source image, autotracing, or external typeface is used. Illustration details and colours are interpretive, not a verified archival facsimile.</desc>
<defs><clipPath id="poster-boundary"><rect width="1000" height="1440"/></clipPath></defs>
<g clip-path="url(#poster-boundary)">
'''+'\n'.join(layers)+'''
</g></svg>'''

def main(output_dir=None):
    out=Path(output_dir).resolve() if output_dir else OUT
    out.mkdir(parents=True,exist_ok=True)
    layers=[
        layer('layer-paper','01 · Yellow field',f'<rect id="yellow-field" width="1000" height="1440" fill="{YELLOW}"/>'),
        layer('layer-canopy','02 · Conifer canopy',build_canopy()),
        layer('layer-flames','03 · Flame field and tongues',build_flames()),
        layer('layer-foreground','04 · Burnt trunks, logs and woodcut marks',build_foreground()+build_ground_details()),
        layer('layer-script','05 · Prevent — constructed script',build_script()),
        layer('layer-headline','06 · FOREST FIRES — constructed capitals',build_headline()),
        layer('layer-footer','07 · Lower slogan and service credit',build_footer()),
    ]
    doc=document(layers)
    # Serialize as supplied so hand-authored path formatting remains readable.
    dest=out/'BC_Forest_Service_Reconstructed.svg'
    dest.write_text(doc,encoding='utf-8')
    ET.fromstring(doc)
    lettering=document([layers[4],layers[5],layers[6]])
    (out/'BC_Forest_Service_Lettering.svg').write_text(lettering,encoding='utf-8')
    illustration=document(layers[:4])
    illustration=illustration.replace(
        '<title id="poster-title">Prevent Forest Fires — British Columbia Forest Service</title>',
        '<title id="poster-title">Forest-fire poster illustration — trees, flames and burnt timber</title>')
    (out/'BC_Forest_Service_Illustration.svg').write_text(illustration,encoding='utf-8')
    print(dest)
    print('Artwork vector paths:',doc.count('<path'))
    print('Raster images:',doc.count('<image'))
    print('Live font-dependent text:',doc.count('<text'))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',help='Output folder; defaults to artwork beside the source folder')
    main(parser.parse_args().output_dir)
