"""Three original miniatures using the companion skill's existing audio engine."""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "engine"))
from compose_edm import Score
from finish_music import Master
import instruments as ins


WORKS = {
    "still-current": {"name": "Still Current", "style": "ambient", "key": "D major",
                      "duration": 32, "bpm": 60, "progression": ["I", "IV", "vi", "I"], "lufs": -20,
                      "sections": [(0, 8, "intro", "Surface"), (8, 16, "texture", "Confluence"),
                                   (16, 24, "evolution", "Open water"), (24, 32, "release", "Still")],
                      "last_onset": 24., "settle": 30.},
    "phase-index": {"name": "Phase Index", "style": "techno", "key": "D minor",
                    "duration": 30, "bpm": 128, "progression": ["i"], "lufs": -16,
                    "sections": [(0, 3.75, "intro", "Index"), (3.75, 11.25, "groove", "Lock"),
                                 (11.25, 22.5, "evolution", "Shift"), (22.5, 28.125, "groove", "Compress"),
                                 (28.125, 30, "outro", "Resolve")],
                    "last_onset": 28.125, "settle": 28.85},
    "amber-hours": {"name": "Amber Hours", "style": "downtempo", "key": "F major",
                    "duration": 32, "bpm": 90, "progression": ["I", "vi", "IV", "I"], "lufs": -18,
                    "sections": [(0, 16/3, "intro", "First light"), (16/3, 16, "groove", "Slow turn"),
                                 (16, 80/3, "evolution", "Warmth"), (80/3, 32, "outro", "Home")],
                    "last_onset": 88/3, "settle": 30.5},
}


def voice(note, gate, kind, colour=.4):
    release = {"cloud": 1.5, "felt": .45, "pulse": .09, "sub": .16}[kind]
    t = np.arange(round((gate + release) * ins.SR)) / ins.SR
    f = ins.hz(note)
    if kind == "cloud":
        sound = np.zeros((len(t), 2))
        for c in range(2):
            for h, strength in [(1,.64),(2,.15),(3,.045),(5,.009)]:
                # Continuous slow harmonic evolution, not a hidden beat.
                amp = .8 + .2 * np.sin(t * (.12+h*.013) + colour + c*.1)
                sound[:,c] += np.sin(2*np.pi*f*h*t+c*.08) * strength * amp
            sound[:,c] = ins.release_shape(sound[:,c], gate, min(2.,gate/3), release)
        return sound.astype(np.float32)
    sound = np.sin(2*np.pi*f*t)
    if kind == "felt":
        sound += .11*np.sin(4*np.pi*f*t)*np.exp(-t*4)
        sound += .025*np.sin(6*np.pi*f*t)*np.exp(-t*8)
        sound *= np.exp(-t*1.5)
    elif kind == "pulse":
        for h in range(2, min(40, int(17000/f))):
            sound += np.sin(2*np.pi*f*h*t+.12*h)/(h**1.1*(1+(h*f/(450+colour*3300))**4))
        sound = np.tanh(sound*.95)*np.exp(-t*9)*.65
    elif kind == "sub":
        sound += .10*np.sin(4*np.pi*f*t)
        sound *= np.exp(-t*2.5)*.7
    return ins.release_shape(sound, gate, .012 if kind != "pulse" else .004, release).astype(np.float32)


def note(score, stem, time, gate, pitch, gain, kind, boundary, pan=0., colour=.4):
    gate = min(gate, boundary-time)
    if gate >= .01:
        score.note(stem, time, gate, pitch, gain, pan=pan, sound=voice(pitch,gate,kind,colour), boundary=boundary)


def hit(score, time, sound, pitch, gain, pan=0.):
    if time >= score.duration: return
    score.add("drums", time, sound, gain, pan)
    score.events.append({"stem":"drums", "time":time, "duration":len(sound)/score.sr,
                         "note":pitch, "velocity":round(min(1,gain)*110)})
    if pitch == 36: score.kicks.append(time)


def compose_cloud(score):
    for index, chord in enumerate(score.harmony):
        a,b = chord["start"], chord["end"]
        for j,pitch in enumerate(chord["voices"]):
            note(score,"pad",a,b-a-.6,pitch+12,.16,"cloud",b,colour=index*.7+j)
        note(score,"bass",a,b-a-.6,chord["root"]+12,.10,"cloud",b)
        if index in (1,2):
            note(score,"lead",a+2.3,3.,chord["voices"][2]+24,.035,"cloud",b)
    t=np.arange(score.n)/score.sr
    noise=ins.RNG.standard_normal(score.n).astype(np.float32)
    texture=ins.filt(noise,[320,2100],"bandpass")
    texture*=((.6+.3*np.sin(t*.17+.5))*np.sin(np.pi*np.clip(t/32,0,1))**2*.035)
    score.add("effects",0,ins.soften(texture,2,3),pan=.15)
    score.instrument_source="Original additive cloud voices, slow harmonic amplitude modulation and filtered generated noise; no drums, samples or field recordings"


def compose_techno(score):
    kick,hat,openhat,clap=ins.tight_kick(),ins.hat(),ins.hat(True),ins.clap()
    for index,chord in enumerate(score.harmony):
        a,b=chord["start"],chord["end"]
        if index == 15:
            hit(score,a,kick,36,.67)
            note(score,"bass",a,.55,chord["root"],.42,"sub",b)
            for p in chord["voices"]: note(score,"chords",a,.65,p+12,.055,"cloud",b)
            continue
        colour=.16+.75*min(index/11,1)
        if index>=12: colour=.8-(index-12)*.13
        positions=[0,.75,1.5,2.75] if index%4<2 else [0,.75,1.75,2.5,3.5]
        if index == 0: positions=[0,1.5,2.75]
        for j,off in enumerate(positions):
            p=chord["root"]+12+(12 if j%3==2 else 0)
            note(score,"lead",a+off*score.beat,.17,p,.22+index*.004,"pulse",b,colour=colour)
        if index>=2:
            for beat in range(4):
                hit(score,a+beat*score.beat,kick,36,.70)
                note(score,"bass",a+(beat+.35)*score.beat,.22,chord["root"],.26,"sub",b)
                if index>=4:
                    hit(score,a+(beat+.5)*score.beat,openhat,46,.23 if index<12 else .17,.20)
            if index>=6:
                for off in (1,3):hit(score,a+off*score.beat,clap,39,.27)
            if 8<=index<14:
                for j in range(16):
                    if j%2:hit(score,a+j*.25*score.beat,hat,42,.10 if j%4==3 else .055,-.20)
            if index in (7,11):
                for j in range(3):hit(score,a+(3.5+j/6)*score.beat,hat,42,.10+j*.025)
        # A dry, quieter delay answers the motif; it never creates new harmony.
    source=score.stems["lead"]
    shift=round(score.beat*.75*score.sr)
    score.stems["effects"][shift:]+=source[:-shift,::-1]*.16
    score.instrument_source="Original filtered harmonic pulse sequence, monophonic sub and synthesized drum/noise voices; 16-bar bespoke pattern/brightness progression"


def compose_downtempo(score):
    kick,snare,hat=ins.tight_kick(),ins.snare(),ins.hat()
    for index,chord in enumerate(score.harmony):
        a,b=chord["start"],chord["end"]
        final=index==11
        for p in chord["voices"]:
            note(score,"chords",a,.95 if final else 2.1,p+12,.075,"cloud",b)
        # Two related, deliberately sparse motifs with different phrase answers.
        offsets=[(.16,2, .75),(1.65,1,.60),(3.1,0,.52)] if index%2==0 else [(.35,1,1.1),(2.65,2,.70)]
        if final: offsets=[(0,0,1.2)]
        for off,j,gate in offsets:
            note(score,"keys",a+off*score.beat,gate,chord["voices"][j]+12,.19,"felt",b,pan=-.12 if j%2 else .12)
        if final:
            hit(score,a,kick,36,.35)
            note(score,"bass",a,1.,chord["root"],.29,"sub",b)
        elif 2<=index<10:
            for off in (0,2.5) if index%2==0 else (0,1.75,2.75):hit(score,a+off*score.beat,kick,36,.46)
            for off in (1.055,3.055):hit(score,a+off*score.beat,snare,38,.30)
            for j in range(8):
                hit(score,a+(j*.5+(.075 if j%2 else 0))*score.beat,hat,42,.13 if j%2==0 else .065,.25)
            for off in (.1,2.65):note(score,"bass",a+off*score.beat,.76,chord["root"],.30,"sub",b)
    delay=round(score.beat*.75*score.sr)
    score.stems["effects"][delay:]+=score.stems["keys"][:-delay,::-1]*.11
    score.instrument_source="Original rounded additive keys, slow chord cushions, synthesized broken drums and sub; laid-back backbeats and alternating phrase answers; no vinyl or third-party samples"


def build(identifier,root):
    work=WORKS[identifier]
    root.mkdir(parents=True,exist_ok=True)
    (root/"work").mkdir(exist_ok=True);(root/"outputs").mkdir(exist_ok=True)
    cfg={"name":work["name"],"slug":identifier,"duration":work["duration"],
         "music":{"style":work["style"],"key":work["key"],"bpm":work["bpm"],
                  "progression":work["progression"],"pulse":"free" if identifier=="still-current" else "metric",
                  "harmony_seconds":8,"seed":24102026,"harmonic_profile":"consonant",
                  "lufs":work["lufs"],"true_peak":-2,"soundfont":None,"export_stems":False},
         "sections":[{"start":a,"end":b,"role":r,"label":l} for a,b,r,l in work["sections"]]}
    (root/"project.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
    score=Score(root,cfg)
    {"still-current":compose_cloud,"phase-index":compose_techno,"amber-hours":compose_downtempo}[identifier](score)
    score.audit()
    score.mix()
    score.write_midi(root/"outputs"/f"{identifier}-music.mid")
    metadata_path=root/"work/music-metadata.json"
    metadata=json.loads(metadata_path.read_text())
    metadata.update(sections=cfg["sections"],composition="Original commissioned showcase miniature",starter_timbres=None,
                    arrangement_source="compose.py; custom arrangement, not an unchanged style preset")
    metadata_path.write_text(json.dumps(metadata,indent=2),encoding="utf-8")
    cue={"work":identifier,"pulse":cfg["music"]["pulse"],"last_compositional_onset":work["last_onset"],
         "visual_settle":work["settle"],"sections":cfg["sections"],
         "kicks":score.kicks,"snares":[e["time"] for e in score.events if e["stem"]=="drums" and e["note"] in (38,39)],
         "tonal_onsets":sorted(set(round(e["time"],6) for e in score.events if e["stem"] in ("lead","keys")))}
    (root/"work/cues.json").write_text(json.dumps(cue,indent=2),encoding="utf-8")
    master=Master(root,cfg);master.render();master.verify()
    if cfg["music"]["pulse"]=="free":
        report=root/"outputs"/f"{identifier}-production.md"
        text=report.read_text(encoding="utf-8-sig").replace("32 秒，60.0 BPM，D major。", "32 秒，自由時間、無鼓；D major。60 BPM 僅為 MIDI 參考速度，不代表週期拍點。")
        report.write_text(text,encoding="utf-8-sig")
    for old,new in (("qc.json","audio-qc.json"),("production.md","audio-production.md")):
        shutil.copy2(root/"outputs"/f"{identifier}-{old}",root/"outputs"/f"{identifier}-{new}")
    # Retain the complete actual arrangement metadata alongside the smaller master provenance.
    print("MINIATURE_COMPLETE",identifier,flush=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("work",choices=WORKS);ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args();build(args.work,args.output.resolve())
