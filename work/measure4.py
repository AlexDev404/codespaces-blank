"""Measuring aid: pitch of stem-down hollow heads (lower voice half notes) in the harp bass staff."""
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
        y = int(round(y)); clr = ~im[y-5,:] & ~im[y+5,:]
        for yy in range(y-2,y+3): nl[yy,clr] = False
LET='CDEFGAB'
def name(p):
    idx = 3*7+5 - round(p); return f'{LET[idx%7]}{idx//7}'
er = ndi.binary_erosion(im, structure=np.ones((9,9),bool))
lab,_ = ndi.label(er)
filled = [((sl[1].start+sl[1].stop-1)/2,(sl[0].start+sl[0].stop-1)/2) for sl in ndi.find_objects(lab)]
for sysi in range(len(staves)//3):
    s = staves[3*sysi+2]
    y0, y1 = int(s[0]-45), int(s[4]+90)
    sub = nl[y0:y1,:]
    out=[]
    x=150
    while x<2960:
        col=sub[:,x]
        d=np.diff(np.concatenate([[0],col.view(np.int8),[0]]))
        st=np.where(d==1)[0]; en=np.where(d==-1)[0]
        hit=None
        for a,b in zip(st,en):
            if 40<=b-a<=66: hit=(a+y0,b+y0); break
        if hit:
            a,b=hit
            near=any(abs(fx-(x))<16 and (a-8<fy<b+8) for fx,fy in filled)
            if not near:
                # ring to the right of stem: columns x+5..x+24, rows a-4..a+24
                win = nl[a-4:a+24, x+6:x+24]
                ys=np.where(win.any(axis=1))[0]
                if len(ys):
                    top=ys.min()+a-4; bot=ys.max()+a-4
                    cy=(top+bot)/2
                    out.append((x, round((cy-s[0])/(sp/2),1), name((cy-s[0])/(sp/2))))
            x+=6
        else: x+=1
    print(f'page {pg} sys {sysi+1}:', out)
