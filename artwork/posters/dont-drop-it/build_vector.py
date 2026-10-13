#!/usr/bin/env python3
"""Geometric reconstruction of the supplied B. C. Forest Service emblem.

The illustration and display lettering are authored as line/cubic-Bezier paths.
No bitmap contour extraction, auto-tracing, or embedded raster image is used.
Only the small footer uses outlines from an installed font (Lato Heavy).
No font file is distributed. Pass --font to substitute a local TTF/OTF.
"""
from __future__ import annotations
import argparse, copy, math, os
from pathlib import Path
from lxml import etree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
import cairosvg

SVG='http://www.w3.org/2000/svg'
INK='http://www.inkscape.org/namespaces/inkscape'
# Inkscape's actual namespace is the historical URI below.
INK='http://www.inkscape.org/namespaces/inkscape'
NS={'svg':SVG, 'inkscape':INK}
GREEN='#003E2D'
CREAM='#F8E3BB'
FOOTER='#F1F0DE'
W=H=1254

def E(parent,tag,**attrs):
    el=ET.SubElement(parent, f'{{{SVG}}}{tag}')
    for k,v in attrs.items(): el.set(k.replace('_','-'),str(v))
    return el

def layer(root,id,label,**attrs):
    g=E(root,'g',id=id,**attrs)
    g.set(f'{{{INK}}}groupmode','layer')
    g.set(f'{{{INK}}}label',label)
    return g

def path(parent,id,d,**attrs):
    return E(parent,'path',id=id,d=' '.join(d.split()),**attrs)

TOP={
 'D':'''M115 224 L161 224 C232 224 260 265 267 330 C274 404 248 451 189 451 L129 451 Z
 M177 260 C194 255 201 274 202 302 L207 383 C209 405 202 415 188 415 Z''',
 'O':'''M347 225 C297 225 274 267 275 337 C277 407 303 454 356 454 C407 454 431 409 425 336 C422 265 398 225 347 225 Z
 M348 255 C336 255 335 264 337 283 L344 400 C345 416 348 424 358 424 C370 424 371 415 369 397 L362 280 C361 264 359 255 348 255 Z''',
 'N':'''M437 229 L478 229 L524 321 L520 229 L554 229 L566 454 L527 454 L480 361 L485 454 L449 454 Z''',
 'apostrophe':'''M554 195 L582 195 L588 265 L568 265 Z''',
 'T':'''M599 229 L729 229 L731 265 L693 265 L701 454 L649 454 L639 266 L600 266 Z''',
}
DROP={
 'D':'''M79 179 L127 179 C178 177 205 210 205 262 C205 316 180 345 134 345 L83 345 Z
 M129 209 C145 205 148 217 148 237 L150 283 C150 304 144 313 131 313 Z''',
 'R':'''M219 178 L264 178 C311 176 337 195 338 232 C338 255 329 272 317 282 L342 343 L295 343 L273 287 L269 287 L270 344 L223 344 Z
 M268 206 L275 206 C285 206 289 216 289 231 C289 247 282 255 269 256 Z''',
 'O':'''M414 174 C370 174 350 209 350 260 C350 314 376 346 415 346 C458 346 480 313 480 260 C480 207 456 174 414 174 Z
 M414 198 C404 198 400 206 400 221 L402 291 C402 312 405 320 415 320 C426 320 430 312 430 296 L428 222 C428 205 424 198 414 198 Z''',
 'P':'''M498 176 L547 175 C592 174 615 196 615 232 C615 267 591 286 548 286 L548 340 L502 341 Z
 M547 203 C562 200 568 211 568 228 C568 245 562 255 549 257 Z''',
}

def add_footer(parent,fontpath,live=False):
    font=TTFont(fontpath)
    glyphs=font.getGlyphSet()
    cmap=font.getBestCmap()
    upem=font['head'].unitsPerEm
    size=44.0
    scale=size/upem
    text='B. C. Forest Service'
    tracking=11.8
    advances=[font['hmtx'].metrics[cmap[ord(c)]][0]*scale for c in text]
    total=sum(advances)+tracking*(len(text)-1)
    radius=533.0
    cx,cy=627.0,620.0
    start_deg=136.5
    group=E(parent,'g',id='footer-lettering',fill=FOOTER,aria_label=text)
    if live:
        start=math.radians(start_deg)
        end=start-total/radius
        a=(cx+radius*math.cos(start),cy+radius*math.sin(start))
        b=(cx+radius*math.cos(end),cy+radius*math.sin(end))
        defs=E(group,'defs')
        path(defs,'footer-baseline',f'M{a[0]:.5f} {a[1]:.5f} A{radius} {radius} 0 0 0 {b[0]:.5f} {b[1]:.5f}')
        t=E(group,'text',font_family='Lato, sans-serif',font_weight='800',font_size=size,letter_spacing=tracking)
        tp=E(t,'textPath',href='#footer-baseline')
        tp.set('{http://www.w3.org/1999/xlink}href','#footer-baseline')
        tp.text=text
    else:
        # Optical positions from the reference, recorded as letter boxes.
        # These position newly typeset glyphs; they are not traced outlines.
        placements = [
            ('B',242,957,34,36), ('.',269,1003,7,7),
            ('C',295,1003,34,35), ('.',323,1046,7,6),
            ('F',362,1046,31,30), ('o',396,1074,22,23),
            ('r',429,1088,21,22), ('e',462,1102,21,23),
            ('s',499,1113,20,23), ('t',536,1114,15,29),
            ('S',593,1118,21,33), ('e',628,1130,21,22),
            ('r',665,1129,13,21), ('v',691,1125,21,21),
            ('i',725,1112,12,29), ('c',750,1113,21,22),
            ('e',783,1103,21,22),
        ]
        for i,(ch,x,y,w,h) in enumerate(placements):
            px,py=x+w/2,y+h/2
            a=math.atan2(py-cy,px-cx)-math.pi/2
            matrix=(scale*math.cos(a),scale*math.sin(a),
                    scale*math.sin(a),-scale*math.cos(a),0,0)
            name=cmap[ord(ch)]
            bp=BoundsPen(glyphs)
            glyphs[name].draw(TransformPen(bp,matrix))
            x0,y0,x1,y1=bp.bounds
            # Centre each clean font outline on its optical reference position.
            matrix=matrix[:4]+(px-(x0+x1)/2,py-(y0+y1)/2)
            g=E(group,'g',id=f'footer-glyph-{i+1:02d}')
            E(g,'title').text=ch
            pen=SVGPathPen(glyphs)
            glyphs[name].draw(TransformPen(pen,matrix))
            path(g,f'footer-outline-{i+1:02d}',pen.getCommands())
    font.close()


def build(fontpath, live=False):
    root=ET.Element(f'{{{SVG}}}svg',nsmap={None:SVG,'inkscape':INK})
    root.set('width','1254');root.set('height','1254');root.set('viewBox','0 0 1254 1254')
    root.set('version','1.1');root.set('role','img')
    root.set('aria-labelledby','artwork-title artwork-description')
    E(root,'title',id='artwork-title').text="DON'T DROP IT! — B. C. Forest Service"
    E(root,'desc',id='artwork-description').text=(
      'A clean geometric reconstruction from the supplied historic-emblem image. '
      'Dark green circular field, cream double border, hand-built condensed display lettering, '
      'diagonal cigarette, looped smoke, and curved Forest Service credit. '
      'The original photographic texture and damaged edge are intentionally omitted. '
      'Illustration and headline are editable vector paths; no raster image or auto-trace is present. '
      +('Footer uses live Lato Heavy text.' if live else 'Footer lettering is outlined.'))
    base=layer(root,'field','01 · Circular field')
    E(base,'circle',id='green-disc',cx=627,cy=620,r=601,fill=GREEN)
    border=layer(root,'borders','02 · Double circular border',fill='none',stroke=CREAM)
    E(border,'circle',id='outer-rim',cx=627,cy=620,r=592,stroke_width=18)
    E(border,'circle',id='inner-rule',cx=627,cy=620,r=556.5,stroke_width=13)
    smoke=layer(root,'smoke','03 · Smoke flourishes')
    sg=E(smoke,'g',id='upper-smoke',fill='none',stroke=CREAM,stroke_width=12.6,stroke_linecap='round',stroke_linejoin='round')
    path(sg,'upper-smoke-strand-a','''M414 301
      C433 281 432 249 433 226 C436 174 469 135 509 132
      C544 124 576 142 611 146 C640 153 659 143 685 132
      C716 120 746 116 765 135 C785 150 789 173 810 189
      C836 207 854 203 884 209 C918 215 934 238 940 264
      C944 284 939 301 949 313''')
    path(sg,'upper-smoke-strand-b','''M383 294
      C392 261 408 247 441 226 C469 210 478 175 513 154
      C548 133 568 134 598 122 C630 109 652 116 674 121
      C706 133 721 141 751 151 C779 166 802 152 827 158
      C863 163 880 184 890 215 C899 242 891 263 896 284
      C899 309 915 307 930 322''')
    path(smoke,'lower-smoke-flourish','''M135 581
      C134 580 131 581 132 585 C140 596 148 608 153 624
      C143 620 131 610 126 610 C121 609 123 616 127 620
      C136 630 151 637 165 642 C178 663 194 670 217 670
      C239 670 255 660 264 655 C294 655 322 644 335 622
      C342 611 342 599 344 590 C361 578 369 565 367 550
      C366 536 355 521 346 515 C342 512 345 521 348 528
      C355 542 358 556 351 567 L344 577
      C344 569 346 561 343 559 C338 555 335 567 333 575 L328 590
      C306 600 288 610 272 627 C263 637 258 644 246 646
      C224 647 190 643 177 639 C167 635 164 625 160 614
      C154 598 144 585 135 581 Z
      M195 653 C208 655 226 655 236 655 C224 662 206 661 195 653 Z
      M280 643 C295 627 309 614 328 605 C321 628 305 641 280 643 Z''',fill=CREAM,fill_rule='evenodd')
    letters=layer(root,'main-lettering','04 · Hand-built display lettering',fill=CREAM,fill_rule='evenodd')
    tg=E(letters,'g',id='word-dont',transform='translate(460 405) rotate(-21) translate(-417 -340)',aria_label="DON'T")
    for k,d in TOP.items(): path(tg,'dont-'+k.lower(),d)
    dg=E(letters,'g',id='word-drop',transform='translate(715 805) rotate(-21) translate(-339 -270)',aria_label='DROP')
    for k,d in DROP.items():path(dg,'drop-'+k.lower(),d)
    ig=E(letters,'g',id='word-it',transform='translate(880 990) rotate(-21) translate(-237 -203)',aria_label='IT')
    path(ig,'it-i','M121 99 L169 99 L170 252 L124 252 Z')
    path(ig,'it-t','M190 99 L305 99 L305 130 L273 130 L272 253 L225 253 L225 131 L190 131 Z')
    eg=E(letters,'g',id='exclamation')
    path(eg,'exclamation-stem','''M1043 569 C1059 569 1063 589 1062 622
       C1061 704 1036 834 1005 904 C1001 914 995 918 983 914
       C978 913 977 906 978 888 C978 842 983 781 990 728
       C998 662 1007 604 1024 579 C1030 571 1036 568 1043 569 Z''')
    E(eg,'circle',id='exclamation-dot',cx=979.32,cy=966.87,r=27.6)
    cig=layer(root,'cigarette','05 · Cigarette and end details')
    path(cig,'paper-wrapper','''M213 805 L895 355
      C900 351 903 352 910 355 C939 367 956 405 956 433
      C956 442 954 449 948 453 L276 893
      C263 904 244 892 228 873 C213 852 198 832 204 816
      C206 811 209 808 213 805 Z''',fill=CREAM)
    mg=E(cig,'g',id='left-cut-end')
    path(mg,'left-end-inset','''M234 814 C237 813 239 817 242 818
      C249 823 256 833 262 845 C270 858 276 873 276 883
      C277 889 273 892 270 892 C258 889 240 873 233 861
      C226 850 222 838 222 828 C223 821 227 817 231 817 Z''',fill=GREEN)
    # Stylized tobacco flecks: deliberately redrawn marks, not raster noise.
    flecks=[
     'M224 819 L229 823 L231 823 L232 829 L239 828 L242 833 L242 838 L237 839 L236 835 L232 838 L235 842 L243 842 L245 847 L242 852 L246 856 L243 861 L237 861 L235 866 L229 863 L225 858 L220 857 L219 852 L213 850 L214 845 L211 842 L216 838 L211 834 L215 830 L221 831 L224 829 L220 825 Z',
     'M240 865 C243 862 246 864 247 867 C247 870 244 870 242 869 Z',
     'M247 870 C248 867 252 868 254 871 L252 874 L247 873 Z',
     'M252 878 L257 875 L260 877 L264 875 L268 879 L266 883 L260 882 L257 884 Z',
     'M269 885 C271 883 273 884 273 887 L270 889 L267 887 Z',
    ]
    for i,d in enumerate(flecks):path(mg,f'tobacco-fleck-{i+1}',d,fill=CREAM)
    ash=E(cig,'g',id='right-ash-end')
    path(ash,'ash-silhouette','''M910 350 C911 343 918 337 923 337 L932 340
      C938 338 940 330 947 328 L955 329 C961 322 970 317 975 321
      L979 327 C984 331 989 331 992 336 L995 349
      L1002 362 C1006 367 1006 374 1005 379 L1009 391 L1011 403
      C1010 408 1002 410 1000 415 L991 415 L985 422
      C979 424 977 416 973 414 L971 431 C967 435 962 436 959 431
      L956 415 L952 401 L947 386 L935 369
      C926 359 917 353 910 350 Z''',fill=CREAM)
    path(ash,'ash-central-opening','''M966 357 L968 363 L966 366 L971 369 L971 376
      L966 378 L967 385 L963 389 L960 385 L957 393 L959 399
      L961 404 L965 399 L969 402 L973 397 L978 397 L980 391
      L978 385 L981 380 L980 374 L974 371 L974 366 L969 361 Z''',fill=GREEN)
    path(ash,'ash-lower-gap','''M951 398 C953 404 959 409 966 410
      L975 415 L977 411 L968 406 L962 405 L957 396 Z''',fill=GREEN)
    path(ash,'ash-speck-upper','M943 350 L946 347 L949 350 L947 353 L944 353 Z',fill=GREEN)
    path(ash,'ash-speck-lower','M989 391 C992 391 993 394 991 397 L987 396 L987 393 Z',fill=GREEN)
    foot=layer(root,'credit','06 · Curved Forest Service credit')
    add_footer(foot,fontpath,live)
    return root


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=Path.cwd())
    ap.add_argument('--font',type=Path,default=Path('/usr/share/fonts/truetype/lato/Lato-Heavy.ttf'))
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    if not args.font.exists(): raise SystemExit('Supply a local Lato-Heavy TTF file with --font. Font files are not included.')
    for live,suffix in [(False,''),(True,'-live-footer')]:
        root=build(str(args.font),live)
        svg=args.out/f'dont-drop-it-forest-service{suffix}.svg'
        svg.write_bytes(ET.tostring(root,pretty_print=True,encoding='UTF-8',xml_declaration=True))
    master=args.out/'dont-drop-it-forest-service.svg'
    cairosvg.svg2png(url=str(master),write_to=str(args.out/'dont-drop-it-forest-service.png'),output_width=3762,output_height=3762)
    cairosvg.svg2png(url=str(master),write_to=str(args.out/'preview.png'),output_width=1254,output_height=1254)
    # Set an explicit square 12-inch page. All artwork remains vector.
    cairosvg.svg2pdf(url=str(master),write_to=str(args.out/'dont-drop-it-forest-service.pdf'),output_width=1152,output_height=1152)

if __name__=='__main__': main()
