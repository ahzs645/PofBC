"""Synchronise conservative wood backplates with the final measured masks."""
import json
from lxml import etree as E
from reconstruct_illustrations import ROOT,ASSETS,NS,node,write_xml,render

def run():
    path=ASSETS/'wildlife-habitat-tree.svg';root=E.parse(str(path)).getroot();white=root.xpath('//*[@id="solid-wood-white"]')[0]
    for child in list(white):white.remove(child)
    for part in ['upper','lower']:
        source=json.loads((ROOT/'source'/f'tree-{part}-regions.json').read_text())
        for p in source.get('white_base_paths',[]):white.append(node('path',id=p['id'],d=p['path']))
    write_xml(root,path);render(path,ASSETS/'wildlife-habitat-tree.png',1600)
    print('Tree backplates synchronised to final measured geometry.',flush=True)

if __name__=='__main__':run()
