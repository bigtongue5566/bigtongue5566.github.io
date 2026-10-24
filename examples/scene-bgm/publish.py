"""Make five original cover designs and publish verified audio in the site catalog."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import zipfile

from PIL import Image,ImageDraw,ImageFont
from compose import WORKS,dump

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
SITE=REPO/'docs'
COLORS={
 'victory-circuit':('#111226','#F4EFEB','#D0FF53','#EB517A'),
 'daybreak-proposal':('#E8EDE5','#183E39','#7EAB91','#F5C674'),
 'cloudside-cafe':('#E9E9F6','#423C63','#BAA3E3','#F2BB81'),
 'jade-wind-ascent':('#EAE9DE','#254A42','#6D9980','#CAAD77'),
 'almost-yours':('#F1DFDD','#653D4F','#C7828F','#E8B998')}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resource(p):return p.relative_to(SITE).as_posix()+'?v='+digest(p)[:12]

def cover(identifier,dest):
 w=WORKS[identifier];bg,ink,accent,warm=COLORS[identifier]
 im=Image.new('RGB',(1920,1080),bg);d=ImageDraw.Draw(im)
 font=lambda size:ImageFont.truetype(str(HERE/'fonts/SpaceGrotesk.ttf'),size)
 cn=ImageFont.truetype('C:/Windows/Fonts/msjh.ttc',52)
 d.line((80,138,1840,138),fill=ink,width=2)
 d.text((80,67),'SCENE / SOUND',font=font(26),fill=ink)
 d.text((1530,67),'ORIGINAL BGM',font=font(26),fill=ink)
 title={ 'victory-circuit':['VICTORY','CIRCUIT'], 'daybreak-proposal':['DAYBREAK','PROPOSAL'],
   'cloudside-cafe':['CLOUDSIDE','CAFE'], 'jade-wind-ascent':['JADE WIND','ASCENT'], 'almost-yours':['ALMOST','YOURS']}[identifier]
 for i,line in enumerate(title):d.text((80,248+i*106),line,font=font(88),fill=ink)
 d.text((86,500),w['title'],font=cn,fill=ink)
 d.text((86,645),w['family'],font=font(23),fill=ink)
 d.text((86,698),f'60 SEC    /    {w["bpm"]} BPM    /    '+('6/8' if w['meter']==3 else '4/4'),font=font(24),fill=ink)
 d.text((80,970),'bigtongue5566   /   Skill Library',font=font(24),fill=ink)
 d.text((1520,970),'FIVE SCENES / '+str(list(WORKS).index(identifier)+1).zfill(2),font=font(24),fill=ink)
 if identifier=='victory-circuit':
    # A circuit winds into a broad winner's crest, with one raised bright rail.
    d.polygon([(1140,254),(1650,254),(1760,430),(1610,747),(1395,850),(1180,747),(1030,430)],fill=accent)
    d.polygon([(1210,335),(1580,335),(1663,439),(1540,680),(1395,756),(1250,680),(1127,439)],fill=bg)
    for i,x in enumerate([1210,1330,1450,1570]):
      height=[115,195,270,195][i]
      d.rounded_rectangle((x,650-height,x+65,650),radius=13,fill=warm if i==2 else accent)
    d.line([(1040,810),(1175,810),(1175,899),(1620,899),(1620,818),(1780,818)],fill=warm,width=9)
    for x,y in [(1040,810),(1780,818)]:d.ellipse((x-13,y-13,x+13,y+13),fill=warm)
 elif identifier=='daybreak-proposal':
    d.ellipse((1240,235,1720,715),fill=warm)
    for i,(x,y) in enumerate([(1010,540),(1230,440),(1450,340)]):
      d.rounded_rectangle((x,y,x+235,850),radius=28,fill=accent if i%2==0 else ink)
      d.line((x+35,y+68,x+195,y+68),fill=bg,width=8)
      d.line((x+35,y+100,x+146,y+100),fill=bg,width=4)
      d.ellipse((x+40,765,x+76,801),fill=warm)
    d.line([(1055,460),(1268,365),(1487,270),(1650,270)],fill=ink,width=11)
    d.polygon([(1650,270),(1600,240),(1600,300)],fill=ink)
 elif identifier=='cloudside-cafe':
    d.rounded_rectangle((1040,520,1760,850),radius=75,fill=accent)
    for x,y,r in [(1170,485,140),(1390,390,185),(1590,495,145)]:d.ellipse((x-r,y-r,x+r,y+r),fill='#FAF7ED')
    d.rounded_rectangle((1040,420,1740,650),radius=95,fill='#FAF7ED')
    for x in (1240,1490):d.ellipse((x,510,x+26,546),fill=ink)
    d.arc((1310,510,1440,602),0,180,fill=ink,width=9)
    for x,y in [(1100,720),(1260,780),(1550,725),(1700,800)]:
      d.ellipse((x-38,y-38,x+38,y+38),fill=warm)
      d.line((x-17,y,x+17,y),fill=ink,width=6);d.line((x,y-17,x,y+17),fill=ink,width=6)
 elif identifier=='jade-wind-ascent':
    d.ellipse((1470,238,1750,518),fill=warm)
    for points,color in [([(950,850),(1110,580),(1200,650),(1400,360),(1600,640),(1740,520),(1835,850)],accent),
       ([(1020,890),(1240,630),(1370,760),(1515,550),(1800,890)],ink)]:d.polygon(points,fill=color)
    d.line([(995,720),(1145,720),(1250,680),(1370,680),(1465,635),(1790,635)],fill=bg,width=14)
    d.line([(1030,804),(1190,804),(1310,760),(1460,760),(1580,710),(1820,710)],fill=warm,width=6)
    # Three simple birds, no real brand or photographed landscape.
    for x,y in [(1190,375),(1270,333),(1340,388)]:
      d.line([(x-20,y),(x,y+10),(x+20,y)],fill=ink,width=5)
 elif identifier=='almost-yours':
    # Two independent shapes share one quiet overlap.
    d.ellipse((1050,325,1510,825),fill=accent)
    d.ellipse((1300,250,1760,750),fill=warm)
    d.arc((1170,400,1650,910),205,330,fill=ink,width=12)
    d.arc((1030,220,1780,940),218,328,fill=bg,width=10)
    d.line([(1390,428),(1418,470),(1466,480),(1429,512),(1436,560),(1390,538),(1347,560),(1355,512),(1318,480),(1365,470),(1390,428)],fill=bg,width=5)
    for x,y,r in [(1160,265,12),(1740,820,17),(1690,226,9)]:d.ellipse((x-r,y-r,x+r,y+r),fill=ink)
 dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest,quality=94)
 return im

def publish(build,local_outputs=None):
 media=SITE/'demos/scene-bgm';media.mkdir(parents=True,exist_ok=True)
 records=[];covers=[];source_records={}
 for identifier,w in WORKS.items():
    root=build/identifier;out=root/'outputs'
    qc=json.loads((out/f'{identifier}-qc.json').read_text())
    meta=json.loads((root/'work/music-metadata.json').read_text())
    if qc['full_decode_errors'] or qc['wav']['samples']!=2880000 or qc['unexpected_chord_conflicts']:
      raise ValueError('Unverified score '+identifier)
    if qc['aac_sha256']!=digest(out/f'{identifier}.m4a'):raise ValueError('Changed audio since QC')
    if abs(meta['last_effective_onset']-meta['musical_final_onset'])>1e-5:raise ValueError('Unresolved ending')
    # Keep actual notes, MIDI, instrument provenance and measurements reviewable.
    project=HERE/'projects'/identifier;project.mkdir(parents=True,exist_ok=True)
    shutil.copy2(root/'project.json',project/'project.json')
    for name in ('note-events.json','music-metadata.json'):shutil.copy2(root/'work'/name,project/name)
    for suffix in ('music.mid','qc.json','provenance.json','production.md'):
      shutil.copy2(out/f'{identifier}-{suffix}',project/f'{identifier}-{suffix}')
    for suffix in ('.m4a','-qc.json'):
      shutil.copy2(out/f'{identifier}{suffix}',media/f'{identifier}{suffix}')
    covers.append(cover(identifier,media/f'{identifier}-cover.jpg'))
    source_records[identifier]={'aac_sha256':digest(out/f'{identifier}.m4a'),
       'sampled_programs_zero_based':meta['sampled_programs_zero_based'],
       'soundfont_sha256':meta['soundfont_sha256'],'last_effective_onset':meta['last_effective_onset']}
    records.append(dict(id=identifier,title=w['title'],subtitle=w['name'],summary=w['summary'],description=w['description'],type='audio',
      poster=resource(media/f'{identifier}-cover.jpg'),src=resource(media/f'{identifier}.m4a'),
      facts=[w['context'],'60 SEC',f'{w["bpm"]} BPM','6/8' if w['meter']==3 else w['family']],
      source='https://github.com/bigtongue5566/bigtongue5566.github.io/tree/main/examples/scene-bgm',
      rights='https://github.com/bigtongue5566/bigtongue5566.github.io/blob/main/examples/scene-bgm/RIGHTS.md',
      credits=('原創編曲與電子聲音；'+('取樣樂器使用 GeneralUser GS 2.0.3／FluidSynth 2.6.1，曲目來源頁列出實際音色。' if meta['sampled_programs_zero_based'] else '全曲使用振盪器及噪聲合成，未使用取樣音源。')+'封面為原創圖形。'),
      chapters=[dict(time=s['start'],title=s['label']) for s in meta['sections']],
      contributors=[dict(skillId='electronic-music-production',role='原創旋律、情境編曲、音源渲染、混音與母帶')],
      revision='2026-10-24-five-scene-bgm'))
    if local_outputs:
      local_outputs.mkdir(parents=True,exist_ok=True)
      for suffix in ('.m4a','-master.wav','-music.mid','-qc.json'):
        shutil.copy2(out/f'{identifier}{suffix}',local_outputs/f'{identifier}{suffix}')
 dump(HERE/'sources.json',dict(created='2026-10-24',composition='Five original bespoke arrangements, no third-party songs or song recordings',
   soundfont=dict(name='GeneralUser GS',version='2.0.3',upstream='https://github.com/mrbumpy409/GeneralUser-GS',
     license='GeneralUser-GS-LICENSE.txt; instrument samples rendered into music, SF2 not bundled'),
   renderer=dict(name='FluidSynth',version='2.6.1',upstream='https://github.com/FluidSynth/fluidsynth/releases/tag/v2.6.1'),
   font=dict(name='Space Grotesk',license='OFL 1.1',upstream='https://github.com/floriankarsten/space-grotesk'),
   chinese_cover_font='Locally installed Microsoft JhengHei, used for cover rendering; font binary not redistributed',
   tracks=source_records,engine_sha256={p.name:digest(p) for p in (HERE/'engine').glob('*.py')}))
 archive=media/'five-scenes-source.zip'
 with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(HERE.rglob('*')):
      if p.is_file() and not any(x in ('.venv','__pycache__','work','outputs') for x in p.relative_to(HERE).parts):
        z.write(p,'scene-bgm/'+p.relative_to(HERE).as_posix())
 for record in records:record['download']=resource(archive)
 catalog_path=SITE/'data/catalog.json';catalog=json.loads(catalog_path.read_text(encoding='utf-8'))
 ids=set(WORKS);catalog['demos']=records+[d for d in catalog['demos'] if d['id'] not in ids]
 collection=dict(id='scene-bgm',title='五個場景・五種聲音',date='2026-10-24',
   summary='五首全新原創 BGM：電競賽事、商業簡報、休閒遊戲、仙俠與戀愛時刻。每首一分鐘，附可編輯 MIDI、音源來源與重建程式。',demoIds=list(WORKS))
 catalog['collections']=[collection]+[c for c in catalog.get('collections',[]) if c['id']!='scene-bgm']
 for skill in catalog['skills']:
    if skill['id']=='electronic-music-production':skill['demoIds']=list(WORKS)+[x for x in skill['demoIds'] if x not in ids]
 dump(catalog_path,catalog)
 # A readable five-cover press image / social thumbnail.
 im=Image.new('RGB',(1500,940),'#EAEDE5');d=ImageDraw.Draw(im)
 f=ImageFont.truetype(str(HERE/'fonts/SpaceGrotesk.ttf'),60)
 small=ImageFont.truetype(str(HERE/'fonts/SpaceGrotesk.ttf'),23)
 d.text((45,34),'FIVE SCENES / FIVE SOUNDS',font=f,fill='#183E39')
 d.text((49,121),'ESPORTS   /   BUSINESS   /   CASUAL GAME   /   FANTASY   /   ROMANCE',font=small,fill='#183E39')
 for i,c in enumerate(covers):im.paste(c.resize((480,270)),(15+(i%3)*495,205+(i//3)*290))
 d.text((49,848),'Original BGM collection   /   60 seconds each   /   Skill Library',font=small,fill='#183E39')
 im.save(media/'collection.jpg',quality=94)
 print('PUBLISHED_CONTENT',len(records),'scores;',len(catalog['demos']),'total demos',flush=True)

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--build',type=Path,required=True)
 ap.add_argument('--local-outputs',type=Path)
 args=ap.parse_args();publish(args.build.resolve(),args.local_outputs.resolve() if args.local_outputs else None)
