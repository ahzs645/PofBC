#!/usr/bin/env python3
"""Construct clean wordmarks from intentional glyph masters, not raster contours.

The reference rasters supply only the nominal character boxes. Every contour
below is an explicit geometric design with a small number of nodes and curves.
No bitmap tracing, contour fitting, font lookup, or raster embedding is used.
"""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent

class Pen:
    def __init__(self,w,h): self.w,self.h,self.parts=w,h,[]
    def add(self,cmd,*a):
        def f(x): return f'{x:.4f}'.rstrip('0').rstrip('.') or '0'
        self.parts.append(cmd+' '.join(f(v*(self.w if i%2==0 else self.h)) for i,v in enumerate(a)))
        return self
    def m(self,*a): return self.add('M',*a)
    def l(self,*a): return self.add('L',*a)
    def c(self,*a): return self.add('C',*a)
    def q(self,*a): return self.add('Q',*a)
    def z(self): self.parts.append('Z'); return self
    def poly(self,*pts):
        self.m(*pts[0])
        for pt in pts[1:]: self.l(*pt)
        return self.z()
    def d(self): return ' '.join(self.parts)

def glyph(c,w,h,style,counter=None):
    p=Pen(w,h)
    # Vertical and horizontal strokes are deliberately optically adjusted.
    main = style in ('main-light','main-bold')
    slab = style=='main-light'
    s = {'main-light':.178,'main-bold':.205,'small':.235,'top':.230,'top-heavy':.320}[style]
    sx=s*h/w
    sy=.192 if style=='top' else (.28 if style=='top-heavy' else s)
    if c=='T':
        stem=sx*(1.15 if style=='top' else 1)
        p.poly((0,0),(1,0),(1,sy),(.5+stem/2,sy),(.5+stem/2,1),(.5-stem/2,1),(.5-stem/2,sy),(0,sy))
    elif c=='H':
        cross0,cross1=(.36,.64) if style=='top-heavy' else (.42,.61)
        p.poly((0,0),(sx,0),(sx,cross0),(1-sx,cross0),(1-sx,0),(1,0),(1,1),(1-sx,1),(1-sx,cross1),(sx,cross1),(sx,1),(0,1))
    elif c=='E':
        if style=='top-heavy':sx,sy=.24*h/w,.24
        p.poly((0,0),(1,0),(1,sy),(sx,sy),(sx,.42),(.84,.42),(.84,.60),(sx,.60),(sx,1-sy),(1,1-sy),(1,1),(0,1))
    elif c=='I': p.poly((0,0),(1,0),(1,1),(0,1))
    elif c=='L':
        p.poly((0,0),(sx,0),(sx,1-sy),(1,1-sy),(1,1),(0,1))
    elif c=='N':
        # Humanist diagonal; pointed upper-left and lower-right preserve the
        # characteristic terminal treatment present in both supplied wordmarks.
        p.poly((0,0),(.055,0),(1-sx,.61),(1-sx,0),(1,0),(1,1),(.94,1),(sx,.43),(sx,1),(0,1))
    elif c=='M':
        # A deep central crotch and shallow shoulders, not a generic geometric M.
        valley=.88 if style=='main-bold' else .97
        p.m(0,1).l(0,.02).l(.14,.02).c(.20,.06,.27,.22,.35,.36).l(.5,.60).l(.68,.30).c(.78,.11,.82,.025,.88,0).l(1,0).l(1,1).l(1-sx,1).l(1-sx,.51).l(.54,valley).l(.47,valley).l(sx,.52).l(sx,1).z()
    elif c=='V':
        # The narrow upward-facing terminal rebates are intentional.
        p.m(0,0).l(.25,0).l(.25,.11).c(.28,.25,.38,.48,.50,.69).c(.61,.48,.71,.25,.75,.11).l(.75,0).l(1,0).l(1,.07).c(.92,.28,.76,.68,.58,.98).q(.55,1,.52,1).l(.46,1).c(.29,.73,.12,.33,.015,.10).z()
    elif c=='O':
        # A subtly squared oval (quarter controls about .62 of each radius):
        # broader shoulders than a circle, without raster-like polygon facets.
        p.m(.47,0).c(.7986,0,1,.1862,1,.49).c(1,.8062,.8214,1,.53,1).c(.2014,1,0,.8138,0,.51).c(0,.1938,.1786,0,.47,0).z()
        ix=(1-counter[0]/w)/2 if counter else s*h/w*.92
        iy=(1-counter[1]/h)/2 if counter else sy*.92
        innerw,innerh=1-2*ix,1-2*iy
        # Four controlled curves create a round, very gently shouldered counter.
        p.m(.48,iy).c(.48+innerw*.31,iy,1-ix,.5-innerh*.31,1-ix,.5).c(1-ix,.5+innerh*.31,.52+innerw*.31,1-iy,.52,1-iy).c(.52-innerw*.31,1-iy,ix,.5+innerh*.31,ix,.5).c(ix,.5-innerh*.31,.48-innerw*.31,iy,.48,iy).z()
    elif c=='C':
        p.m(1,.17).c(.85,.04,.68,0,.49,0).c(.18,0,0,.20,0,.51).c(0,.83,.18,1,.49,1).c(.70,1,.87,.94,1,.84).l(.96,.66).c(.81,.75,.70,.79,.51,.79).c(.33,.79,.26,.70,.26,.50).c(.26,.32,.33,.23,.51,.23).c(.69,.23,.79,.28,.91,.34).z()
    elif c=='D':
        if slab:
            # D and P have short left-hand slab projections in the horizontal
            # main line; they are a distinguishing feature of this reference.
            p.m(0,0).l(.46,0).c(.72,0,1,.21,1,.38).l(1,.67).c(1,.82,.71,1,.43,1).l(0,1).l(0,.87).l(.067,.87).l(.067,.12).l(0,.12).z()
            p.m(.30,.15).l(.43,.15).c(.63,.15,.80,.30,.80,.42).l(.80,.65).c(.80,.73,.62,.85,.43,.85).l(.30,.85).z()
        else:
            p.m(0,0).l(.40,0).c(.66,0,1,.20,1,.38).l(1,.66).c(1,.82,.70,1,.40,1).l(0,1).z()
            p.m(sx,.18).l(.41,.18).c(.61,.18,1-sx*.92,.32,1-sx*.92,.42).l(1-sx*.92,.65).c(1-sx*.92,.72,.60,.82,.41,.82).l(sx,.82).z()
    elif c=='P':
        if slab:
            p.m(0,0).l(.57,0).c(.84,0,1,.10,1,.28).c(1,.45,.80,.56,.54,.56).l(.36,.56).l(.36,.87).l(.46,.87).l(.46,1).l(0,1).l(0,.87).l(.09,.87).l(.09,.13).l(0,.13).z()
            p.m(.36,.14).l(.55,.14).c(.69,.14,.74,.19,.74,.28).c(.74,.38,.67,.43,.54,.43).l(.36,.43).z()
        else:
            p.m(0,0).l(.56,0).c(.80,0,1,.11,1,.30).c(1,.49,.79,.58,.47,.58).l(sx,.58).l(sx,1).l(0,1).z()
            p.m(sx,.18).l(.48,.18).c(.66,.18,.72,.22,.72,.30).c(.72,.38,.65,.41,.48,.41).l(sx,.41).z()
    elif c=='R':
        # Compact bowl, small counter and a softly splayed diagonal leg.
        p.m(0,0).l(.42,0).c(.68,0,.80,.10,.80,.29).c(.80,.43,.72,.49,.64,.54).c(.74,.61,.80,.76,.90,.85).l(1,.93).l(.98,1).l(.73,1).c(.61,.90,.56,.75,.48,.66).q(.41,.59,.32,.59).l(.31,.59).l(.31,1).l(0,1).z()
        p.m(.31,.19).l(.42,.19).c(.55,.19,.59,.23,.59,.30).c(.59,.39,.54,.43,.43,.43).l(.31,.43).z()
    elif c=='A':
        # Slightly bowed sides and rounded foot corners carry the source's
        # humanist construction through low-resolution pixel uncertainty.
        p.m(.43,0).l(.57,0).c(.63,.11,.77,.44,.98,.85).q(1,.90,1,.95).q(.98,1,.94,1).l(.76,1).l(.65,.66).l(.34,.66).l(.25,1).l(.05,1).q(0,1,0,.95).q(0,.90,.025,.85).c(.20,.46,.35,.12,.43,0).z()
        p.m(.50,.24).l(.39,.49).l(.61,.49).z()
    else: raise ValueError(c)
    return p.d()

LAYOUTS={
 'horizontal':[
  ('THE','top',[(220,108,244,134),(248,108,270,134),(277,108,291,134)]),
  ('DEVELOPMENT','main-light',[(222,142,252,177),(258,142,279,177),(283,143,314,176),(320,143,341,177),(348,143,369,177),(372,142,405,178),(410,143,432,178),(438,143,473,178),(481,143,503,177),(511,142,540,177),(545,142,576,177)]),
  ('CORPORATION','small',[(221,184,246,212),(248,185,276,213),(279,185,300,212),(303,185,320,212),(323,185,349,213),(353,185,373,212),(375,187,399,212),(398,185,421,212),(427,185,433,212),(437,185,464,214),(467,186,491,214)])
 ],
 'stacked':[
  ('THE','top-heavy',[(280,45,302,70),(304,45,326,70),(332,45,346,70)]),
  ('DEVELOPMENT','main-bold',[(152,76,180,109),(184,76,203,109),(205,76,236,107),(240,76,261,109),(267,76,289,109),(289,76,321,109),(326,76,346,109),(351,76,383,109),(391,76,410,108),(416,76,444,108),(448,76,477,108)]),
  ('CORPORATION','small',[(185,114,209,141),(210,115,235,141),(237,115,257,140),(260,115,276,140),(280,115,304,141),(307,115,327,141),(328,117,351,141),(349,116,371,141),(375,116,381,141),(385,116,410,142),(412,116,434,143)])
 ]}

def build():
    metadata={}
    for variant,rows in LAYOUTS.items():
        svg=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','width':'640','height':'350','viewBox':'0 0 640 350'})
        ET.SubElement(svg,'title').text=f'The Development Corporation — {variant} custom vector lettering'
        ET.SubElement(svg,'desc').text='Reconstructed from the supplied raster using explicit geometric glyph masters; no bitmap tracing. No live text or embedded images.'
        allg=ET.SubElement(svg,'g',{'id':'lettering','fill':'#000000','fill-rule':'evenodd'})
        metadata[variant]=[]
        for text,style,boxes in rows:
            g=ET.SubElement(allg,'g',{'id':'word-'+text.lower(),'aria-label':text})
            for i,(c,box) in enumerate(zip(text,boxes)):
                x,y,x1,y1=box
                ocounters={('horizontal','DEVELOPMENT',5):(20,24),('horizontal','CORPORATION',1):(15,16),('horizontal','CORPORATION',4):(15,15),('horizontal','CORPORATION',9):(15,17),('stacked','DEVELOPMENT',5):(18,21),('stacked','CORPORATION',1):(11,12),('stacked','CORPORATION',4):(13,14),('stacked','CORPORATION',9):(12,13)}
                d=glyph(c,x1-x,y1-y,style,ocounters.get((variant,text,i)))
                ET.SubElement(g,'path',{'id':f'{text.lower()}-{i+1:02}-{c.lower()}','transform':f'translate({x} {y})','d':d})
                metadata[variant].append({'char':c,'bbox':box,'style':style,'d':d})
        ET.indent(svg,space='  ')
        ET.ElementTree(svg).write(OUT/f'sans-{variant}-lettering.svg',encoding='utf-8',xml_declaration=True)
    (OUT/'glyph-layouts.json').write_text(json.dumps(metadata,indent=2)+'\n')

if __name__=='__main__': build()
