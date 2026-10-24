"""Package verified triptych assets and update the existing site's content catalog."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

from PIL import Image,ImageDraw,ImageFont

from compose import WORKS
from render import Film

HERE=Path(__file__).resolve().parent
SITE=HERE.parents[1]/"docs"
TITLES={"still-current":"靜流","phase-index":"相位索引","amber-hours":"琥珀時光"}
SUMMARIES={"still-current":"無鼓聲景，讓等高線隨質地緩慢匯流。",
           "phase-index":"機械脈衝與方塊重組，十六小節逐步變形。",
           "amber-hours":"慢速碎拍與暖鍵盤，紙片唱盤拆解再歸位。"}
DESCRIPTIONS={
    "still-current":"32 秒原創 Ambient。緩慢的加法合成長音、泛音振幅變化與濾波噪聲形成聲景，沒有鼓或固定拍點。薄荷色等高線吸收暖色核心，擴張後回到安定狀態；動畫依秒數、和聲與質地變化編排。",
    "phase-index":"30 秒、128 BPM 原創 Techno。以單一和聲中心、濾波脈衝動機、合成鼓與低音推進，十六小節逐步增加明亮度和節奏層次。十六個實心模組組裝、旋轉與壓縮，並在最後一次有效起音合為單一標記。",
    "amber-hours":"32 秒、90 BPM 原創 Downtempo。略為延後的 backbeat、切分鼓型、柔和合成鍵盤及低音交替呼應。暖色紙片唱盤隨實際鼓點與鍵盤起音活動，中段拆成三片再回到完整構圖；沒有使用黑膠或第三方歌曲取樣。"}


def digest(file):return hashlib.sha256(file.read_bytes()).hexdigest()


def link(path):return path.as_posix()+"?v="+digest(SITE/path)[:12]


def publish(build):
    media=SITE/"demos/electronic-triptych";media.mkdir(parents=True,exist_ok=True)
    sources={"created":"2026-10-24","composition_and_graphics":"Original work created for bigtongue5566 Skill Library",
             "recordings":"None; oscillator and generated-noise synthesis only",
             "audio_engine_commit":"3e951db9996ae04ca78483d70fca2d0b24768a3a",
             "video_pipeline_commit":"0cce192eb8739b0310b44f66b8dfe11a9c0ffc02",
             "font":{"name":"Space Grotesk","license":"SIL OFL 1.1","upstream":"https://github.com/floriankarsten/space-grotesk"},
             "files":{}}
    for folder in ("engine","video_pipeline","fonts"):
        for file in sorted((HERE/folder).iterdir()):
            if file.is_file():sources["files"][file.relative_to(HERE).as_posix()]=digest(file)
    (HERE/"sources.json").write_text(json.dumps(sources,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    records=[];covers=[]
    for identifier,work in WORKS.items():
        root=build/identifier;out=root/"outputs"
        qc=json.loads((out/f"{identifier}-qc.json").read_text())
        sync=json.loads((out/f"{identifier}-sync-checks.json").read_text())
        if qc["decode_errors"] or qc["decoded_frames"]!=round(work["duration"]*30) or not sync["picture_packets_unchanged"]:
            raise ValueError("Cannot publish an unverified film")
        # Readable title + fully formed focal object rather than a tiny intro.
        poster_time={"still-current":30.5,"phase-index":5.5,"amber-hours":12.5}[identifier]
        film=Film(root);film.save(poster_time,out/f"{identifier}-poster.jpg")
        covers.append(Image.open(out/f"{identifier}-poster.jpg").copy())
        project=HERE/"projects"/identifier;project.mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/"project.json",project/"project.json")
        metadata=json.loads((root/"work/music-metadata.json").read_text())
        if "audio_import" in metadata:metadata=metadata["audio_import"]["source_metadata"]
        (project/"music-metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
        for name in ("cues.json","note-events.json"):
            shutil.copy2(root/"work"/name,project/name)
        for name in (f"{identifier}-music.mid",f"{identifier}-qc.json",f"{identifier}-audio-qc.json",
                     f"{identifier}-provenance.json",f"{identifier}-soundtrack-source.json",f"{identifier}-sync-checks.json",
                     f"{identifier}-production.md",f"{identifier}-audio-production.md"):
            shutil.copy2(out/name,project/name)
        shutil.copy2(root/"work/visual-review/storyboard.jpg",project/"storyboard.jpg")
        shutil.copy2(root/"work/visual-review/motion-filmstrip.jpg",project/"motion-filmstrip.jpg")
        shutil.copy2(root/"work/encoded-review/ending-filmstrip.jpg",project/"ending-filmstrip.jpg")
        for name in (f"{identifier}.mp4",f"{identifier}.m4a",f"{identifier}-poster.jpg",f"{identifier}-qc.json",
                     f"{identifier}-audio-qc.json",f"{identifier}-soundtrack-source.json",f"{identifier}-sync-checks.json"):
            shutil.copy2(out/name,media/name)
        base=Path("demos/electronic-triptych")
        common={"title":TITLES[identifier],"subtitle":work["name"],"summary":SUMMARIES[identifier],
                "description":DESCRIPTIONS[identifier],"poster":link(base/f"{identifier}-poster.jpg"),
                "source":"https://github.com/bigtongue5566/bigtongue5566.github.io/tree/main/examples/electronic-triptych",
                "rights":"https://github.com/bigtongue5566/bigtongue5566.github.io/blob/main/examples/electronic-triptych/RIGHTS.md",
                "credits":"原創編曲、振盪器／噪聲合成與向量動畫；Space Grotesk 字型依 OFL 1.1 使用。來源套件含完整程式、音符、時間表、授權及實際成品檢查。",
                "chapters":[{"time":a,"title":l} for a,b,r,l in work["sections"]],
                "revision":"2026-10-24-electronic-triptych"}
        timing="FREE TIME" if identifier=="still-current" else f"{work['bpm']} BPM"
        records.append({**common,"id":identifier,"type":"video","src":link(base/f"{identifier}.mp4"),
                        "audio":link(base/f"{identifier}.m4a"),"relatedDemoId":identifier+"-music",
                        "facts":[f"{work['duration']} SEC","1080p",work["style"].upper(),timing],
                        "contributors":[{"skillId":"motion-graphics-video","role":"原創構圖、物件動畫、音畫 cue、合成與影片驗證"},
                                        {"skillId":"electronic-music-production","role":"原創編曲、合成音色、混音與母帶"}]})
        records.append({**common,"id":identifier+"-music","title":TITLES[identifier]+"・原創配樂",
                        "subtitle":work["name"]+" — Original Soundtrack","type":"audio",
                        "src":link(base/f"{identifier}.m4a"),"relatedDemoId":identifier,
                        "description":DESCRIPTIONS[identifier]+" 可獨立播放；音符 MIDI 不包含完整合成音色，請以附帶程式重建。",
                        "facts":[f"{work['duration']} SEC",work["style"].upper(),timing,"ORIGINAL SYNTHESIS"],
                        "contributors":[{"skillId":"electronic-music-production","role":"獨立配樂、實際聲音合成、編曲與母帶"}]})
    # One source bundle for the three related works; exclude caches, venvs and
    # bulky intermediates. Include both engine licenses and the font notice.
    archive=media/"sound-form-source.zip"
    files=[p for p in HERE.rglob("*") if p.is_file() and not any(part in ("__pycache__",".venv","work") for part in p.relative_to(HERE).parts)]
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        for file in sorted(files):z.write(file,"electronic-triptych/"+file.relative_to(HERE).as_posix())
    for record in records:record["download"]=link(Path("demos/electronic-triptych/sound-form-source.zip"))
    collection=Image.new("RGB",(1200,630),"#EDF1E9");draw=ImageDraw.Draw(collection)
    font=ImageFont.truetype(str(HERE/"fonts/SpaceGrotesk.ttf"),56)
    small=ImageFont.truetype(str(HERE/"fonts/SpaceGrotesk.ttf"),22)
    draw.text((42,42),"SOUND / FORM",font=font,fill="#153E37")
    draw.text((45,128),"Three original electronic miniatures",font=small,fill="#153E37")
    for i,cover in enumerate(covers):collection.paste(cover.resize((400,225)),(400*i,235))
    draw.text((45,515),"AMBIENT     /     TECHNO     /     DOWNTEMPO",font=small,fill="#153E37")
    draw.text((45,556),"bigtongue5566  /  Skill Library",font=small,fill="#153E37")
    collection.save(media/"collection.jpg",quality=94)
    catalog_path=SITE/"data/catalog.json";catalog=json.loads(catalog_path.read_text(encoding="utf-8"))
    new_ids={r["id"] for r in records}
    catalog["demos"]=records+[d for d in catalog["demos"] if d["id"] not in new_ids]
    collection_record={"id":"electronic-triptych","title":"聲音的三種時間",
                       "summary":"三支全新原創短片：自由流動的 Ambient、機械脈衝 Techno、暖色慢律動 Downtempo。每支附獨立配樂與可重建來源。",
                       "date":"2026-10-24","demoIds":list(WORKS)}
    catalog["collections"]=[collection_record]+[c for c in catalog.get("collections",[]) if c["id"]!="electronic-triptych"]
    for skill in catalog["skills"]:
        ids=list(WORKS) if skill["id"]=="motion-graphics-video" else [id+"-music" for id in WORKS] if skill["id"]=="electronic-music-production" else []
        skill["demoIds"]=ids+[id for id in skill["demoIds"] if id not in ids]
    catalog_path.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("PACKAGED",len(records),"new catalog entries;",len(files),"source files")


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--build",type=Path,required=True)
    args=ap.parse_args();publish(args.build.resolve())
