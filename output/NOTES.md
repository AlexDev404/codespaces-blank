# Ave Maria + Bach Prelude in C (36 measures) - transcription notes

Source: `input/ave_maria.pdf` (2 pages, landscape A4, 36 measures, 6 per system).
Deliverables (suffix `__avepreludec`): `score__avepreludec.mscx`, `.mscz`, `.pdf`
(+ `score__avepreludec_check-1/2.png`, `score__avepreludec_check.musicxml` for verification).

## Tooling
- MuseScore **3.2.3** (Ubuntu 24.04 apt `musescore3` 3.2.3+dfsg2-16build5), x86_64.
- MuseScore 4 AppImage route is blocked by network policy: the agent proxy returns 403 for
  `api.github.com/repos/musescore/MuseScore/...` (session GitHub access is limited to this repo). apt was used.
- Headless invocation (works without xvfb): `QT_QPA_PLATFORM=offscreen musescore3 -o <out> <in>`
- `.mscz` and `.pdf` were produced by the MuseScore CLI from the generated `.mscx`. No zip-fallback packaging was needed.
- Pipeline: `work/make_score_json.py` (transcription, no XML) -> `work/score.json` -> `generate_mscx.py` -> `.mscx` -> CLI.
- `setup_env.sh` reproduces the install. `work/measure*.py` are measuring aids I used to read note-head heights
  off the PDF raster (staff lines + filled heads + stems); pitches were then checked against the picture by eye.

## Instruments / parts
Two parts, as in the source: **Voice** (melody, treble clef) and **Harp** (accompaniment, grand staff).

## Verification
- Every voice of every measure sums to 4/4 (the generator aborts otherwise).
- PDF, PNG and MusicXML exports succeed; MusicXML parses (2 parts x 36 measures).
- Rendered pages compared with the source page by page: system breaks (6/6/6 per page), clefs, key (C), time (C),
  tempo (quarter = 48), pitches, rhythms, ties, accidentals, chord symbols, fermatas, text all match.

## Reading choices / ambiguities
- Left-hand pitches: voice 1 (16th rest, dotted 8th tied to quarter) and voice 2 (half notes) were read from
  staff positions; the lower note always equals the chord's bass note, which cross-checks the reading.
- m5/7/9: the tied half note is an octave above the following eighths (A5~A5 then A4 B4 C5; G5 then G4 A4 B4; C6 then
  C5 D5 E5) exactly as engraved.
- m23 (the measure with no chord symbol): lower voice G2 in beat 1-2 and B2 in beat 3-4 (as engraved), Eb3 above,
  RH B3 C4 Eb4. It is labelled "Who added this ?" in the source; kept as a staff text above the harp.
- m34-35: harp right hand switches to bass clef (m34) and back to treble (m35); 14 sixteenths after an 8th rest.
- m36: final chord E4 G4 C5 (RH) over C3 and C2 (LH), fermata on RH chord and LH upper note.
- Dm in m34 is a second chord symbol on beat 3 (stored as a relative-location Harmony).
- "Charles Gounod (1818-1983)" is copied literally from the source (the death year is a typo in the source: 1893).

## Not transcribed / differences
- Handwritten, boxed chord-symbol style and bold title/tempo styling: MuseScore default styles are used.
- Small size/spacing differences (Spatium 1.2 mm, landscape A4) were set only so the 6-measure systems fit.
- Substitute fonts in the headless render; judged on notation only.
