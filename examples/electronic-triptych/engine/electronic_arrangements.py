"""Six distinct synthesis studies extending the original three beat arrangements.

These small, reproducible sketches do not replace a DAW or a production library.
Uses existing instrument/envelope/filter helpers and NumPy/SciPy, not a new engine.
"""
from functools import lru_cache
import math

import numpy as np

import instruments as ins
from arrangements import _hit


@lru_cache(maxsize=128)
def bass_voice(note,gate,kind,rate=2.):
    t=np.arange(round((gate+.15)*ins.SR))/ins.SR
    f=ins.hz(note)
    if kind=='808':
        phase=2*math.pi*(f*t+f*.28*.026*(1-np.exp(-t/.026)))
        body=np.sin(phase)*np.exp(-t*1.45)
        body=np.tanh(body*1.35)*.58
    elif kind=='wobble':
        # Harmonic brightness follows an LFO while the sub remains stable.
        movement=(.5+.5*np.sin(2*math.pi*rate*t-.8))**1.5
        body=.48*np.sin(2*math.pi*f*t)
        for h in range(2,min(30,int(16000/f))):
            body+=.38/h**1.1*np.sin(2*math.pi*f*h*t)*np.exp(-h/(2+12*movement))
        body=np.tanh(body*2.1)*.45
    else:
        body=.7*np.sin(2*math.pi*f*t)+.15*np.sin(4*math.pi*f*t)
        body*=np.exp(-t*(7 if kind=='trance' else 3.2))*.65
    return ins.release_shape(body,gate,.008,.15).astype(np.float32)


@lru_cache(maxsize=128)
def pulse_voice(note,gate,phase=0.):
    t=np.arange(round((gate+.18)*ins.SR))/ins.SR
    f=ins.hz(note);body=np.zeros_like(t)
    cutoff=850+850*(.5+.5*math.sin(phase))
    for h in range(1,min(28,int(17000/f))):
        body+=np.sin(2*math.pi*f*h*t)/(h**1.2*(1+(h*f/cutoff)**3))
    body*=np.exp(-t*6)*.35
    return ins.release_shape(body,gate,.006,.18).astype(np.float32)


@lru_cache(maxsize=64)
def drone_voice(note,gate,phase=0.):
    t=np.arange(round((gate+.8)*ins.SR))/ins.SR
    f=ins.hz(note)
    stereo=[]
    for channel in range(2):
        body=np.zeros_like(t)
        for h,weight in [(1,.5),(2,.17),(3,.08),(5,.02)]:
            movement=.75+.25*np.sin(t*(.11+h*.017)+phase+channel*.2)
            body+=weight*movement*np.sin(2*math.pi*f*h*t+channel*.06)
        stereo.append(ins.release_shape(body,gate,min(1.5,gate/4),.8))
    return np.column_stack(stereo).astype(np.float32)


def ambient(score):
    for index,chord in enumerate(score.harmony):
        a,b=chord['start'],chord['end'];gate=b-a
        for j,pitch in enumerate(chord['voices']):
            score.note('pad',a,gate,pitch+12,.17,pan=0,
                       sound=drone_voice(pitch+12,gate,index*.7+j),boundary=b)
        pitch=chord['root']+12
        score.note('bass',a,gate,pitch,.12,sound=drone_voice(pitch,gate,index*.4),boundary=b)
    # Nonperiodic texture; no hits, kick sidechain, riser or compulsory drop.
    t=np.arange(score.n)/score.sr
    noise=ins.filt(ins.RNG.standard_normal(score.n).astype(np.float32),[260,2800],'bandpass')
    envelope=(.55+.25*np.sin(t*.21)+.15*np.sin(t*.083+.7))
    score.add('effects',0,ins.soften(noise*envelope*.035,1.,1.))
    score.instrument_source='Original slow additive drones and filtered generated noise; no drums or sampled recordings'


def arrange(score,style):
    if style=='ambient':
        ambient(score);return
    if style not in ('techno','trance','dubstep','trap','downtempo'):
        raise ValueError('No arrangement for '+style)
    kick=ins.tight_kick(style in ('trance','trap'))
    snare=ins.snare(style=='trap');hat=ins.hat();opened=ins.hat(True)
    for index,chord in enumerate(score.harmony):
        a,b,role=chord['start'],chord['end'],chord['role'];span=b-a
        active=role in ('groove','build','drop','evolution')
        full=role in ('drop','evolution')
        def note(stem,off,beats,pitch,gain,sound):
            start=a+off*score.beat
            if start>=b or start<0:return
            gate=min(beats*score.beat,b-start)
            if gate>.009:score.note(stem,start,gate,pitch,gain,sound=sound(pitch,gate),boundary=b)
        if style=='techno':
            # One harmonic centre, dry repetitive motif, eight-bar brightness cycle.
            for j in range(8 if active else 2):
                off=j*.5 if active else j*2
                pitch=chord['root']+12+(12 if j%4==3 else 0)
                note('lead',off,.22,pitch,.33 if active else .12,
                     lambda n,g: pulse_voice(n,g,index*.55+j*.13))
            if active:
                for off in (0,1,2,3):
                    _hit(score,chord,off,kick,36,.68)
                    note('bass',off+.25,.57,chord['root'],.24,lambda n,g:bass_voice(n,g,'techno'))
                for off in (.5,1.5,2.5,3.5):_hit(score,chord,off,opened,46,.30)
                for off in (1.75,2.75,3.25):_hit(score,chord,off,snare,38,.13 if index%2 else .20)
        elif style=='trance':
            for pitch in chord['voices']:
                note('pad',0,span/score.beat,pitch+12,.07,ins.pad_voice)
            # Sustained poly-saw answers and short sixteenth-note arpeggios.
            if active:
                for j in range(16):
                    pitch=chord['voices'][[0,1,2,1,0,2,1,2][j%8]]+24
                    note('arp',j*.25,.19,pitch,.14 if full else .075,
                         lambda n,g:ins.chord_voice(n,g,True))
                for j in range(4):
                    _hit(score,chord,j,kick,36,.65)
                    _hit(score,chord,j+.5,opened,46,.35)
                    note('bass',j+.5,.35,chord['root'],.42,lambda n,g:bass_voice(n,g,'trance'))
                for off in (1,3):_hit(score,chord,off,ins.clap(),39,.43)
                if full:
                    for off,degree in [(0,2),(1.5,1),(2.5,0)]:
                        note('lead',off,.85,chord['voices'][degree]+24,.20,lambda n,g:ins.chord_voice(n,g,True))
        elif style in ('dubstep','trap'):
            # 140-ish double-time grid: principal snare on beat three (offset 2).
            if not active:
                for pitch in chord['voices']:
                    note('pad',0,span/score.beat,pitch+12,.07,ins.pad_voice)
            if active:
                for off in ([0,1.5,3.25] if style=='dubstep' else [0,.75,2.75,3.5]):
                    _hit(score,chord,off,kick,36,.64)
                _hit(score,chord,2,snare,38,.72)
                for j in range(8):_hit(score,chord,j*.5,hat,42,.20 if j%2 else .30)
                if style=='trap':
                    for j in range(6):_hit(score,chord,3+j/6,hat,42,.11+.025*j)
                    for off,beats in [(0,1.3),(1.5,.35),(2.75,.5),(3.5,.38)]:
                        note('bass',off,beats,chord['root'],.64,lambda n,g:bass_voice(n,g,'808'))
                    note('lead',.25,.6,chord['voices'][2]+12,.13,ins.organ_voice)
                else:
                    for j,(off,beats) in enumerate([(0,.8),(1,.5),(2.75,.7)]):
                        note('bass',off,beats,chord['root']+(12 if j==1 else 0),.65,
                             lambda n,g,j=j:bass_voice(n,g,'wobble',rate=(2 if j%2 else 4)/score.beat))
        elif style=='downtempo':
            for pitch in chord['voices']:note('chords',0,span/score.beat,pitch,.10,ins.organ_voice)
            for off,degree in ([(.35,2),(2.7,0)] if index%2==0 else [(1.4,1)]):
                note('keys',off,.9,chord['voices'][degree]+12,.17,ins.tine_keys)
            if active:
                for off in (0,2.5):_hit(score,chord,off,kick,36,.42)
                for off in (1.06,3.06):_hit(score,chord,off,snare,38,.38)
                for j in range(8):_hit(score,chord,j*.5+( .09 if j%2 else 0),hat,42,.15)
                for off,beats in [(.15,1.4),(2.6,1.05)]:note('bass',off,beats,chord['root'],.32,ins.bass_note)
    score.instrument_source='Original oscillator/noise synthesis; distinct '+style+' rhythm, voicing, articulation and modulation study'
