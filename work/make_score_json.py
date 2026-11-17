#!/usr/bin/env python3
"""Transcription of input/ave_maria.pdf (Ave Maria / Bach Prelude in C, 36 measures) -> work/score.json.

This file only records *musical facts read from the PDF* (pitches, rhythms, chords, text). It contains no XML.
Token syntax used in score.json (parsed by generate_mscx.py):
    PITCH[#|b]OCT:DUR[.][~][^]   e.g. G4:16  E4:8.~  C5:2~  E4+G4+C5:1^
    r:DUR                        rest
    DUR: 1=whole 2=half 4=quarter 8=eighth 16=16th ; '.' = dotted ; '~' = tied to next chord ;
    '^' = fermata ; 'A+B' = chord (several pitches).
Harp texture (Bach prelude): each measure of the right hand is two identical half-measures
    r:8 a b c a b c   (a b c = rising arpeggio of 16ths);
the left hand has voice 1 = (r:16 X:8.~ X:4) x2 (upper pitch X) and voice 2 = two half notes (bass pitch).
"""
import json
from pathlib import Path

# ---- harp right hand: 3-note arpeggio cell per measure (m1..m33) ----
RH = """G4 C5 E5 | A4 D5 F5 | G4 D5 F5 | G4 C5 E5 | A4 E5 A5 | F#4 A4 D5 |
G4 D5 G5 | E4 G4 C5 | E4 G4 C5 | D4 F#4 C5 | D4 G4 B4 | E4 G4 C#5 |
D4 A4 D5 | D4 F4 B4 | C4 G4 C5 | A3 C4 F4 | A3 C4 F4 | G3 B3 F4 |
G3 C4 E4 | Bb3 C4 E4 | A3 C4 E4 | A3 C4 Eb4 | B3 C4 Eb4 | B3 C4 D4 |
G3 B3 D4 | G3 C4 E4 | G3 C4 F4 | G3 B3 F4 | A3 C4 F#4 | G3 C4 G4 |
G3 C4 F4 | G3 B3 F4 | G3 Bb3 E4"""
RH = [c.split() for c in " ".join(RH.split()).split(" | ")]
assert len(RH) == 33

# ---- harp left hand: upper (voice 1, dotted-8th tied to quarter) and lower (voice 2, half notes) ----
UPPER = "E4 D4 D4 E4 E4 D4 D4 C4 C4 A3 B3 Bb3 A3 Ab3 G3 F3 F3 D3 E3 G3 F3 C3 Eb3 F3 F3 E3 D3 D3 Eb3 E3 D3 D3 C3".split()
LOWER = ("C4 C4 B3 C4 C4 C4 B3 B3 A3 D3 G3 G3 F3 F3 E3 E3 D3 G2 C3 C3 F2 F#2 G2/B2 Ab2 "
         "G2 G2 G2 G2 G2 G2 G2 G2 C2").split()
assert len(UPPER) == 33 and len(LOWER) == 33

# ---- voice (melody), one token string per measure ----
VOICE = [
    "E5:1",
    "F5:2. F5:4",
    "G5:2. D5:4",
    "E5:1",
    "A5:2~ A5:8 A4:8 B4:8 C5:8",
    "D5:4. E5:8 D5:2",
    "G5:2~ G5:8 G4:8 A4:8 B4:8",
    "C5:4. D5:8 C5:2",
    "C6:2~ C6:8 C5:8 D5:8 E5:8",
    "F#5:4. E5:8 D5:4 A4:4",
    "B4:2. D5:4",
    "E5:2~ E5:8 E5:8 F5:8 G5:8",
    "A5:4. A4:8 A4:2",
    "D5:2~ D5:8 D5:8 E5:8 F5:8",
    "G5:2 G4:2",
    "C5:2~ C5:8 C5:8 D5:8 E5:8",
    "F5:2~ F5:8 F5:8 G5:8 A5:8",
    "B5:4. A5:8 G5:4 D5:4",
    "E5:2~ E5:8 r:8 r:8 E5:8",
    "G5:2 E5:4. E5:8",
    "A5:2 A4:4 r:8 A5:8",
    "A5:2 C5:4 r:8 A5:8",
    "C6:2 Eb5:4 r:8 C6:8",
    "C6:2 D5:4 r:8 D5:8",
    "D5:2~ D5:8 D5:8 C5:8 B4:8",
    "G5:4. E5:8 C5:2",
    "F5:2~ F5:8 F5:8 E5:8 D5:8",
    "D6:4. B5:8 G5:2",
    "A5:2~ A5:8 A5:8 B5:8 C6:8",
    "E6:2~ E6:8 C6:8 G5:8 E5:8",
    "D5:2~ D5:8 A5:8 B5:8 A5:8",
    "G5:8 D6:8 B5:8 G5:8 F5:8 D5:8 B4:8 G4:8",
    "C5:1",
    "C5:1",
    "G5:1",
    "G5:1",
]

# ---- chord symbols: (root, suffix, bass) per measure; m34 has a second chord on beat 3 ----
C = lambda r, n="", b=None: {"root": r, "name": n, "bass": b}
CHORDS = [
    C("C"), C("D", "m7", "C"), C("G", "7", "B"), C("C"), C("A", "m", "C"), C("D", "7", "C"),
    C("G", "", "B"), C("C", "maj7", "B"), C("A", "m7"), C("D", "7"), C("G", "", "B"), C("G", "dim7"),
    C("D", "m", "F"), C("F", "dim7"), C("C", "", "E"), C("F", "maj7", "E"), C("D", "m7"), C("G", "7"),
    C("C"), C("C", "7"), C("F", "maj7"), C("F#", "dim7"), None, C("Ab", "dim7"),
    C("G", "7"), C("C", "", "G"), C("G", "7sus4"), C("G", "7"), C("A", "dim7", "G"), C("C", "", "G"),
    C("G", "7sus4"), C("G", "7"), C("C", "7"), C("F", "", "C"), C("G", "7", "C"), C("C"),
]

# ---- measures 34-36 are special in the harp part ----
RH34 = ["r:8 F3:16 A3:16 C4:16 F4:16 C4:16 A3:16 C4:16 A3:16 F3:16 A3:16 F3:16 D3:16 F3:16 D3:16"]   # bass clef
RH35 = ["r:8 G4:16 B4:16 D5:16 F5:16 D5:16 B4:16 D5:16 B4:16 G4:16 B4:16 D4:16 F4:16 E4:16 D4:16"]   # treble clef again
RH36 = ["E4+G4+C5:1^"]


def hand_rh(i):  # i = 0-based measure index
    if i < 33:
        a, b, c = RH[i]
        half = f"r:8 {a}:16 {b}:16 {c}:16 {a}:16 {b}:16 {c}:16"
        return [half + " " + half]
    return [RH34, RH35, RH36][i - 33]


def hand_lh(i):
    if i < 33:
        x = UPPER[i]
        v1 = f"r:16 {x}:8.~ {x}:4 r:16 {x}:8.~ {x}:4"
        lo = LOWER[i].split("/")
        v2 = f"{lo[0]}:2 {lo[-1]}:2"
        return [v1, v2]
    if i == 33:
        return ["r:16 C3:8.~ C3:4~ C3:2", "C2:1"]
    if i == 34:
        return ["r:16 B2:8.~ B2:4~ B2:2", "C2:1"]
    return ["C3:1^", "C2:1"]


measures = []
for i in range(36):
    m = {"chord": CHORDS[i], "voice": [VOICE[i]], "harp_rh": hand_rh(i), "harp_lh": hand_lh(i)}
    if i == 33:
        m["chord2"] = {"at": "1/2", **C("D", "m")}
        m["harp_rh_clef"] = "F"
    if i == 34:
        m["harp_rh_clef"] = "G"
    if i == 22:
        m["harp_rh_text"] = "Who added this ?"
    measures.append(m)

score = {
    "title": "Ave Maria",
    "composer": "Charles Gounod (1818-1983)\nJ.S Bach (1685-1750)",
    "lyricist": "Instructor:\nHerng-Yow Chen (陳恒佑)",
    "copyright": "© Interactive Music Programming and Creation, National Chi Nan University, Taiwan, 2020\n(https://www.openedu.tw/course.jsp?id=990)",
    "time_signature": {"beats": 4, "beat_type": 4, "common_time": True},
    "key_fifths": 0,
    "tempo": {"unit": "quarter", "bpm": 48},
    "parts": [
        {"name": "Voice", "short": "Vo.", "instrument": "voice", "program": 52, "staves": ["G"]},
        {"name": "Harp", "short": "Hrp.", "instrument": "harp", "program": 46, "staves": ["G", "F"]},
    ],
    "line_breaks_after_measures": [6, 12, 24, 30],
    "page_breaks_after_measures": [18],
    "measures": measures,
}

if __name__ == "__main__":
    out = Path(__file__).parent / "score.json"
    out.write_text(json.dumps(score, ensure_ascii=False, indent=1), encoding="utf-8")
    print("wrote", out, len(measures), "measures")
