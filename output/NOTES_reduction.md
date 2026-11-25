# Ave Maria + Prelude in C reduced to a harmonic accompaniment

Deliverable: `output/score_reduction__avepreludec.mscz` (also `.mscx`, `.pdf`).

## Arrangement
- **Violin** - the Ave Maria melody, all 36 measures, unchanged from the transcription of the class PDF; chord symbols kept above it.
- **Piano** (grand staff) - the Prelude in C reduced to a harmonic accompaniment:
  - **Left hand = the original bass part**, pitch for pitch and rhythm for rhythm (half notes C4 C4 B3 C4 ... G2 ... C2; whole notes C2 at the end).
    This is the harmonic foundation. In m23 the bass moves G2 -> B2 and in m24 it is Ab2, as engraved.
  - **Right hand = block chords**, one per half measure (the bass's harmonic rhythm). Each chord collects the tones of the
    original arpeggio of that measure (the upper left-hand note + the 3-note right-hand cell), same pitch classes and spelling,
    in close position from middle C upward.
  - m34-35 (the two bars of running 16ths) are reduced to the chords they outline: F | Dm and G7 | G7, over the held C2.
  - m36: final chord E4-G4-C5 over C3 + C2, with fermata.
- Dynamics: Violin mp, Piano p. Tempo quarter = 48, 4/4, C major, as in the source.

## Why these instruments
A violin sings the long, vocal-style melody (range G4-E6 fits comfortably); a piano can hold sustained chords above a low
bass line, so the Bach harmony is preserved without the busy arpeggios competing with the melody.

## How it was made
`work/make_score_json.py` (transcription of the PDF) -> `work/make_reduction_json.py` (reduction rules above, no re-reading
of the PDF) -> `work/score_reduction.json` -> `generate_mscx.py` -> `.mscx` -> MuseScore 3.2.3 CLI (`QT_QPA_PLATFORM=offscreen`)
-> `.mscz` / `.pdf`. All measures sum to 4/4 (checked by the generator).

## Notes
- The composer line says Gounod (1818-1893); the original PDF has "1983", an apparent typo, which I corrected here.
- The m23 measure labelled "Who added this ?" in the source PDF has no chord symbol; its harmony is reduced like the others.
