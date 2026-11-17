"""Measuring aid: hollow note heads on the voice staff (staff lines removed, enclosed interiors found)."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
pg = sys.argv[1]
im = np.array(Image.open(f'work/am/pg-{pg}.png').convert('L')) < 128
rows = np.where(im[:, 200:2900].sum(axis=1) > 0.6 * 2700)[0]
lines = []
for r in rows:
    if lines and r - lines[-1][-1] <= 2: lines[-1].append(r)
    else: lines.append([r])
cent = [np.mean(l) for l in lines]
staves = [cent[i:i+5] for i in range(0, len(cent)-4, 5)]
sp = (staves[0][4]-staves[0][0])/4
nl = im.copy()
for s in staves:
    for y in s:
        y=int(round(y)); clr=~im[y-5,:]&~im[y+5,:]
        for yy in range(y-2,y+3): nl[yy,clr]=False
holes = ndi.binary_fill_holes(nl) & ~nl
hl,_ = ndi.label(holes)
LET='CDEFGAB'
def name(p):
    idx=5*7+3-round(p); return f'{LET[idx%7]}{idx//7}'
bars_cache={}
for sysi in range(len(staves)//3):
    s=staves[3*sysi]; hs=staves[3*sysi+1]; hb=staves[3*sysi+2]
    out=[]
    for i,sl in enumerate(ndi.find_objects(hl)):
        h=sl[0].stop-sl[0].start; w=sl[1].stop-sl[1].start
        cy=(sl[0].start+sl[0].stop-1)/2; cx=(sl[1].start+sl[1].stop-1)/2
        if not (s[0]-5*sp < cy < s[4]+5*sp): continue
        area=(hl[sl]==i+1).sum()
        if 6<=h<=16 and 9<=w<=22 and 40<=area<=190:
            out.append((round(cx), name((cy-s[0])/(sp/2)), h, w, int(area)))
    print(f'page {pg} sys {sysi+1} voice hollow candidates:', sorted(out))
