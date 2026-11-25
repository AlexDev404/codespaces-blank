#!/usr/bin/env python3
"""Reduce the Bach Prelude in C part of the Ave Maria arrangement to a harmonic accompaniment -> work/score_reduction.json.

Assignment: notate all 36 measures of Ave Maria and reduce Prelude in C Major to a harmonic accompaniment,
*retaining its original bass part* as the harmonic foundation.

Method (uses only the transcription in make_score_json.py - nothing is re-read from the PDF):
  * Melody (Ave Maria): unchanged, 36 measures, played by Violin.  Chord symbols kept above the melody.
  * Bass: the original lower voice of the harp left hand (the half notes C4 C4 B3 ... G2 ... C2), unchanged pitches and
    rhythm, written in the piano left hand.
  * Harmony: the arpeggio (upper LH note + 3-note RH cell of every measure) is collapsed into block chords, one chord per
    half measure (the harmonic rhythm of the bass).  Chord tones keep their original pitch classes and are put in
    close position at or above middle C (so they sit in the piano right hand, above the bass).
    m34-35 (the two bars of running 16ths) are reduced to the chords they outline: F | Dm and G7 | G7.
    m36 = final chord over C3 + C2 with fermata, as in the source.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import make_score_json as src  # noqa: E402  (the transcription)

STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi(p):
    s, i, alt = p[0], 1, 0
    while p[i] in "#b":
        alt += 1 if p[i] == "#" else -1
        i += 1
    return 12 * (int(p[i:]) + 1) + STEP[s] + alt


def spell(p_orig, m):
    """MIDI m written with the accidental style of the original pitch p_orig (sharp or flat key colour)."""
    flat = "b" in p_orig[1:2]
    if not flat:
        return f"{NAMES_SHARP[m % 12]}{m // 12 - 1}"
    flats = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
    return f"{flats[m % 12]}{m // 12 - 1}"


def close_position(pitches, floor=60):
    """Keep pitch classes (and their original spelling); lift every tone to >= floor (middle C); sorted, no duplicates."""
    out = {}
    for p in pitches:
        m = midi(p)
        while m < floor:
            m += 12
        out.setdefault(m, spell(p, m))
    return [out[m] for m in sorted(out)]


def chord_tok(pitches, dur, extra=""):
    return "+".join(pitches) + f":{dur}{extra}"


measures = []
for i in range(36):
    ch = src.CHORDS[i]
    if i < 33:
        tones = close_position([src.UPPER[i]] + src.RH[i])
        half = chord_tok(tones, 2)
        rh = [f"{half} {half}"]
        lo = src.LOWER[i].split("/")
        lh = [f"{lo[0]}:2 {lo[-1]}:2"]
    elif i == 33:   # F/C (beats 1-2) then Dm (beats 3-4); bass C2 held the whole bar
        rh = [chord_tok(["C4", "F4", "A4"], 2) + " " + chord_tok(["D4", "F4", "A4"], 2)]
        lh = ["C2:1"]
    elif i == 34:   # G7/C: both halves G7, bass C2 held
        g7 = chord_tok(["G4", "B4", "D5", "F5"], 2)
        rh = [f"{g7} {g7}"]
        lh = ["C2:1"]
    else:           # final chord, fermata
        rh = ["E4+G4+C5:1^"]
        lh = ["C3:1^", "C2:1"]
    m = {"chord": ch, "melody": [src.VOICE[i]], "piano_rh": rh, "piano_lh": lh}
    if i == 33:
        m["chord2"] = {"at": "1/2", **src.C("D", "m")}
    measures.append(m)

score = {
    "title": "Ave Maria",
    "composer": "Charles Gounod (1818-1893)\nJ.S Bach (1685-1750)\nPrelude in C reduced to a harmonic accompaniment",
    "lyricist": "Instructor:\nHerng-Yow Chen (陳恒佑)",
    "copyright": src.score["copyright"],
    "time_signature": src.score["time_signature"],
    "key_fifths": 0,
    "tempo": src.score["tempo"],
    "spatium": 1.5,
    "dynamics": {"melody": "mp", "piano_rh": "p", "piano_lh": "p"},
    "staff_keys": ["melody", "piano_rh", "piano_lh"],
    "parts": [
        {"name": "Violin", "short": "Vln.", "instrument": "violin", "program": 40, "range": [55, 103], "staves": ["G"]},
        {"name": "Piano", "short": "Pno.", "instrument": "piano", "program": 0, "range": [21, 108], "staves": ["G", "F"]},
    ],
    "line_breaks_after_measures": [6, 12, 24, 30],
    "page_breaks_after_measures": [18],
    "measures": measures,
}

if __name__ == "__main__":
    out = HERE / "score_reduction.json"
    out.write_text(json.dumps(score, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out, len(measures), "measures")
    for i in (0, 9, 11, 20, 21, 32, 33, 34, 35):
        print(f"m{i+1}: RH {measures[i]['piano_rh'][0]}   LH {measures[i]['piano_lh']}")
