import sys, os, warnings, collections
import pymupdf as fitz
src=sys.argv[1]
for fn in sorted(os.listdir(src)):
    try: d=fitz.open(os.path.join(src,fn))
    except Exception: continue
    for pi in range(min(d.page_count,60)):
        try: dr=d[pi].get_drawings()
        except Exception: continue
        c=collections.Counter()
        for x in dr:
            if x.get('fill') and len(x['items'])>3:
                f=tuple(round(v,2) for v in x['fill']); c[f]+=1
        col=[(k,v) for k,v in c.items() if k not in [(0,0,0),(1,1,1)] and v>=3]
        if col: print(fn, 'p',pi+1, col[:6])
