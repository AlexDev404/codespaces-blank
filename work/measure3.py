"""Measuring aid: find stem-down half notes (hollow heads) in the harp bass staff + voice staff by locating their stems."""
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
staves = [cent[i:i+5] for i in range(0, len(cent) - 4, 5)]
sp = (staves[0][4] - staves[0][0]) / 4
nl = im.copy()
for s in staves:
    for y in s:
        y = int(round(y)); clr = ~im[y-5, :] & ~im[y+5, :]
        for yy in range(y-2, y+3): nl[yy, clr] = False
LET = 'CDEFGAB'
def name(clef, p):
    topidx = 5*7+3 if clef == 'T' else 3*7+5
    idx = topidx - round(p)
    return f'{LET[idx%7]}{idx//7}'
er = ndi.binary_erosion(im, structure=np.ones((9, 9), bool))
lab, n = ndi.label(er)
filled = [((sl[1].start+sl[1].stop-1)/2, (sl[0].start+sl[0].stop-1)/2) for sl in ndi.find_objects(lab)]
for si, (s, clef) in enumerate([(staves[i], 'T' if i % 3 < 2 else 'B') for i in range(len(staves))]):
    kind = ['VOICE', 'HARP-R', 'HARP-L'][si % 3]
    if kind == 'HARP-R': continue
    y0, y1 = int(s[0] - 8*sp/2*1.0 - 14), int(s[4] + 8*sp/2*1.0 + 14)
    # vertical runs
    res = []
    sub = nl[y0:y1, :]
    # stems ~ 3px wide: use columns where run-length >= 40
    for x in range(150, 2960):
        col = sub[:, x]
        d = np.diff(np.concatenate([[0], col.view(np.int8), [0]]))
        starts = np.where(d == 1)[0]; ends = np.where(d == -1)[0]
        for a, b in zip(starts, ends):
            if 40 <= b - a <= 64: res.append((x, a + y0, b + y0))
    # group adjacent x
    groups = []
    for x, a, b in res:
        if groups and x - groups[-1][-1][0] <= 2 and abs(a - groups[-1][-1][1]) <= 2: groups[-1].append((x, a, b))
        else: groups.append([(x, a, b)])
    out = []
    for g in groups:
        x = np.mean([t[0] for t in g]); a = g[0][1]; b = g[0][2]
        # near a filled head? (stem up attaches to its right: head center x ~ stem x - 9)
        near = any(abs((fx) - x) < 16 and (fy > a - 8 and fy < b + 8) for fx, fy in filled)
        if near: continue
        # stem-down hollow: head center ~ a+5 ; stem-up hollow: head center ~ b-5 . report both
        out.append((round(x), name(clef, (a + 5 - s[0]) / (sp/2)), name(clef, (b - 5 - s[0]) / (sp/2))))
    print(f'sys{si//3+1} {kind}: (x, headIfStemDown, headIfStemUp)')
    print('  ', out)
