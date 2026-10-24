"""Five bespoke context scores; sampled instruments plus the electronic skill engine."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import mido
import numpy as np
from scipy.io import wavfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'engine'))
import instruments as ins
from compose_edm import Score
from finish_music import Master

WORKS={
 'victory-circuit':dict(title='決勝脈衝',name='Victory Circuit',context='電競賽事',bpm=174,meter=4,key='D minor',style='drum-and-bass',
   family='CINEMATIC D&B',lufs=-15,final_bar=42,progression=['i','VI','III','VII'],
   cuts=[(0,'intro','就位'),(4,'build','集結'),(12,'groove','交鋒'),(20,'break','屏息'),(22,'drop','決勝'),(34,'drop','全力推進'),(42,'outro','落定')],
   summary='為賽前開場與賽事精華製作，快速破拍、低音問答與主題回歸。',
   description='174 BPM 電競賽事配樂。緊湊 kick/snare、ghost notes、Reese 中頻低音與獨立 sub 構成動能；圓潤合成器短句在兩小節動機上變奏，中段實際撤鼓後回歸，末段以主和弦和最後一擊結束。'),
 'daybreak-proposal':dict(title='向光提案',name='Daybreak Proposal',context='商業簡報',bpm=112,meter=4,key='D major',style='melodic-house',
   family='CLEAN ELECTRONIC POP',lufs=-18,final_bar=27,progression=['I','V','vi','IV'],
   cuts=[(0,'intro','開題'),(4,'groove','展開'),(12,'break','留白'),(16,'groove','前進'),(24,'build','結語'),(27,'outro','定案')],
   summary='乾淨明亮的簡報襯樂，鋼琴與悶音吉他接力，為口白留出空間。',
   description='112 BPM 商業簡報 BGM。取樣鋼琴的簡短主題、悶音吉他的切分和弦、指彈貝斯與輕量電子鼓分工；中段移除 kick 與前景旋律，保留和聲呼吸，重返段落後變化旋律句尾。'),
 'cloudside-cafe':dict(title='雲朵補給站',name='Cloudside Cafe',context='休閒遊戲',bpm=104,meter=4,key='C major',style='breakbeat',
   family='PLAYFUL GAME ELECTRONICA',lufs=-17,final_bar=25,progression=['I','IV','vi','V'],
   cuts=[(0,'intro','登入雲端'),(4,'groove','採集時光'),(12,'break','小小發現'),(16,'groove','快樂補給'),(24,'outro','存檔')],
   summary='像經營一座雲端小店，俏皮電子短句與撥弦弦樂輪流打招呼。',
   description='104 BPM 休閒遊戲 BGM。撥奏弦樂、尼龍吉他、短小電子旋律與鬆散切分鼓形成輕巧律動；兩個主題交替問答，中段減少鼓與低音，最後以 C 大調短句收束。這版為有結尾的試聽曲，未標示無縫循環。'),
 'jade-wind-ascent':dict(title='御風入雲',name='Jade Wind Ascent',context='仙俠',bpm=80,meter=4,key='D major',style='ambient',
   family='PENTATONIC FANTASY HYBRID',lufs=-19,final_bar=19,progression=['I','vi','V','I'],
   cuts=[(0,'intro','山門'),(4,'texture','雲行'),(8,'evolution','御風'),(12,'evolution','遠峰'),(16,'release','歸雲'),(19,'outro','餘韻')],
   summary='五聲旋律越過雲海，長笛、箏式撥弦質地與稀疏低鼓構成仙俠景色。',
   description='80 BPM 仙俠幻想混合配樂。主旋律限制於 D 大調五聲音階，以長笛取樣長句及 General MIDI Koto 撥弦交替，低量弦樂、原創風感噪聲與稀疏合成低鼓支撐空間。Koto 是箏式質地的近似選擇，非古箏或洞簫實錄。'),
 'almost-yours':dict(title='靠近的那一秒',name='Almost Yours',context='戀愛時刻',bpm=72,meter=3,key='F major',style='downtempo',
   family='ROMANTIC ELECTROACOUSTIC',lufs=-20,final_bar=23,progression=['I','vi','IV','V'],
   cuts=[(0,'intro','初見'),(4,'texture','並肩'),(8,'groove','心動'),(14,'break','欲言又止'),(16,'evolution','靠近'),(22,'outro','那一秒')],
   summary='六八拍的柔和搖曳，取樣鋼琴、尼龍吉他與慢弦樂寫下靠近的片刻。',
   description='以 72 quarter-note BPM 記拍的 6/8 戀愛配樂。柔和取樣鋼琴用長短句呼應，尼龍吉他以八分音符輕搖、慢弦樂漸入；沒有 kick、snare 或 hi-hat。中段讓旋律停下，再以新的回應與 F 大調終止收尾。')
}

def dump(path,value): path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

class ContextScore(Score):
 def __init__(self,root,cfg,work,sf,fluid):
    super().__init__(root,cfg)
    self.w,self.sf_file,self.fluid=work,sf,fluid
    self.sampled={};self.channels={};self.programs={};self.harmony=[]
    # Harmonic changes every two bars; final tonic is a composed event.
    for i in range(0,work['final_bar'],2):
      degree=work['progression'][(i//2)%len(work['progression'])]
      voices,bass,hook=self.harmony_data[degree]
      a=self.at(i);b=self.at(min(i+2,work['final_bar']))
      self.harmony.append(dict(start=a,end=b,voices=[p+self.shift for p in voices],root=bass+self.shift,
        pcs={(p+self.shift)%12 for p in voices},name=degree,role='custom'))
    voices,bass,hook=self.harmony_data['i' if work['key'].endswith('minor') else 'I']
    self.final=self.at(work['final_bar'])
    self.harmony.append(dict(start=self.final,end=60,voices=[p+self.shift for p in voices],root=bass+self.shift,
      pcs={(p+self.shift)%12 for p in voices},name='tonic',role='outro'))
    self.cfg['music']['soundfont']=None

 def chord(self,t): return next(c for c in self.harmony if c['start']<=t<c['end'])
 def at(self,bar,off=0): return round((bar*self.w['meter']+off)*self.beat,9)
 def tone(self,stem,t,gate,pitch,gain,voice='organ',pan=0):
    if t>=60 or gate<=.01:return
    c=self.chord(t)
    gate=min(gate, c['end']-t-.035 if t<self.final else 59.65-t)
    if gate<.01:return
    factory={'organ':ins.organ_voice,'sub':ins.bass_note,'reese':ins.reese_voice,'pad':ins.pad_voice}
    self.note(stem,t,gate,pitch,gain,pan=pan,sound=factory[voice](pitch,gate),velocity=round(min(.9,gain*2)*110),boundary=60)
    self.events[-1].update(source='original synthesis',gain=gain)
 def sampled_note(self,stem,program,t,gate,pitch,vel=68,pan=0):
    if t>=60:return
    c=self.chord(t);gate=min(gate,max(.015,c['end']-t-.20) if t<self.final else 59.40-t)
    if gate<.012:return
    if stem not in self.sampled:
      self.sampled[stem]=[];self.channels[stem]=len(self.sampled)-1;self.programs[stem]=program
    ev=dict(stem=stem,time=t,duration=gate,note=pitch,velocity=vel,pan=pan,
            source='GeneralUser GS 2.0.3',program_zero_based=program)
    self.sampled[stem].append(ev);self.events.append(ev.copy())
 def drum(self,t,sound,pitch,gain,pan=0):
    self.add('drums',t,sound,gain,pan)
    self.events.append(dict(stem='drums',time=t,duration=len(sound)/self.sr,note=pitch,velocity=round(gain*110),source='original noise/oscillator synthesis'))
    if pitch==36:self.kicks.append(t)
 def render_sample(self,stem):
    path=self.root/'work'/f'{stem}.mid'
    self.midi(path,only=stem)
    dest=self.root/'work'/f'{stem}-raw.wav'
    p=subprocess.run([str(self.fluid),'-ni','-q','-r','48000','-g','.65','-R','0','-C','0',
      '-o','synth.cpu-cores=1','-F',str(dest),'-T','wav','-O','float',str(self.sf_file),str(path)],capture_output=True)
    (self.root/'work'/f'{stem}-render.log').write_bytes(p.stdout+b'\n'+p.stderr)
    if p.returncode:raise RuntimeError('FluidSynth rendering failed: '+stem)
    sr,x=wavfile.read(dest);assert sr==self.sr
    if x.ndim==1:x=np.column_stack([x,x])
    x=np.pad(x[:self.n],((0,max(0,self.n-len(x))),(0,0))).astype(np.float32)
    return stem,x
 def midi(self,path,only=None):
    m=mido.MidiFile(type=1,ticks_per_beat=960)
    meta=mido.MidiTrack();m.tracks.append(meta)
    meta.append(mido.MetaMessage('track_name',name=self.w['name']))
    meta.append(mido.MetaMessage('set_tempo',tempo=mido.bpm2tempo(self.bpm)))
    meta.append(mido.MetaMessage('time_signature',numerator=6 if self.w['meter']==3 else 4,denominator=8 if self.w['meter']==3 else 4))
    programs={**self.programs,'lead':16,'bass':38,'arp':38,'pad':89,'chords':89,'drums':0}
    names=[only] if only else list(dict.fromkeys(e['stem'] for e in self.events))
    channels={n:i for i,n in enumerate(n for n in names if n!='drums')}
    for name in names:
      if name=='effects':continue
      ch=9 if name=='drums' else channels[name]
      tr=mido.MidiTrack();m.tracks.append(tr)
      tr.append(mido.MetaMessage('track_name',name=name))
      tr.append(mido.Message('program_change',channel=ch,program=programs[name]))
      pan=next((e.get('pan',0) for e in self.events if e['stem']==name),0)
      for cc,v in [(7,100),(10,round(64+pan*50)),(91,0),(93,0)]:tr.append(mido.Message('control_change',channel=ch,control=cc,value=v))
      queue=[]
      for e in self.events:
        if e['stem']!=name:continue
        for t,on in ((e['time'],True),(min(60,e['time']+e['duration']),False)):
          queue.append((round(t/self.beat*960),1 if on else 0,mido.Message('note_on' if on else 'note_off',
             channel=ch,note=e['note'],velocity=e['velocity'] if on else 0)))
      prior=0
      for tick,order,msg in sorted(queue,key=lambda e:(e[0],e[1])):tr.append(msg.copy(time=tick-prior));prior=tick
      tr.append(mido.MetaMessage('end_of_track',time=max(0,round(60/self.beat*960)-prior)))
    m.save(path)

def bed(s,gain=.045):
 # Tied common tones use the companion skill's existing voice and tail handling.
 live={};phrases=[]
 for c in s.harmony[:-1]:
    for p in list(live):
      if p not in c['voices']:phrases.append(live.pop(p))
    for p in c['voices']:
      if p in live:live[p][1]=c['end']
      else:live[p]=[c['start'],c['end'],p]
 phrases+=list(live.values())
 for a,b,p in phrases:s.note('pad',a,max(.02,b-a-.16),p,gain,sound=ins.pad_voice(p,max(.02,b-a-.16)),boundary=60)

def esport(s):
 bed(s,.042)
 k,sn,h=ins.tight_kick(True),ins.snare(True),ins.hat()
 cells=[[(0,.70,0),(1.25,.45,2),(2.5,.65,1),(3.5,.3,0)],
        [(.25,.65,0),(1.75,.35,1),(2.5,.6,2),(3.5,.3,1)]]
 for bar in range(s.w['final_bar']):
    if 20<=bar<22:continue
    c=s.chord(s.at(bar));full=bar>=22
    if bar>=4:
      for off in ([0,1.75,2.5] if bar%2==0 else [0,.75,2.5,3.75]):s.drum(s.at(bar,off),k,36,.76 if full else .55)
      for off in (1,3):s.drum(s.at(bar,off),sn,38,.62 if full else .43)
      for j in range(16 if full else 8):s.drum(s.at(bar,j*(.25 if full else .5)),h,42,.24 if j%2==0 else .12,.15*(-1 if j%2 else 1))
      if full and bar%2:
        for off in (.75,2.75):s.drum(s.at(bar,off),sn,38,.11)
      for off,length,octave in [(0,1.15,0),(1.75,.4,12),(2.5,.95,0)]:
        s.tone('bass',s.at(bar,off),length*s.beat,c['root']-12,.43,'sub')
        s.tone('arp',s.at(bar,off),length*s.beat,c['root']+octave,.32 if full else .20,'reese')
    # A quiet opening motif expands into the full call/response after the break.
    if bar%2==0 or full:
      for off,length,index in cells[bar%2]:
        pitch=c['voices'][index]+(12 if bar>=34 and index==2 else 0)
        s.tone('lead',s.at(bar,off),length*s.beat,pitch,.23 if full else .16,'organ',.1*(-1 if index%2 else 1))
 for at in (s.at(4),s.at(22),s.at(34)):
    s.add('effects',at-min(.8,at),ins.swell(min(.8,at)),.5)
 s.drum(s.final,k,36,.86)

def business(s):
 bed(s,.035)
 k,sn,h=ins.tight_kick(),ins.clap(),ins.hat()
 for bar in range(s.w['final_bar']):
    c=s.chord(s.at(bar));quiet=12<=bar<16
    # Distinct four-bar piano sentence; alternate bars leave foreground space.
    phrase=[(0,1.2,0),(1.5,.55,2),(3,.65,1)] if bar%4 in (0,2) else [(.5,1.15,1),(2.75,.7,0)]
    if not quiet and (bar<4 or bar%2==0 or bar>=24):
      for off,length,index in phrase:s.sampled_note('piano',0,s.at(bar,off),length*s.beat,c['voices'][index]+12,60 if bar<16 else 65,-.08)
    for off in (.5,2.,3.5):
      if quiet and off!=2:continue
      for p in c['voices']:s.sampled_note('guitar',28,s.at(bar,off),.35*s.beat,p,43,.20)
    if bar>=4 and not quiet:
      for off in (0,1,2,3):s.drum(s.at(bar,off),k,36,.36)
      for off in (1,3):s.drum(s.at(bar,off),sn,39,.23)
      for j in range(8):s.drum(s.at(bar,j*.5+.025*(j%2)),h,42,.13 if j%2==0 else .07,.15)
      for off,length in ((0,1.2),(2.5,.9)):s.sampled_note('finger-bass',33,s.at(bar,off),length*s.beat,c['root']-12,62)

def casual(s):
 k,sn,h=ins.tight_kick(),ins.snare(),ins.hat()
 for bar in range(s.w['final_bar']):
    c=s.chord(s.at(bar));bridge=12<=bar<16
    for off,index in ((0,0),(1.5,2),(2.5,1)) if bar%2==0 else ((.5,1),(2,0),(3.25,2)):
      s.sampled_note('pizzicato',45,s.at(bar,off),.40*s.beat,c['voices'][index]+12,66 if not bridge else 50,-.10)
    for p in c['voices']:s.sampled_note('nylon-guitar',24,s.at(bar,.07),1.8*s.beat,p,45,.22)
    if bar%4 in (1,3):
      for off,index,length in ((.25,2,.45),(1.25,1,.5),(2.5,0,.7)):
        s.tone('lead',s.at(bar,off),length*s.beat,c['voices'][index]+12,.16,'organ',-.12)
    if bar>=4 and not bridge:
      for off in ([0,2.5] if bar%2==0 else [0,1.75,2.75]):s.drum(s.at(bar,off),k,36,.40)
      for off in (1.04,3.04):s.drum(s.at(bar,off),sn,38,.25)
      for j in range(8):s.drum(s.at(bar,j*.5+(.07 if j%2 else 0)),h,42,.14 if j%2==0 else .08,.20)
      for off,length in ((.1,.9),(2.35,.95)):s.tone('bass',s.at(bar,off),length*s.beat,c['root']-12,.31,'sub')

def xianxia(s):
 pent={2,4,6,9,11}
 # Flute-led four-bar phrases use only the D-major pentatonic set; Koto
 # provides a plucked texture and is honestly credited, not called a guzheng.
 for bar in range(s.w['final_bar']):
    c=s.chord(s.at(bar))
    allowed=[p+12 for p in c['voices'] if p%12 in pent]
    if bar%4 in (0,1,3):
      offsets=[(.25,1.5,0),(2.25,1.1,-1)] if bar%4!=3 else [(.5,2.5,0)]
      for off,length,index in offsets:
        s.sampled_note('flute',73,s.at(bar,off),length*s.beat,allowed[index],67 if bar<8 else 73,-.06)
    if bar%4!=1:
      for off,index in ((0,0),(.55,1),(1.35,2),(3,1)):
        p=allowed[index%len(allowed)]-12
        s.sampled_note('koto',107,s.at(bar,off),.70*s.beat,p,64 if bar<12 else 57,.23)
    if bar>=4:
      for p in c['voices']:s.sampled_note('strings',48,s.at(bar),3.6*s.beat,p,39,-.1)
    if 8<=bar<16 and bar%2==0:s.drum(s.at(bar),ins.filt(ins.tight_kick(),450,'lowpass'),41,.33)
 n=s.n;t=np.arange(n)/s.sr
 air=ins.filt(ins.RNG.standard_normal((n,2)).astype(np.float32),[260,1500],'bandpass')
 env=(.008+.004*np.sin(t*.31)) * np.minimum(t/1.5,1)*np.clip((58.8-t)/1.8,0,1)
 s.add('effects',0,air*env[:,None])
 # Verify the intended pentatonic restriction in the actual melodic note list.
 assert all(e['note']%12 in pent for e in s.events if e['stem'] in ('flute','koto'))

def romance(s):
 for bar in range(s.w['final_bar']):
    c=s.chord(s.at(bar));quiet=14<=bar<16
    # Six eighths per bar, not six quarter notes. Last two bars form a cadence.
    pattern=[0,2,1,2,1,2] if bar%2==0 else [0,1,2,1,2,1]
    if bar>=4:
      for j,index in enumerate(pattern):
        s.sampled_note('nylon-guitar',24,s.at(bar,j*.5),.70*s.beat,c['voices'][index],43 if j%3 else 50,.2)
    if not quiet:
      phrase=[(.05,1.1,2),(1.5,.95,1)] if bar%2==0 else [(.4,1.8,0)]
      for off,length,index in phrase:
        s.sampled_note('piano',0,s.at(bar,off),length*s.beat,c['voices'][index]+12,52 if bar<8 else 61,-.13)
    # A low piano root supplies foundation without kick or synth pumping.
    s.sampled_note('piano',0,s.at(bar,.03),2.45*s.beat,c['root'],43,-.13)
    if bar>=8:
      for p in c['voices']:s.sampled_note('slow-strings',49,s.at(bar),2.75*s.beat,p,37 if bar<16 else 44,.05)
 assert not any(e['stem']=='drums' for e in s.events)

def cadence(s,identifier):
 c=s.harmony[-1];span=60-s.final
 if identifier=='victory-circuit':
    s.tone('bass',s.final,span*.60,c['root']-12,.45,'sub')
    for p in c['voices']:s.tone('chords',s.final,span*.66,p,.09,'pad')
    s.tone('lead',s.final,span*.55,c['voices'][0],.24,'organ')
 elif identifier in ('daybreak-proposal','almost-yours'):
    for p in c['voices']:s.sampled_note('piano',0,s.final,span*.64,p+12,60 if identifier=='daybreak-proposal' else 54,-.1)
    s.sampled_note('piano',0,s.final,span*.66,c['root'],53,-.1)
 elif identifier=='cloudside-cafe':
    for p in c['voices']:s.sampled_note('pizzicato',45,s.final,.75,p+12,58,-.1)
    for p in c['voices']:s.sampled_note('nylon-guitar',24,s.final,1.15,p,52,.2)
    s.tone('bass',s.final,.8,c['root']-12,.30,'sub')
 elif identifier=='jade-wind-ascent':
    s.sampled_note('flute',73,s.final,span*.60,c['voices'][0]+12,62,-.06)
    for p in c['voices']:s.sampled_note('koto',107,s.final,.65,p,52,.23)
    for p in c['voices']:s.sampled_note('strings',48,s.final,span*.52,p,38,-.1)

def build(identifier,root,sf,fluid):
 w=WORKS[identifier];root.mkdir(parents=True,exist_ok=True)
 for folder in ('work','outputs'):(root/folder).mkdir(exist_ok=True)
 bar=60/w['bpm']*w['meter'];cuts=w['cuts']
 sections=[dict(start=a*bar,end=cuts[i+1][0]*bar if i+1<len(cuts) else 60,role=r,label=l) for i,(a,r,l) in enumerate(cuts)]
 cfg=dict(name=w['title'],slug=identifier,duration=60,sections=sections,
   music=dict(style=w['style'],key=w['key'],bpm=w['bpm'],progression=w['progression'],seed=24102026+list(WORKS).index(identifier),
     pulse='metric',harmonic_profile='consonant',lufs=w['lufs'],true_peak=-2,soundfont=None,export_stems=False))
 dump(root/'project.json',cfg)
 s=ContextScore(root,cfg,w,sf,fluid)
 {'victory-circuit':esport,'daybreak-proposal':business,'cloudside-cafe':casual,'jade-wind-ascent':xianxia,'almost-yours':romance}[identifier](s)
 cadence(s,identifier)
 # Validate actual note-on harmony membership, including sampled tracks.
 conflicts=[e for e in s.events if e['stem']!='drums' and e['note']%12 not in s.chord(e['time'])['pcs']]
 if conflicts:raise ValueError('Unexpected note-on/chord conflict: '+str(conflicts[0]))
 s.midi(root/'outputs'/f'{identifier}-music.mid')
 dump(root/'work/note-events.json',s.events)
 sf_targets={'piano':(-23.5 if identifier=='daybreak-proposal' else -24.5,95,6500),
  'guitar':(-30,180,6000),'finger-bass':(-27,35,1800),'pizzicato':(-23.5,190,6400),
  'nylon-guitar':(-29 if identifier=='almost-yours' else -28,130,6200),
  'flute':(-24,260,5400),'koto':(-27,160,6500),'strings':(-32,180,4400),'slow-strings':(-32,180,4000)}
 if s.sampled:
    with ThreadPoolExecutor(max_workers=2) as pool:
      for name,x in pool.map(s.render_sample,s.sampled):
        db,lo,hi=sf_targets[name];x=ins.filt(ins.filt(x,lo,'highpass'),hi,'lowpass')
        rms=np.sqrt(np.mean(x.reshape(600,4800,2)**2,axis=(1,2)));active=rms[rms>max(float(rms.max())*.15,1e-8)]
        assert len(active),'Silent sampled instrument '+name
        x*=10**(db/20)/max(float(np.sqrt(np.mean(active**2))),1e-8)
        s.stems[name]=x
 for name,lo,hi in [('lead',190,3200),('pad',180,2800),('chords',180,2800),('arp',145,2300),('bass',27,120)]:
    s.stems[name]=ins.filt(ins.filt(s.stems[name],lo,'highpass'),hi,'lowpass')
 if s.kicks:
    duck=np.ones(s.n,np.float32)
    depth=.36 if identifier=='victory-circuit' else .13
    for t in s.kicks:
      at=round(t*s.sr);n=min(round(.14*s.sr),s.n-at)
      env=1-depth*np.exp(-np.arange(n)/s.sr/.042);env[:96]=np.linspace(1,env[96],96)
      duck[at:at+n]=np.minimum(duck[at:at+n],env)
    s.stems['bass']*=duck[:,None]
    if 'finger-bass' in s.stems:s.stems['finger-bass']*=duck[:,None]
 # Filtered early reflections are sparse; no whole-mix repeated gating.
 for name in ('piano','flute','koto','lead','nylon-guitar'):
    if name not in s.stems:continue
    for delay,wet in ((.037,.09),(.071,.06),(.123,.035)):
      n=round(delay*s.sr);s.stems['effects'][n:]+=ins.filt(s.stems[name][:-n],2600,'lowpass')[:,::-1]*wet
 t=np.arange(s.n)/s.sr
 env=np.minimum(t/.035,1)*np.cos(np.clip((t-59.40)/.55,0,1)*np.pi/2)**2
 mix=ins.filt(sum(s.stems.values()),25,'highpass')*env[:,None]
 mix*=min(1,.82/max(float(np.abs(mix).max()),1e-8))
 wavfile.write(root/'work/score-mix.wav',s.sr,mix.astype(np.float32))
 metadata=dict(duration_seconds=60,original_composition=True,composition=f'Original bespoke score: {w["name"]}',
  style=w['family'],pulse='metric',bpm=w['bpm'],key=w['key'],meter='6/8' if w['meter']==3 else '4/4',
  tempo_note='Quarter-note BPM; six eighth notes per bar' if w['meter']==3 else 'Quarter-note BPM',
  instrument_source=('Original oscillator/noise synthesis'+('; GeneralUser GS 2.0.3 sampled instruments rendered by FluidSynth 2.6.1' if s.sampled else ' only')),
  sampled_programs_zero_based=s.programs,soundfont_source='https://github.com/mrbumpy409/GeneralUser-GS' if s.sampled else None,
  soundfont_sha256=hashlib.sha256(sf.read_bytes()).hexdigest() if s.sampled else None,
  soundfont_license_file='GeneralUser-GS-LICENSE.txt' if s.sampled else None,
  sections=sections,note_events=len(s.events),unexpected_chord_conflicts=0,
  harmonic_check_scope='Actual note-on/chord membership; sampled release and reflections are not fully represented by MIDI gates',
  last_effective_onset=max(e['time'] for e in s.events),musical_final_onset=s.final,
  engine_files_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (HERE/'engine').glob('*.py')},
  arrangement_source='compose.py; five separate original arrangements, not relabeled presets',
  limits='Objective QC does not certify musical style, taste or subjective listening quality.')
 dump(root/'work/music-metadata.json',metadata)
 master=Master(root,cfg);master.render();master.verify()
 provenance=root/'outputs'/f'{identifier}-provenance.json'
 p=json.loads(provenance.read_text());p.update(composition=metadata['composition'],meter=metadata['meter'],
    sampled_programs_zero_based=s.programs,musical_final_onset=s.final)
 dump(provenance,p)
 print('CONTEXT_SCORE_COMPLETE',identifier,flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('work',choices=WORKS);ap.add_argument('--output',type=Path,required=True)
 ap.add_argument('--soundfont',type=Path,help='GeneralUser GS v2.0.3 SF2, acquired separately')
 ap.add_argument('--fluidsynth',type=Path,help='FluidSynth 2.6.1 executable, acquired separately')
 a=ap.parse_args()
 if a.work!='victory-circuit' and (not a.soundfont or not a.fluidsynth):ap.error('This score needs --soundfont and --fluidsynth')
 build(a.work,a.output.resolve(),a.soundfont,a.fluidsynth)
