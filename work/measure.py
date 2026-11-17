"""Measuring aid (not part of the deliverable): finds staves and filled noteheads in a page raster
and prints each head's diatonic step relative to its staff, to double-check hand reading."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

pg = sys.argv[1]
im = np.array(Image.open(f'work/am/pg-{pg}.png').convert('L')) < 128
H, W = im.shape
# staff lines: rows where a long horizontal run of dark exists
rows = np.where(im[:, 200:2900].sum(axis=1) > 0.6 * 2700)[0]
# merge adjacent rows into line centres
lines = []
for r in rows:
    if lines and r - lines[-1][-1] <= 2: lines[-1].append(r)
    else: lines.append([r])
cent = [np.mean(l) for l in lines]
staves = [cent[i:i+5] for i in range(0, len(cent) - 4, 5)]
print('staves:', len(staves))
# barlines: columns dark across whole staff height
# heads: erode to remove thin things
st = np.ones((9, 9), bool)
er = ndi.binary_erosion(im, structure=st)
lab, n = ndi.label(er)
objs = ndi.find_objects(lab)
heads = []
for i, sl in enumerate(objs):
    cy = (sl[0].start + sl[0].stop - 1) / 2; cx = (sl[1].start + sl[1].stop - 1) / 2
    heads.append((cx, cy, sl[0].stop - sl[0].start, sl[1].stop - sl[1].start))
for si, s in enumerate(staves):
    sp = (s[4] - s[0]) / 4
    print(f'--- staff {si} top={s[0]:.0f} spacing={sp:.1f}')
    out = []
    for cx, cy, h, w in sorted(heads):
        # step relative to top line, in half-spacings (positive = down)
        if s[0] - 6 * sp < cy < s[4] + 6 * sp and (si % 3 != 0 or True):
            # assign to nearest staff
            d = min(range(len(staves)), key=lambda k: abs(cy - (staves[k][0] + staves[k][4]) / 2))
            if d != si: continue
            out.append((round(cx), round((cy - s[0]) / (sp / 2), 1)))
    print(out)
