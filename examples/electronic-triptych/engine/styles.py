"""Distinct starter directions; these are example choices, not genre definitions."""
PRESETS = {
    "melodic-house": {"bpm": 120, "key": "G major", "progression": ["I", "V", "vi", "IV"],
                      "name": "原創 Melodic House", "timbres": ["soft keys", "saw pluck", "offbeat sub bass", "clap"]},
    "breakbeat": {"bpm": 132, "key": "D minor", "progression": ["i", "iv", "VI", "VII"],
                  "name": "原創 Breakbeat", "timbres": ["tine keys", "rounded organ", "syncopated bass", "short snare"]},
    "drum-and-bass": {"bpm": 172, "key": "F minor", "progression": ["i", "III", "VI", "iv"],
                      "name": "原創 Drum and Bass", "timbres": ["air pad", "long organ answer", "moving reese bass", "tight snare / ghost notes"]},
}

# These are executable studies, not a closed taxonomy of electronic music.
PRESETS.update({
    'techno': {'bpm':132, 'key':'D minor', 'progression':['i'], 'name':'原創 Techno',
               'timbres':['filtered pulse sequence','dry percussion','saturated sub','slow timbral evolution']},
    'trance': {'bpm':138, 'key':'A minor', 'progression':['i','VI','III','VII'], 'name':'原創 Trance',
               'timbres':['layered saw riff','offbeat bass','sixteenth-note arp','four-on-the-floor drums']},
    'dubstep': {'bpm':140, 'key':'F minor', 'progression':['i','VI'], 'name':'原創 Dubstep',
                'timbres':['half-time snare','modulated harmonic bass','sub','bass call and response']},
    'trap': {'bpm':148, 'key':'D minor', 'progression':['i','VI','iv','i'], 'name':'原創 Electronic Trap',
             'timbres':['pitched 808-style bass','hat triplet rolls','half-time snare','sparse organ motif']},
    'ambient': {'bpm':60, 'key':'C major', 'progression':['I','IV','vi','I'], 'name':'原創 Ambient',
                'timbres':['slow evolving drone','sustained pad','filtered noise bed','no drums']},
    'downtempo': {'bpm':84, 'key':'D minor', 'progression':['i','iv','VI','VII'], 'name':'原創 Downtempo',
                  'timbres':['laid-back broken beat','soft organ','long bass','sparse tine replies']},
})

# Per-style mix choices keep bass-led sketches from sharing one house filter.
MIX = {
    'melodic-house':(230,.63), 'breakbeat':(480,.38), 'drum-and-bass':(1200,.30),
    'techno':(950,.48), 'trance':(650,.55), 'dubstep':(3600,.23),
    'trap':(1600,.25), 'ambient':(1200,0.), 'downtempo':(480,.18),
}


def apply_preset(cfg, style):
    preset = PRESETS[style]
    cfg["name"], cfg["slug"] = preset["name"], style
    cfg["music"].update(style=style, bpm=preset["bpm"], key=preset["key"], progression=list(preset["progression"]))
    cfg['music']['pulse'] = 'free' if style == 'ambient' else 'metric'
    if style == 'ambient':
        cfg['music']['harmony_seconds'] = 12.
        sections=[(0,.15,'intro'),(.15,.5,'texture'),(.5,.85,'evolution'),(.85,1,'release')]
        cfg['sections']=[{'start':a*cfg['duration'],'end':b*cfg['duration'],'role':r,'label':r} for a,b,r in sections]
        return
    if style == 'techno':
        sections=[(0,.1,'intro'),(.1,.4,'groove'),(.4,.65,'evolution'),(.65,.9,'groove'),(.9,1,'outro')]
        cfg['sections']=[{'start':a*cfg['duration'],'end':b*cfg['duration'],'role':r,'label':r} for a,b,r in sections]
        return
    if style == "melodic-house":
        return
    sections = ([(0, .12, "intro"), (.12, .4, "groove"), (.4, .5, "break"), (.5, .9, "drop"), (.9, 1, "outro")]
                if style == "breakbeat" else
                [(0, .1, "intro"), (.1, .2, "build"), (.2, .58, "drop"), (.58, .68, "break"), (.68, .9, "drop"), (.9, 1, "outro")])
    cfg["sections"] = [{"start": a * cfg["duration"], "end": b * cfg["duration"], "role": role, "label": role}
                       for a, b, role in sections]
