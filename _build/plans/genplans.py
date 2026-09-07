# -*- coding: utf-8 -*-
"""Generate one clean SVG floor plan per apartment from the architect's PDFs."""
import pymupdf, re, os, json

# ---------------------------------------------------------------- geometry
UP_OUT, LOW_OUT = 631.0, 208.0          # balcony outer edges (rot0 x)
CROP = {
 "I": (419, 55,  UP_OUT, 372),
 "A": (440, 516, UP_OUT, 741),
 "B": (440, 741, UP_OUT, 952),
 "C": (384, 952, UP_OUT, 1112),
 "H": (LOW_OUT, 55,  419, 372),
 "G": (LOW_OUT, 391, 398, 520),
 "F": (LOW_OUT, 520, 398, 662),
 "E": (LOW_OUT, 662, 398, 815),
 "D": (LOW_OUT, 815, 384, 1112),
}
CROP_1NP = dict(CROP); CROP_1NP.pop("I")
CROP_1NP["H"] = (378, 55, UP_OUT, 375)  # 1NP: no I, H sits on the upper side

# rooms: (name lines, [codes to sum], anchor spec)  anchor: int code | ("mid",a,b)
LIVING = ["Obývacia izba", "s kuchyňou"]
STUDIO = ["Obytná izba", "s kuchyňou"]
SCHEMA = {
 "A": [(LIVING,[3,4],("mid",3,4)), (["Spálňa"],[5],5), (["Predsieň"],[1],1), (["Kúpeľňa"],[6],6), (["WC"],[2],2)],
 "B": [(LIVING,[3,4],("mid",3,4)), (["Spálňa"],[5],5), (["Predsieň"],[1],1), (["Kúpeľňa"],[6],6), (["WC"],[2],2)],
 "C": [(LIVING,[4,5],("mid",4,5)), (["Spálňa"],[3],3), (["Predsieň"],[1],1), (["Kúpeľňa"],[2],2)],
 "D": [(LIVING,[5,6],("mid",5,6)), (["Spálňa"],[4],4), (["Predsieň"],[1],1), (["Kúpeľňa"],[2],2), (["Šatník"],[3],3)],
 "E": [(STUDIO,[1,3],("mid",1,3)), (["Kúpeľňa"],[2],2)],
 "F": [(STUDIO,[1,3],("mid",1,3)), (["Kúpeľňa"],[2],2)],
 "G": [(STUDIO,[1,3],("mid",1,3)), (["Kúpeľňa"],[2],2)],
 "H": [(LIVING,[4,5],("mid",4,5)), (["Spálňa"],[6],6), (["Spálňa"],[7],7), (["Predsieň"],[1],1),
       (["Kúpeľňa"],[2],2), (["Komora"],[3],3)],
 "I": [(LIVING,[4,5],("mid",4,5)), (["Spálňa"],[6],6), (["Spálňa"],[7],7), (["Predsieň"],[1],1),
       (["Kúpeľňa"],[2],2), (["Komora"],[3],3)],
}
UPPER = set("IABC")

# ---------------------------------------------------------------- svg helpers
def col(c):
    if c is None: return None
    return "#%02x%02x%02x" % tuple(round(v*255) for v in c)

def path_d(items, close):
    d=[]; cur=None
    def m(p):
        nonlocal cur
        if cur is None or abs(cur.x-p.x)>1e-3 or abs(cur.y-p.y)>1e-3:
            d.append("M%.1f %.1f"%(p.x,p.y))
    for op in items:
        k=op[0]
        if k=="l":
            a,b=op[1],op[2]; m(a); d.append("L%.1f %.1f"%(b.x,b.y)); cur=b
        elif k=="c":
            a,b,c,e=op[1],op[2],op[3],op[4]; m(a)
            d.append("C%.1f %.1f %.1f %.1f %.1f %.1f"%(b.x,b.y,c.x,c.y,e.x,e.y)); cur=e
        elif k=="re":
            r=op[1]; d.append("M%.1f %.1fH%.1fV%.1fH%.1fZ"%(r.x0,r.y0,r.x1,r.y1,r.x0)); cur=None
        elif k=="qu":
            q=op[1]; d.append("M%.1f %.1fL%.1f %.1fL%.1f %.1fL%.1f %.1fZ"%(
                q.ul.x,q.ul.y,q.ur.x,q.ur.y,q.lr.x,q.lr.y,q.ll.x,q.ll.y)); cur=None
    if close: d.append("Z")
    return "".join(d)

def codes_of(pdf):
    d=pymupdf.open(pdf); p=d[0]; p.set_rotation(0)
    pos={}; area={}
    words=[(w[4],(w[0]+w[2])/2,(w[1]+w[3])/2) for w in p.get_text("words")]
    C=[w for w in words if re.fullmatch(r"\.[A-I]\.\d",w[0])]
    A=[w for w in words if re.fullmatch(r"\d+,\d+m2",w[0])]
    bal=[a for a in A if a[1]<262 or a[1]>560]      # note: rot0 x
    inner=[a for a in A if a not in bal]
    # dedupe stray duplicates, then nearest-neighbour pair
    seen={}
    for t,x,y in C: seen.setdefault(t,[]).append((x,y))
    uniq=[]
    for t,v in seen.items():
        if len(v)==1: uniq.append((t,)+v[0]); continue
        best=min(v,key=lambda q:min((q[0]-a[1])**2+(q[1]-a[2])**2 for a in inner))
        uniq.append((t,)+best)
    used=set()
    for t,x,y in sorted(uniq):
        cand=[(((a[1]-x)*1.1)**2+(a[2]-y)**2, j) for j,a in enumerate(inner) if j not in used]
        _,j=min(cand); used.add(j)
        pos[t]=(x,y); area[t]=float(inner[j][0].replace("m2","").replace(",","."))
    balpos={}
    for t,x,y in bal:
        balpos.setdefault(("up" if x>560 else "low"),[]).append((float(t.replace("m2","").replace(",",".")),y))
    return pos, area, balpos

def build(pdf, letter, crop, pos, area, balcony, out, pad=5.0):
    doc=pymupdf.open(pdf); page=doc[0]; page.set_rotation(0)
    x0,y0,x1,y1=crop
    bx0,by0,bx1,by1 = x0-pad, y0-pad, x1+pad, y1+pad
    pw,ph = page.rect.width, page.rect.height
    body=[]
    for it in page.get_drawings():
        r=it["rect"]
        if r.is_infinite: continue
        if r.x1<bx0 or r.x0>bx1 or r.y1<by0 or r.y0>by1: continue
        if r.width>pw*0.92 and r.height>ph*0.92: continue
        d=path_d(it["items"], it.get("closePath"))
        if not d: continue
        f=col(it.get("fill")); s=col(it.get("color")); typ=it.get("type","s")
        a=['fill="%s"'%(f if (f and typ in ("f","fs")) else "none")]
        if s and typ in ("s","fs"):
            a.append('stroke="%s"'%s); a.append('stroke-width="%.2f"'%max(it.get("width") or .4,.35))
        else: a.append('stroke="none"')
        if it.get("even_odd"): a.append('fill-rule="evenodd"')
        body.append('<path %s d="%s"/>'%(" ".join(a),d))

    W=x1-x0; H=y1-y0
    inner=('<g transform="translate(0 %.1f) rotate(-90) translate(%.1f %.1f)">%s</g>'
           %(W,-x0,-y0,"".join(body)))

    def to_svg(lx,ly): return (ly-y0, W-(lx-x0))
    labels=[]
    for names, codes, anchor in SCHEMA[letter]:
        key=lambda n:".%s.%d"%(letter,n)
        if not all(key(c) in pos for c in codes): continue
        tot=sum(area[key(c)] for c in codes)
        if isinstance(anchor,tuple):
            ax=sum(pos[key(anchor[i])][0] for i in (1,2))/2
            ay=sum(pos[key(anchor[i])][1] for i in (1,2))/2
        else:
            ax,ay=pos[key(anchor)]
        labels.append((to_svg(ax,ay), names, tot))
    if balcony:
        bx = 607.0 if letter in UPPER else 231.0
        labels.append((to_svg(bx,(y0+y1)/2), ["Balkón"], balcony))

    FS, LH = 4.3, 5.3
    txt=[]
    for (sx,sy), names, tot in labels:
        area_s = ("%.1f"%tot).replace(".",",")+" m²"
        n=len(names)+1
        wide = max([len(x) for x in names]+[len(area_s)]) * FS * 0.55
        sx = min(max(sx, wide/2+3.0), H-wide/2-3.0)
        top = min(max(sy-(n-1)*LH/2, FS+3.0), W-(n-1)*LH-3.0)
        for i,ln in enumerate(names+[area_s]):
            cls = "ra" if i==len(names) else "rn"
            txt.append('<text class="%s" x="%.1f" y="%.1f">%s</text>'%(cls, sx, top+i*LH, ln))

    # width/height are required for <img> to get an intrinsic size — with only a
    # viewBox the image lays out 0px tall.
    svg=('<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f" '
         'viewBox="0 0 %.1f %.1f" '
         'preserveAspectRatio="xMidYMid meet" role="img" aria-label="Pôdorys bytu %s">'
         '<style>text{font-family:Inter,system-ui,-apple-system,sans-serif;text-anchor:middle;'
         'paint-order:stroke;stroke:#F7F4EF;stroke-width:2.2;stroke-linejoin:round}'
         '.rn{font-size:4.3px;font-weight:600;fill:#14120F}'
         '.ra{font-size:4px;font-weight:500;fill:#6E655B}</style>'
         '<rect width="100%%" height="100%%" fill="#F7F4EF"/>%s%s</svg>')%(H*4,W*4,H,W,letter,inner,"".join(txt))
    open(out,"w",encoding="utf-8").write(svg)
    return len(svg)

# ---------------------------------------------------------------- run
SRC=[("1np.pdf","1np",CROP_1NP), ("2 az 4 np.pdf","24np",CROP), ("5np.pdf","5np",CROP)]
os.makedirs("out",exist_ok=True)
meta={}
for pdf,tag,crops in SRC:
    pos,area,balpos = codes_of(pdf)
    for letter,crop in crops.items():
        side = "up" if letter in UPPER else "low"
        if tag=="1np" and letter=="H": side="up"
        mid=(crop[1]+crop[3])/2
        cands=balpos.get(side,[])
        bal=min(cands,key=lambda z:abs(z[1]-mid))[0] if cands else None
        f="out/plan-%s-%s.svg"%(tag,letter)
        n=build(pdf,letter,crop,pos,area,bal,f)
        rooms={k:v for k,v in area.items() if k.split(".")[1]==letter}
        meta.setdefault(tag,{})[letter]={"interior":round(sum(rooms.values()),1),"balcony":bal,
                                         "rooms":{k[3:]:v for k,v in sorted(rooms.items())},"svg":n}
json.dump(meta,open("plans_meta.json","w"),ensure_ascii=False,indent=1)
for tag in meta:
    print(tag, " ".join("%s:%.1f+%.1f"%(k,v["interior"],v["balcony"] or 0) for k,v in sorted(meta[tag].items())))
print("files:", len(os.listdir("out")), "avg KB:", round(sum(os.path.getsize("out/"+f) for f in os.listdir("out"))/len(os.listdir("out"))/1024,1))
