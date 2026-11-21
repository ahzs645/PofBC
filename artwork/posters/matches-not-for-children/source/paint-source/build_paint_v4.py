#!/usr/bin/env python3
"""Synthesize editable paint paths from authored placement and material fields.

No photograph or evaluation mask is read. Draft mode renders the designed
coverage directly for iteration; --svg exports those same synthetic coverage
fields as opaque vector paths, plus a simplified authored-field component.
"""
from pathlib import Path
import argparse
import json
import math
import re
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, distance_transform_edt
import contourpy
from paint_design import GROUND, UNDERPAINT, MASSES, OVERPAINT, GESTURES, LOWER_PATCHES

HERE=Path(__file__).resolve().parent
OUT=HERE.parent
W,H=1000,1400
SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('',SVG);ET.register_namespace('inkscape',INK)


def rgb(c):return np.array([int(c[i:i+2],16) for i in (1,3,5)])
def colour(c,delta):return '#'+''.join(f'{max(0,min(255,int(v+d))):02x}' for v,d in zip(rgb(c),delta))
def ashex(v):return '#'+''.join(f'{int(x):02x}' for x in v)
def polygon(points):
    im=Image.new('1',(W,H));ImageDraw.Draw(im).polygon(points,fill=1)
    return np.array(im,dtype=bool)
def newroot(title):
    root=ET.Element('{'+SVG+'}svg',width=str(W),height=str(H),viewBox=f'0 0 {W} {H}',version='1.1')
    ET.SubElement(root,'{'+SVG+'}title').text=title
    ET.SubElement(root,'{'+SVG+'}desc').text='Manually composed paint fields and localized brush gestures with seeded synthetic deposition. No photograph pixels generate contours. Opaque filled paths only. Colours match the supplied photograph appearance, not calibrated historical inks.'
    return root
def layer(root,id,label):return ET.SubElement(root,'{'+SVG+'}g',{'id':'paint-v4-'+id,'{'+INK+'}groupmode':'layer','{'+INK+'}label':label})
def poly_path(parent,pts,col,id):
    return ET.SubElement(parent,'{'+SVG+'}path',{'id':id,'fill':col,'d':'M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in pts)+' Z'})


class Paint:
    def __init__(self,export):
        self.export=export;self.rng=np.random.default_rng(14201967)
        self.image=np.zeros((H,W,3),dtype=np.uint8);self.image[:]=rgb(GROUND)
        self.root=newroot('BC Forest Service — Revision 4 composed paint')
        self.clean=newroot('BC Forest Service — Revision 4 clean paint fields')
        self.counts={'path_objects':0,'subpaths':0,'nodes':0}
        self.slow=self.field(22,18)
        self.pull=self.field(32,5.0)
        self.mid=self.field(5.0,2.1)
        self.fine=self.field(.7,.65)
        self.small=self.field(1.8,1.1)
        self.cross=self.field(2.2,8.0)
        self.rub=self.field(6,14)
        self.patch=self.field(12,8)
        self.noise=.42*self.mid+.36*self.fine+.22*self.small
        self.pigment=.35*self.pull+.34*self.slow+.24*self.mid+.14*self.fine
        self.all_orange=np.zeros((H,W),bool)

    def field(self,sy,sx):
        a=gaussian_filter(self.rng.normal(size=(H,W)).astype('float32'),(sy,sx))
        return a/(a.std()+1e-6)

    def path(self,g,mask,col,id,min_area=.8):
        self.image[mask]=rgb(col)
        if not self.export:return
        z=gaussian_filter(mask.astype('float32'),.5)
        cg=contourpy.contour_generator(z=np.pad(z,1),fill_type='OuterOffset',corner_mask=True)
        pp,oo=cg.filled(.5,1.5);commands=[]
        for points,offsets in zip(pp,oo):
            for start,end in zip(offsets[:-1],offsets[1:]):
                v=points[start:end]-1
                if len(v)<4:continue
                area=abs(float(np.sum(v[:-1,0]*v[1:,1]-v[1:,0]*v[:-1,1])))/2
                if area<min_area:continue
                keep=[0];last=0
                for k in range(2,len(v)):
                    d=v[k]-v[last];length=math.hypot(*d)
                    if not length:continue
                    inner=v[last+1:k]-v[last]
                    dist=np.abs(inner[:,0]*d[1]-inner[:,1]*d[0])/length
                    if len(dist) and dist.max()>.22:keep.append(k-1);last=k-1
                if keep[-1]!=len(v)-1:keep.append(len(v)-1)
                v=v[keep]
                commands.append('M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in v[:-1])+'Z')
                self.counts['subpaths']+=1;self.counts['nodes']+=len(v)-1
        if commands:
            ET.SubElement(g,'{'+SVG+'}path',{'id':'paint-v4-'+id,'fill':col,'fill-rule':'evenodd','d':' '.join(commands)})
            self.counts['path_objects']+=1

    def material(self,mask,kind):
        distance=distance_transform_edt(mask)-distance_transform_edt(~mask)
        # A long pull field gives sheared/dragged boundaries, avoiding a ring of
        # equal-sized round scallops on every perimeter.
        edge_shift=1.9*self.pull+.7*self.rub+.8*self.mid
        if kind=='wash' or kind=='rightwash':
            mask=(distance+edge_shift*2>0)&(.35*self.patch+.30*self.pull+.55*self.mid+.35*self.fine>-.55)
        elif kind=='body':
            mask=(distance+edge_shift>0)&~((.3*self.patch+.55*self.mid+.3*self.fine>1.45)&(distance<13))
        elif kind=='solid' or kind=='base-red':
            mask=distance+edge_shift*.6>0
        elif kind=='thin-lift':
            mask=(distance+edge_shift>0)&(.5*self.rub+.4*self.patch+.35*self.mid>-.12)
        else:
            mask=(distance+edge_shift*1.35>0)&(.5*self.patch+.3*self.rub+.3*self.mid>-.48)
        return mask,distance

    def tone(self,g,mask,col,id,strength=1,kind=None):
        # Low-contrast vertical pigment variations have no repeating hatch grid.
        tex=.45*self.pull+.4*self.mid+.15*self.fine+.1*self.patch
        steps=[(-1.2,(-2,-6,-1)),(-.65,(-1,-3,-1)),(-.15,(0,0,0)),(.35,(1,4,1)),(.8,(1,8,1)),(1.2,(2,12,2)),(1.6,(3,18,2))]
        if kind in {'wash','rightwash'}:
            tex=.3*self.pull+.4*self.mid+.15*self.fine+.25*self.patch
            steps=[(-.5,(-1,-3,-1)),(.15,(1,3,1)),(.85,(2,7,1))]
        for j,(threshold,delta) in enumerate(steps):
            self.path(g,mask&(tex>threshold),colour(col,tuple(round(x*strength) for x in delta)),id+f'-tone-{j}',1.2)

    def fields(self,rootid,label,items):
        g=layer(self.root,rootid,label);cg=layer(self.clean,rootid,label)
        for name,pts,col,kind in items:
            pm=polygon(pts);mask,dist=self.material(pm,kind)
            if name=='header-warmth':
                yy=np.arange(H)[:,None]
                mask=(yy<145)&(.4*self.mid+.35*self.fine+.20*self.patch>(yy-65)/35)
            if name=='centre-right-thin-lift':
                mask&=(.55*self.mid+.35*self.fine+.2*self.pull>.05)
            if kind=='body':
                # Thin dragged paint sits beneath the opaque body and extends
                # unevenly beyond it; it is not a uniform ring or dotted halo.
                veil=(dist+2*self.pull+.8*self.rub>-10)&(.3*self.patch+.5*self.mid+.6*self.fine>.15)
                self.path(g,veil,colour(col,(0,24,2)),name+'-thin-drag',1.2)
            self.path(g,mask,col,name);poly_path(cg,pts,col,'clean-'+name)
            self.tone(g,mask,col,name,.8 if kind in {'wash','rightwash'} else 1,kind)
            if kind=='body':
                rubbed=mask&(.5*self.pull+.5*self.mid+.4*self.fine>1.6)&(self.patch>.5)
                self.path(g,rubbed,colour(col,(1,18,2)),name+'-rubbed-pigment',1.4)
            if kind in {'body','base-red','solid'}:self.all_orange|=mask
        return g

    def ribbon(self,points,width):
        p=np.array(points,float);t=np.linspace(0,1,151)[:,None]
        v=(1-t)**3*p[0]+3*(1-t)**2*t*p[1]+3*(1-t)*t**2*p[2]+t**3*p[3]
        tangent=np.gradient(v,axis=0);normal=np.stack([-tangent[:,1],tangent[:,0]],1)
        normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-6)
        w=width*(.54+.46*np.sin(np.pi*t[:,0])**.5)/2
        outer=np.vstack([v+normal*w[:,None],(v-normal*w[:,None])[::-1]])
        return polygon([tuple(x) for x in outer]),outer

    def run(self):
        ground=layer(self.root,'ground','01 · Yellow ground and pigment');clean=layer(self.clean,'ground','01 · Yellow ground')
        poly_path(ground,[(-10,-10),(1010,-10),(1010,1410),(-10,1410)],GROUND,'paint-v4-yellow-ground')
        poly_path(clean,[(-10,-10),(1010,-10),(1010,1410),(-10,1410)],GROUND,'clean-yellow-ground')
        for j,(threshold,col) in enumerate([(-.7,'#f0bf08'),(.0,'#f2c40a'),(.72,'#f4c80c')]):
            self.path(ground,(.55*self.slow+.28*self.mid+.15*self.small>threshold),col,f'ground-pigment-{j}',1.4)
        self.fields('underpaint','02 · Warm underpainting',UNDERPAINT)
        self.fields('orange-fields','03 · Long orange and red pulls',MASSES)
        self.fields('overpaint','04 · Yellow lifts and thin overlap',OVERPAINT)
        g=layer(self.root,'lower-remnants','05 · Unequal lower paint remnants')
        cg=layer(self.clean,'lower-remnants','05 · Lower paint remnants')
        yy,xx=np.indices((H,W))
        belt_points=[(35,810),(116,837),(170,860),(280,876),(380,893),(480,886),(598,904),(600,1085),(60,1070)]
        belt=polygon(belt_points)
        # A connected old undercoat is exposed unevenly through yellow rubbing.
        # This replaces the first draft's separate upright tuft silhouettes.
        threshold=np.interp(yy,[810,890,970,1040],[2.1,1.35,.3,-.8])
        terrain=.42*self.patch+.5*self.pull+.45*self.mid+.3*self.cross+.25*self.fine
        exposed=belt&(terrain>threshold)
        self.path(g,exposed,'#e85d0b','lower-connected-undercoat',1.3)
        deep=exposed&(terrain>threshold+.55)
        self.path(g,deep,'#e64a09','lower-deeper-remnants',1.6)
        muted_zone=polygon([(267,925),(498,922),(512,968),(494,1018),(278,1018),(270,976)])
        mz=distance_transform_edt(muted_zone)-distance_transform_edt(~muted_zone)
        mute=(mz+2*self.mid>0)&(.5*self.mid+.3*self.fine>-.2)
        self.path(g,exposed&mute,'#e86b0c','lower-muted-thin-cores',1.2)
        self.path(g,deep&mute,'#e65b0a','lower-muted-deep-cores',1.2)
        self.path(g,exposed&(self.rub>.45)&(self.mid>-.3),'#e9890c','lower-thin-rubbing',1.5)
        poly_path(cg,belt_points,'#eeb10c','clean-lower-connected-undercoat')
        # Warm broken deposits occupy the width of the right field; no narrow
        # repeated side rail determines their positions.
        right=(xx>875)&(yy>75)&(yy<1120)
        right_tex=.5*self.patch+.60*self.pull+.4*self.mid+.2*self.fine
        amber=right&(right_tex>.85)
        self.path(g,amber,'#f0a611','right-broad-amber-residue',1.4)
        self.path(g,amber&(self.mid+.5*self.fine>.35),'#ed9110','right-broken-amber-residue',1.1)
        self.path(g,right&(right_tex>1.4)&(self.mid+.5*self.fine>.25),'#e9780e','right-broken-orange-residue',1.1)
        g=layer(self.root,'brush-gestures','06 · Located dry brush gestures')
        for i,(name,points,width,col,kind,cov) in enumerate(GESTURES):
            if name.startswith('lower-') and width>25:continue
            mask,outer=self.ribbon(points,width)
            d=distance_transform_edt(mask)-distance_transform_edt(~mask)
            if kind=='dry':
                tex=.45*self.pull+.5*self.mid+.2*self.fine
                mask=(d+1.2*self.mid>0)&(tex>cov-.2)
            else:
                tex=.36*self.pull+.4*self.mid+.28*self.fine+.26*self.slow
                mask=(d+1.5*self.mid>0)&(tex>cov-.2)
            self.path(g,mask,col,name,.8)
            self.path(g,mask&(self.pigment>.5),colour(col,(2,14,1)),name+'-thin',1.1)
        g=layer(self.root,'print-grain','07 · Local pigment grain')
        # Quantized low-amplitude pigment differences, tied to current paint.
        current=self.image.copy()
        for j,(mask,delta) in enumerate([
            ((self.small*.5+self.fine*.55>1.4),(-2,-3,-1)),
            ((self.small*.4-self.fine*.55>1.6),(2,4,1)),
        ]):
            # Use a few broad ink families, not a per-photo-pixel colour map.
            families=[((current[:,:,1]<100)&(current[:,:,0]>220),'#f14c11'),
                      ((current[:,:,1]>=100)&(current[:,:,1]<165),'#eda10e'),
                      (current[:,:,1]>=165,'#f0bd0c')]
            for k,(family,col) in enumerate(families):self.path(g,mask&family,colour(col,delta),f'grain-{j}-{k}',1.0)
        g=layer(self.root,'lower-red-finish','08 · Continuous lower red print edge')
        # The photograph darkens toward the bottom. Opaque, gently interlocking
        # tonal fields express that appearance without a live SVG gradient.
        bottom=(yy>1125)&((xx<770)|(yy>1280)|(xx>981))
        for j in range(11):
            fraction=j/10
            col=ashex(np.round(np.array([229,46,10])*(1-fraction)+np.array([210,27,7])*fraction).astype(int))
            y=1120+fraction*275
            mask=bottom&(yy+self.slow*33+self.mid*9>y)
            self.path(g,mask,col,f'lower-red-tone-{j}',3)
            self.path(g,mask&(self.pigment>.48),colour(col,(2,3,1)),f'lower-red-pigment-{j}',2)
        self.image[1396:]=rgb('#d21b07')
        poly_path(g,[(0,1396),(1000,1396),(1000,1410),(0,1410)],'#d21b07','paint-v4-continuous-lower-edge')
        # A clean version uses two broad low-contrast lower fields.
        cg=layer(self.clean,'lower-red-finish','06 · Continuous lower red field')
        poly_path(cg,[(0,1285),(1000,1285),(1000,1410),(0,1410)],'#dc2409','clean-lower-red')
        Image.fromarray(self.image).save(OUT/'paint_v4_draft.png')
        if self.export:
            ET.ElementTree(self.root).write(OUT/'paint_v4.svg',encoding='utf-8',xml_declaration=True)
            ET.ElementTree(self.clean).write(OUT/'paint_v4_clean.svg',encoding='utf-8',xml_declaration=True)
            (OUT/'paint_v4_construction_stats.json').write_text(json.dumps(self.counts,indent=2))
        print(json.dumps({'draft':str(OUT/'paint_v4_draft.png'),'export_svg':self.export,**self.counts}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--svg',action='store_true')
    Paint(parser.parse_args().svg).run()
