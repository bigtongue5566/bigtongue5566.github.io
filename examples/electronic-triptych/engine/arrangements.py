"""Broken-beat and drum-and-bass studies with independent phrase and sound choices."""
import instruments as ins
from projectlib import section_at


def _hit(score, chord, offset, sound, pitch, gain, pan=0):
    start = chord["start"] + offset * score.beat
    if start >= chord["end"] or section_at(score.cfg, start)[1]["role"] not in ("groove", "build", "drop", "evolution"):
        return
    count = min(len(sound), round((chord["end"] - start) * score.sr))
    score.add("drums", start, sound[:count], gain, pan)
    score.events.append({"stem": "drums", "time": start, "duration": min(.08, chord["end"] - start),
                         "note": pitch, "velocity": max(1, min(127, round(gain * 110)))})
    if pitch == 36:
        score.kicks.append(start)


def arrange(score, style):
    fast = style == "drum-and-bass"
    kick = ins.tight_kick(fast)
    snare = ins.snare(fast)
    hat = ins.hat()
    for index, chord in enumerate(score.harmony):
        a, b, role = chord["start"], chord["end"], chord["role"]
        active = role in ("groove", "build", "drop")
        full = role == "drop"
        span = b - a
        # Quiet sustained chords contrast with the original continuous saw/pluck layers.
        for pitch in chord["voices"]:
            length = max(.01, span - .025)
            if fast:
                score.note("pad", a, length, pitch + 12, .065, sound=ins.pad_voice(pitch + 12, length), boundary=b)
            else:
                score.note("chords", a, length, pitch, .15, sound=ins.organ_voice(pitch, length), boundary=b)
        if fast:
            # Sparse sustained answers leave room for a bass-led groove.
            if index % 2 == 0 or not active:
                pitch = chord["voices"][2 if index % 4 == 0 else 1] + 12
                length = min(span * .8, score.beat * 2.6)
                score.note("lead", a + score.beat * .25, length, pitch, .20,
                           sound=ins.organ_voice(pitch, length), boundary=b)
        else:
            # Alternating two-bar tine phrases; articulation, rests and register differ from house.
            offsets, degrees = ([.25, 1.5, 2.75], [2, 1, 0]) if index % 2 == 0 else ([.75, 2.25], [0, 2])
            for offset, degree in zip(offsets, degrees):
                start, length = a + offset * score.beat, score.beat * .65
                pitch = chord["voices"][degree] + 12
                score.note("keys", start, length, pitch, .27 if full else .20,
                           sound=ins.tine_keys(pitch, length), boundary=b)
        if not active:
            continue
        kicks = ([0, 1.75, 2.5] if index % 2 == 0 else [0, .75, 2.5, 3.75]) if fast else ([0, 1.5, 2.75] if index % 2 == 0 else [0, 2, 3.5])
        for offset in kicks:
            _hit(score, chord, offset, kick, 36, .70 if full else .46)
        for offset in [1, 3]:
            _hit(score, chord, offset, snare, 38, .63 if full else .43)
        if fast and full:
            for offset in [.75, 2.75]:
                _hit(score, chord, offset, snare, 38, .11, -.12)
        for step in range(16 if fast and full else 8):
            offset = step * (.25 if fast and full else .5)
            if not fast and step % 2:
                offset += .08
            _hit(score, chord, offset, hat, 42, .16 if step % 2 else .27, .15 if step % 2 else -.15)
        # Long moving bass vs clipped, syncopated bass; neither repeats four house offbeats.
        bass_notes = ([(.25, .95, 0), (1.75, .35, 12), (2.25, 1.25, 0)] if fast else
                      [(.25, .42, 0), (1.75, .32, 0), (2.5, .48, 12), (3.5, .25, 0)])
        for offset, beats, octave in bass_notes:
            pitch, length = chord["root"] + octave, beats * score.beat
            sound = ins.reese_voice(pitch, length) if fast else ins.bass_note(pitch, length)
            score.note("bass", a + offset * score.beat, length, pitch, .42 if full else .30,
                       sound=sound, boundary=b)
    for section in score.cfg["sections"]:
        if section["role"] == "drop":
            score.add("effects", section["start"], ins.crash(), .16)
    score.instrument_source = "Original oscillator/noise synthesis: " + ("air pads, organ answers, moving reese bass, tight drums" if fast else "tine keys, organ chords, syncopated bass, short snare")
