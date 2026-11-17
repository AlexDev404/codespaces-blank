"""Measuring aid (not part of the deliverable): per system / measure / staff, list note heads (name w/o accidental).
Voice staff = treble, harp staves = treble + bass. f=filled head, h=hollow head."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi

pg = sys.argv[1]
im = np.array(Image.open(f'work/am/pg-{pg}.png').convert('L')) < 128
H, W = im.shape
rows = np.where(im[:, 200:2900].sum(axis=1) > 0.6 * 2700)[0]
lines = []
for r in rows:
    if lines and r - lines[-1][-1] <= 2: lines[-1].append(r)
    else: lines.append([r])
cent = [np.mean(l) for l in lines]
staves = [cent[i:i+5] for i in range(0, len(cent) - 4, 5)]
sp = (staves[0][4] - staves[0][0]) / 4

# remove staff lines
nl = im.copy()
for s in staves:
    for y in s:
        y = int(round(y))
        for yy in range(y - 2, y + 3):
            col_clear = ~im[y - 5, :] & ~im[y + 5, :]
            nl[yy, col_clear] = False
# filled heads
er = ndi.binary_erosion(im, structure=np.ones((9, 9), bool))
lab, n = ndi.label(er)
heads = []
for sl in ndi.find_objects(lab):
    heads.append(((sl[1].start + sl[1].stop - 1) / 2, (sl[0].start + sl[0].stop - 1) / 2, 'f'))
# barlines from voice staff of each system
def bars(si):
    y0, y1 = int(staves[si + 1][0]), int(staves[si + 2][4])
    colsum = im[y0:y1 + 1, :].sum(axis=0)
    xs = np.where(colsum >= (y1 - y0) * 0.98)[0]
    out = []
    for x in xs:
        if out and x - out[-1][-1] <= 3: out[-1].append(x)
        else: out.append([x])
    return [np.mean(o) for o in out]

LET = 'CDEFGAB'
def name(clef, p):
    # p = half-steps below top line -> diatonic steps below top note
    steps = round(p)
    top = (5, 4) if clef == 'T' else (5, 2)   # F5 for treble (letter idx F=3?) handled below
    # top line: treble F5 -> idx = 5*7+3 ; bass A3 -> 3*7+5
    topidx = 5 * 7 + 3 if clef == 'T' else 3 * 7 + 5
    idx = topidx - steps
    return f'{LET[idx % 7]}{idx // 7}'

for sysi in range(len(staves) // 3):
    v, ht, hb = staves[3 * sysi], staves[3 * sysi + 1], staves[3 * sysi + 2]
    bx = bars(3 * sysi)
    print(f'=== page {pg} system {sysi+1}: barlines at', [round(b) for b in bx])
    # measures: between consecutive barlines (first barline = system start bracket line)
    for mi in range(len(bx) - 1):
        x0, x1 = bx[mi], bx[mi + 1]
        line = []
        for lab_, s, clef in (('V', v, 'T'), ('R', ht, 'T'), ('L', hb, 'B')):
            hs = [(x, y, k) for x, y, k in heads if x0 < x < x1 and s[0] - 7 * sp / 2 * 2 < y < s[4] + 7 * sp / 2 * 2 + 0]
            # keep heads belonging to this staff (nearest staff center)
            cs = (s[0] + s[4]) / 2
            hs = [h for h in hs if min(range(len(staves)), key=lambda k: abs(h[1] - (staves[k][0] + staves[k][4]) / 2)) == staves.index(s)]
            hs.sort()
            line.append(lab_ + ': ' + ' '.join(f"{name(clef,(y - s[0]) / (sp/2))}{'' if k=='f' else '(h)'}" for x, y, k in hs))
        print(f'  m{mi+1} of sys: ' + ' | '.join(line))
