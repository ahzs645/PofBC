import sys, pymupdf
for f in sys.argv[1:]:
    try: d=pymupdf.open(f)
    except Exception as e: print(f,'ERR',e); continue
    print('==',f,len(d),'pages', d.metadata.get('creationDate'), d.metadata.get('producer'))
    pages=list(range(min(3,len(d))))+list(range(max(3,len(d)-2),len(d)))
    for i in pages:
        p=d[i]
        imgs=p.get_image_info()
        dr=p.get_drawings()
        fills=[x for x in dr if x.get('fill')]
        cols=sorted(set(tuple(round(c,2) for c in x['fill']) for x in fills))[:8]
        print(f' p{i+1}: imgs={[(round(b["bbox"][0]),round(b["bbox"][1]),round(b["bbox"][2]),round(b["bbox"][3]),b["width"],b["height"]) for b in imgs][:5]} drawings={len(dr)} fillcols={cols}')
