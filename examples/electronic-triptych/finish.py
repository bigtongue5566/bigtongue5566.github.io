"""Use the updated motion skill's finished-score import path, then verify cues."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import imageio_ffmpeg

HERE=Path(__file__).resolve().parent


def video_hash(ff,path):
    return subprocess.check_output([ff,"-v","error","-i",str(path),"-map","0:v:0","-c","copy","-f","hash","-"]).decode().strip()


def finish(root):
    cfg=json.loads((root/"project.json").read_text())
    cfg.update(width=1920,height=1080,fps=30,brand={"primary":"#153E37","secondary":"#D79164","accent":"#B8D529","ink":"#171A17"})
    cfg["scenes"]=[{"start":s["start"],"end":s["end"],"chapter":s["label"],
                     "music_role":{"texture":"break","evolution":"groove","release":"outro"}.get(s["role"],s["role"])} for s in cfg["sections"]]
    (root/"project.json").write_text(json.dumps(cfg,indent=2),encoding="utf-8")
    subprocess.run([sys.executable,str(HERE/"video_pipeline/finish_video.py"),"--project",str(root),
                    "--audio",str(root/"outputs"/f"{cfg['slug']}-master.wav"),
                    "--audio-metadata",str(root/"work/music-metadata.json")],check=True)
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    picture=video_hash(ff,root/"work/picture.mp4");muxed=video_hash(ff,root/"outputs"/f"{cfg['slug']}.mp4")
    if picture!=muxed:raise ValueError("Picture packets changed during mux")
    cues=json.loads((root/"work/cues.json").read_text())
    events=json.loads((root/"work/note-events.json").read_text())
    last=max(e["time"] for e in events)
    if abs(last-cues["last_compositional_onset"])>1e-5:raise ValueError("Final composition onset does not match visual cue")
    if cues["pulse"]=="free" and cues["kicks"]:raise ValueError("Free-time work unexpectedly contains kicks")
    # Export final and fast-motion frame strips from the encoded film itself.
    folder=root/"work/encoded-review";folder.mkdir(exist_ok=True)
    from PIL import Image
    times=[cues["visual_settle"]-0.3,cues["visual_settle"],cfg["duration"]-1/30]
    tiles=[]
    for i,t in enumerate(times):
        file=folder/f"end-{i}.jpg"
        subprocess.run([ff,"-v","error","-y","-ss",str(t),"-i",str(root/"outputs"/f"{cfg['slug']}.mp4"),
                        "-frames:v","1",str(file)],check=True)
        tiles.append(Image.open(file).resize((640,360)))
    sheet=Image.new("RGB",(1920,360))
    for i,tile in enumerate(tiles):sheet.paste(tile,(i*640,0))
    sheet.save(folder/"ending-filmstrip.jpg",quality=94)
    from render import Film
    import numpy as np
    reference=Film(root).frame(times[-1]).toarray(colorType=__import__("skia").ColorType.kRGBA_8888_ColorType)
    encoded=np.asarray(Image.open(folder/"end-2.jpg").convert("RGB"))
    # Check the encoded final frame against the intended palette. Native Skia
    # surfaces may be BGRA; the encoder explicitly receives RGBA in render.py.
    pixel_error=int(np.max(np.abs(encoded[150,100].astype(int)-reference[150,100,:3].astype(int))))
    if pixel_error>6:raise ValueError("Encoded palette differs from the intended frame")
    report={"picture_packets_unchanged":True,"picture_packet_hash":picture,"background_colour_max_channel_error":pixel_error,
            "actual_last_event_seconds":last,"declared_last_event_seconds":cues["last_compositional_onset"],
            "visual_settle_seconds":cues["visual_settle"],"duration_seconds":cfg["duration"],
            "cue_source":"actual composed note and percussion events; no inferred/fabricated beat grid",
            "audio_master_sha256":hashlib.sha256((root/"outputs"/f"{cfg['slug']}-master.wav").read_bytes()).hexdigest(),
            "limits":"Decoded-frame, sample and symbolic-cue checks do not certify subjective listening quality."}
    (root/"outputs"/f"{cfg['slug']}-sync-checks.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print("FILM_COMPLETE",cfg["slug"],flush=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--project",type=Path,required=True)
    args=ap.parse_args();finish(args.project.resolve())
