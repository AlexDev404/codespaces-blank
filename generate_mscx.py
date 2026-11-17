#!/usr/bin/env python3
"""Generate output/score__avepreludec.mscx (MuseScore 3.x format, learned from real MuseScore 3.2.3 exports)
from work/score.json.  Standard library only.  Musical content lives in score.json; this file only writes XML.

score.json token syntax: see work/make_score_json.py (e.g. 'G4:16', 'E4:8.~', 'E4+G4+C5:1^', 'r:8').
"""
import json
import sys
import xml.etree.ElementTree as ET
from datetime import date
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "work" / "score.json"
SUFFIX = "__avepreludec"
OUT = ROOT / "output" / f"score{SUFFIX}.mscx"

DIV = 480  # ticks per quarter
DUR_NAME = {1: "whole", 2: "half", 4: "quarter", 8: "eighth", 16: "16th"}
STEP_SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
STEP_TPC = {"F": 13, "C": 14, "G": 15, "D": 16, "A": 17, "E": 18, "B": 19}  # natural tpc; +7 per sharp, -7 per flat
REST_LIFT = -3  # sp: lifts the left-hand voice-1 rests clear of the voice-2 half notes


def dur_fraction(d, dots):
    f = Fraction(1, d)
    return f * 2 - f / (2 ** dots) if dots else f


def parse_pitch(tok):
    step, i, alter = tok[0], 1, 0
    while i < len(tok) and tok[i] in "#b":
        alter += 1 if tok[i] == "#" else -1
        i += 1
    octave = int(tok[i:])
    return 12 * (octave + 1) + STEP_SEMI[step] + alter, STEP_TPC[step] + 7 * alter


def tpc_of(name):  # chord root/bass letter (optionally with #/b) -> tpc
    return STEP_TPC[name[0]] + 7 * (name.count("#") - name.count("b"))


def parse_voice(text):
    """'G4:16 E4:8.~ E4+G4:1^ r:8' -> list of events."""
    events = []
    for tok in text.split():
        head, dur = tok.split(":")
        fermata = dur.endswith("^")
        dur = dur.rstrip("^")
        tie = dur.endswith("~")
        dur = dur.rstrip("~")
        dots = dur.count(".")
        d = int(dur.rstrip("."))
        ev = {"d": d, "dots": dots, "frac": dur_fraction(d, dots), "tie": tie, "fermata": fermata}
        if head == "r":
            ev["rest"] = True
        else:
            ev["notes"] = [parse_pitch(p) for p in head.split("+")]
        events.append(ev)
    return events


def sub(parent, tag, text=None):
    e = ET.SubElement(parent, tag)
    if text is not None:
        e.text = str(text)
    return e


def write_voice(measure_el, events, extras=None, lift_rests=False):
    voice = sub(measure_el, "voice")
    if extras:
        extras(voice)
    for i, ev in enumerate(events):
        if ev.get("rest"):
            r = sub(voice, "Rest")
            if lift_rests:
                o = sub(r, "offset"); o.set("x", "0"); o.set("y", str(REST_LIFT))
            if ev["dots"]:
                sub(r, "dots", ev["dots"])
            sub(r, "durationType", DUR_NAME[ev["d"]])
            continue
        if ev["fermata"]:
            f = sub(voice, "Fermata"); sub(f, "subtype", "fermataAbove")
        c = sub(voice, "Chord")
        if ev["dots"]:
            sub(c, "dots", ev["dots"])
        sub(c, "durationType", DUR_NAME[ev["d"]])
        prev = events[i - 1] if i > 0 else None
        prev_tied = bool(prev and prev["tie"] and not prev.get("rest"))
        for midi, tpc in ev["notes"]:
            n = sub(c, "Note")
            if prev_tied:  # this note ends a tie from the previous chord
                sp = sub(n, "Spanner"); sp.set("type", "Tie")
                loc = sub(sub(sp, "prev"), "location")
                sub(loc, "fractions", -prev["frac"])
            if ev["tie"]:  # this note starts a tie into the next chord
                sp = sub(n, "Spanner"); sp.set("type", "Tie")
                sub(sp, "Tie")
                loc = sub(sub(sp, "next"), "location")
                sub(loc, "fractions", ev["frac"])
            sub(n, "pitch", midi)
            sub(n, "tpc", tpc)
    return voice


def write_harmony(parent, ch):
    h = sub(parent, "Harmony")
    sub(h, "root", tpc_of(ch["root"]))
    if ch["name"]:
        sub(h, "name", ch["name"])
    if ch["bass"]:
        sub(h, "base", tpc_of(ch["bass"]))


def check_measure(where, events, expected):
    total = sum(e["frac"] for e in events)
    if total != expected:
        sys.exit(f"DURATION ERROR {where}: {total} != {expected}")


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    ts = data["time_signature"]
    expected = Fraction(ts["beats"], ts["beat_type"])
    measures = data["measures"]

    root = ET.Element("museScore", version="3.01")
    sub(root, "programVersion", "3.2.3")
    sub(root, "programRevision", "d2d863f")
    score = sub(root, "Score")
    lt = sub(score, "LayerTag"); lt.set("id", "0"); lt.set("tag", "default")
    sub(score, "currentLayer", 0)
    sub(score, "Division", DIV)
    style = sub(score, "Style")
    sub(style, "pageWidth", "11.6929")   # landscape A4 (inches), as in the source PDF
    sub(style, "pageHeight", "8.26772")
    sub(style, "pagePrintableWidth", "10.6929")
    for k in ("pageEvenLeftMargin", "pageOddLeftMargin", "pageEvenTopMargin", "pageOddTopMargin",
              "pageEvenBottomMargin", "pageOddBottomMargin"):
        sub(style, k, "0.5")
    sub(style, "Spatium", "1.2")
    sub(style, "measureSpacing", "1.0")
    sub(style, "minNoteDistance", "0.4")
    sub(score, "showInvisible", 1)
    sub(score, "showUnprintable", 1)
    sub(score, "showFrames", 1)
    sub(score, "showMargins", 0)
    flat = lambda s: s.replace("\n", " ")
    for name, val in [("arranger", ""), ("composer", flat(data["composer"])),
                      ("copyright", flat(data["copyright"])), ("creationDate", date.today().isoformat()),
                      ("lyricist", flat(data["lyricist"])), ("movementNumber", ""),
                      ("movementTitle", ""), ("platform", "Linux"), ("poet", ""), ("source", ""),
                      ("translator", ""), ("workNumber", ""), ("workTitle", data["title"])]:
        m = sub(score, "metaTag", val); m.set("name", name)

    # ---- parts / staves ----
    staff_clefs = []  # global staff index -> clef letter
    for part in data["parts"]:
        pe = sub(score, "Part")
        first = len(staff_clefs) + 1
        n = len(part["staves"])
        for k, clef in enumerate(part["staves"]):
            st = sub(pe, "Staff"); st.set("id", str(first + k))
            stt = sub(st, "StaffType"); stt.set("group", "pitched")
            sub(stt, "name", "stdNormal")
            if k == 0 and n > 1:
                br = sub(st, "bracket"); br.set("type", "1"); br.set("span", str(n)); br.set("col", "0")
                sub(st, "barLineSpan", n)
            staff_clefs.append(clef)
        sub(pe, "trackName", part["name"])
        inst = sub(pe, "Instrument"); inst.set("id", part["instrument"])
        sub(inst, "longName", part["name"])
        sub(inst, "shortName", part["short"])
        sub(inst, "trackName", part["name"])
        lo, hi = (23, 104) if part["instrument"] == "harp" else (36, 94)
        sub(inst, "minPitchP", lo); sub(inst, "maxPitchP", hi)
        sub(inst, "minPitchA", lo); sub(inst, "maxPitchA", hi)
        if n > 1:
            cl = sub(inst, "clef", part["staves"][1]); cl.set("staff", "2")
        ch = sub(inst, "Channel")
        pr = sub(ch, "program"); pr.set("value", str(part["program"]))
        sub(ch, "synti", "Fluid")

    line_breaks = set(data.get("line_breaks_after_measures", []))
    page_breaks = set(data.get("page_breaks_after_measures", []))
    tempo = data["tempo"]
    sym = {"quarter": "metNoteQuarterUp", "half": "metNoteHalfUp", "eighth": "metNote8thUp"}[tempo["unit"]]
    keys = ["voice", "harp_rh", "harp_lh"]

    for si, key in enumerate(keys):
        st = sub(score, "Staff"); st.set("id", str(si + 1))
        if si == 0:
            vb = sub(st, "VBox")
            sub(vb, "height", 10)
            for style_name, txt in (("Title", data["title"]), ("Composer", data["composer"]),
                                    ("Lyricist", data["lyricist"])):
                t = sub(vb, "Text"); sub(t, "style", style_name)
                sub(t, "text").text = txt
        for mi, m in enumerate(measures, start=1):
            me = sub(st, "Measure")
            if si == 0:
                if mi in line_breaks:
                    lb = sub(me, "LayoutBreak"); sub(lb, "subtype", "line")
                if mi in page_breaks:
                    lb = sub(me, "LayoutBreak"); sub(lb, "subtype", "page")
            voices = [parse_voice(v) for v in m[key]]
            for vi, ev in enumerate(voices, start=1):
                check_measure(f"m{mi} {key} voice{vi}", ev, expected)

            def first_voice_extras(voice, _mi=mi, _si=si, _m=m):
                clef_change = _m.get("harp_rh_clef") if _si == 1 else None
                if _mi == 1 or clef_change:
                    letter = staff_clefs[_si] if _mi == 1 else clef_change
                    c = sub(voice, "Clef")
                    sub(c, "concertClefType", letter)
                    sub(c, "transposingClefType", letter)
                if _mi == 1:
                    if data["key_fifths"]:  # C major needs no explicit KeySig
                        k = sub(voice, "KeySig"); sub(k, "accidental", data["key_fifths"])
                    t = sub(voice, "TimeSig")
                    if ts.get("common_time"):
                        sub(t, "subtype", 1)
                    sub(t, "sigN", ts["beats"]); sub(t, "sigD", ts["beat_type"])
                if _mi == 1 and _si == 0:
                    tp = sub(voice, "Tempo")
                    sub(tp, "tempo", tempo["bpm"] / 60)
                    sub(tp, "followText", 1)
                    tx = sub(tp, "text")
                    s = ET.SubElement(tx, "sym"); s.text = sym
                    s.tail = f" = {tempo['bpm']}"
                if _si == 0 and _m.get("chord"):
                    write_harmony(voice, _m["chord"])
                if _si == 1 and _m.get("harp_rh_text"):
                    stx = sub(voice, "StaffText"); sub(stx, "text", _m["harp_rh_text"])

            for vi, ev in enumerate(voices):
                write_voice(me, ev, first_voice_extras if vi == 0 else None,
                            lift_rests=(key == "harp_lh" and vi == 0))
            # second chord symbol part-way through a measure (written after the notes, relative location)
            if si == 0 and m.get("chord2"):
                at = Fraction(m["chord2"]["at"])
                vo = me.findall("voice")[0]
                loc = sub(vo, "location"); sub(loc, "fractions", at - expected)
                write_harmony(vo, m["chord2"])
                loc = sub(vo, "location"); sub(loc, "fractions", expected - at)

    ET.indent(root, space="  ")
    OUT.parent.mkdir(exist_ok=True)
    ET.ElementTree(root).write(OUT, encoding="UTF-8", xml_declaration=True)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes), {len(measures)} measures, all voices = {expected}")


if __name__ == "__main__":
    main()
