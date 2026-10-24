"""Original deterministic Skia films: fluid contours, kinetic modules, warm collage."""
import argparse
import bisect
import hashlib
import json
import math
from pathlib import Path
import subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image
import skia

HERE = Path(__file__).resolve().parent
W,H,FPS=1920,1080,30


def ease(x):
    x=max(0.,min(1.,x));return x*x*(3-2*x)


def paint(colour,alpha=1.,stroke=0):
    p=skia.Paint(AntiAlias=True,Color=skia.ColorSetARGB(round(255*max(0,min(1,alpha))),
        int(colour[1:3],16),int(colour[3:5],16),int(colour[5:7],16)))
    if stroke:p.setStyle(skia.Paint.kStroke_Style);p.setStrokeWidth(stroke)
    return p


def path(points,closed=False):
    p=skia.Path();p.addPoly(points,closed)
    return p


class Film:
    def __init__(self,root):
        self.root=root
        self.cfg=json.loads((root/"project.json").read_text())
        self.cues=json.loads((root/"work/cues.json").read_text())
        self.id=self.cfg["slug"];self.duration=self.cfg["duration"]
        self.surface=skia.Surface(W,H)
        self.face=skia.Typeface.MakeFromFile(str(HERE/"fonts/SpaceGrotesk.ttf"))
        if self.face is None:raise ValueError("Space Grotesk font missing")
        self.fonts={}

    def text(self,c,text,x,y,size,colour,alpha=1):
        if size not in self.fonts:
            font=skia.Font(self.face,size);font.setEdging(skia.Font.Edging.kAntiAlias)
            self.fonts[size]=font
        c.drawString(text,x,y,self.fonts[size],paint(colour,alpha))

    def rect(self,c,x,y,w,h,colour,alpha=1,r=0):
        rect=skia.Rect.MakeXYWH(x,y,w,h)
        if r:c.drawRoundRect(rect,r,r,paint(colour,alpha))
        else:c.drawRect(rect,paint(colour,alpha))

    def circle(self,c,x,y,r,colour,alpha=1,stroke=0):
        c.drawCircle(x,y,r,paint(colour,alpha,stroke))

    def line(self,c,a,b,colour,alpha=1,width=2):
        c.drawLine(*a,*b,paint(colour,alpha,width))

    def impulse(self,t,key="kicks",decay=14):
        events=self.cues[key];index=bisect.bisect_right(events,t)-1
        return math.exp(-(t-events[index])*decay) if index>=0 else 0.

    def frame(self,t):
        c=self.surface.getCanvas();c.resetMatrix()
        {"still-current":self.current,"phase-index":self.phase,"amber-hours":self.amber}[self.id](c,t)
        return self.surface.makeImageSnapshot()

    def headers(self,c,index,genre,colour,footer):
        self.text(c,"SOUND / FORM",80,72,23,colour)
        self.text(c,index+"   /   "+genre,1330,72,22,colour)
        self.line(c,(80,105),(1840,105),colour,.25,1)
        self.text(c,footer,80,1016,22,colour)
        self.text(c,"ORIGINAL ELECTRONIC MINIATURE",1342,1016,19,colour)

    def current(self,c,t):
        bg,ink="#EDF1E9","#153E37"
        c.clear(skia.ColorSetRGB(237,241,233))
        q=min(t,self.cues["visual_settle"])
        emerge=ease(q/5);join=ease((q-7)/8);open_=ease((q-15)/6);settle=ease((q-24)/6)
        self.headers(c,"01","AMBIENT / FREE TIME",ink,"STILL CURRENT     /     32 SECONDS")
        c.save();c.clipRect(skia.Rect.MakeXYWH(70,120,1780,830))
        # A solid lobe splits into translucent contours; its outline is the
        # same deterministic object throughout, not unrelated transition cards.
        cx=1260-join*170+settle*30;cy=533
        size=(255+open_*80-settle*70)*(.2+.8*emerge)
        theta=np.linspace(0,2*np.pi,181)
        for layer in range(38,-1,-1):
            f=layer/38
            radius=size*(.23+.77*f)
            warp=(.14-.08*settle)*np.sin(3*theta+q*.11+f*.9)
            warp+=(.075-.04*settle)*np.sin(5*theta-q*.07+f)
            xx=cx+radius*(1+warp)*np.cos(theta)*(1.22-open_*.15)
            yy=cy+radius*(1+warp)*np.sin(theta)*(1.05+join*.10)
            xx+=70*math.sin(q*.09+f*1.6)*(1-settle*.8)
            colour="#1B6455" if layer%3 else "#A7C4B4"
            if layer==38:
                c.drawPath(path(list(zip(xx,yy)),True),paint("#C3D8C8",.9))
            else:
                c.drawPath(path(list(zip(xx,yy)),True),paint(colour,.26+f*.27,1.6 if layer%4 else 3))
        # A second source follows an arc into the contour field and becomes
        # its warm core. Its motion stops explicitly before the final frame.
        travel=ease((q-3)/17)
        ox=760+(cx-760)*travel;oy=734-210*math.sin(travel*math.pi/2)
        self.circle(c,ox+6,oy+11,75-35*travel,"#153E37",.07)
        self.circle(c,ox,oy,75-35*travel,"#D79164")
        self.circle(c,ox-12,oy-13,43-20*travel,"#E8B28A",.65)
        for j in range(7):
            rr=88+j*22
            self.circle(c,ox,oy,rr,"#D79164",(.17-j*.018)*(1-travel),1)
        # Clipped horizontal wash gives the second half a new spatial state.
        if open_>0:
            for j in range(7):
                x=np.linspace(700,1830,90)
                y=755+j*22+np.sin(x*.004+q*.08+j*.25)*27*(1-settle*.8)
                c.drawPath(path(list(zip(x,y))),paint("#699A89",open_*(.14-j*.009),2))
        c.restore()
        title_alpha=1-ease((q-6)/2)+ease((q-25)/4)
        self.text(c,"STILL",80,348,136,ink,title_alpha)
        self.text(c,"CURRENT",80,480,136,ink,title_alpha)
        self.text(c,"A space without a grid.",88,549,28,ink,title_alpha)
        words=[("SURFACE",0),("CONFLUENCE",8),("OPEN WATER",16),("STILL",24)]
        label=next(word for word,start in reversed(words) if q>=start)
        self.text(c,label,88,844,27,ink,.8)
        self.text(c,"DRONE / AIR / SLOW HARMONIC MOTION",88,887,19,ink,.65)
        self.line(c,(88,796),(435,796),ink,.30,1)

    def phase(self,c,t):
        final=self.cues["last_compositional_onset"];q=min(t,self.cues["visual_settle"])
        end=ease((q-final)/.65)
        # A limited inversion gives the central development its own hierarchy.
        dark=11.25<=q<22.5
        bg,ink,accent=("#171A17","#F0F0E8","#D4ED44") if dark else ("#F0F0E8","#171A17","#B8D529")
        c.clear(skia.ColorSetRGB(int(bg[1:3],16),int(bg[3:5],16),int(bg[5:7],16)))
        self.headers(c,"02","TECHNO / 128 BPM",ink,"PHASE INDEX     /     16 BARS")
        kick=self.impulse(q);snare=self.impulse(q,"snares",20)
        lead=self.impulse(q,"tonal_onsets",12)
        if q<3.75:word,sub="PHASE","INDEX"
        elif q<11.25:word,sub="LOCK","INTO STEP"
        elif q<22.5:word,sub="SHIFT","REPEAT"
        elif q<final:word,sub="LESS","IS MORE"
        else:word,sub="PHASE","INDEX"
        self.text(c,word,80,360,155,ink)
        self.text(c,sub,88,452,63,ink)
        self.rect(c,88,515,96+kick*34,13,accent)
        self.text(c,"ONE CENTRE.",88,623,27,ink)
        self.text(c,"MANY STATES.",88,661,27,ink)
        bar=min(15,int(q/(240/128)))
        self.text(c,f"{bar+1:02d} / 16",88,875,70,ink,.7)
        # Sixteen solid modules assemble, rotate as a field, compress, then
        # combine into one square on the final actual compositional onset.
        c.save();c.clipRect(skia.Rect.MakeXYWH(785,135,1055,805))
        cx,cy=1320,535
        angle=0
        if dark:
            local=(q-11.25)/(240/128)
            step=math.floor(local)
            angle=(step*45+45*ease((local-step-.72)/.28))%360
        if q>=22.5:angle=45*(1-ease((q-22.5)/1.2))
        angle*=1-end
        c.translate(cx,cy);c.rotate(angle)
        spacing=(163-35*ease((q-22.5)/2))* (1-end)
        for row in range(4):
            for col in range(4):
                j=row*4+col
                enter=ease((q-j*.055)/1.0)
                dx=(col-1.5)*spacing+(1-enter)*(510 if col%2 else -510)
                dy=(row-1.5)*spacing+(1-enter)*(280 if row%2 else -280)
                delay=(j%4)*.045
                active=(bar*3+int(q*128/60))%16
                scale=(.80+.20*enter)*(1+.045*kick)
                side=(131+end*170)*scale
                fill=accent if (j==active or (row+col)%4==0) else ink
                c.save();c.translate(dx,dy)
                localrot=90*ease((q-(bar*240/128)-delay)/.34) if dark and j%3==0 else 0
                c.rotate(localrot*(1-end))
                self.rect(c,-side/2,-side/2,side,side,fill)
                if end<.8 and j%3==0:
                    self.circle(c,0,0,side*.25,bg,1-end)
                elif end<.8 and j%3==1:
                    self.rect(c,-side*.12,-side*.5,side*.24,side,bg,1-end)
                c.restore()
        c.restore()
        # A controlled percussive edge, never full-screen flashing.
        self.rect(c,1824,164,14,650,accent,.22+.65*snare)
        for j in range(16):self.rect(c,850+j*61,902,42,5,accent if j<=bar else ink,1 if j<=bar else .15)

    def amber(self,c,t):
        q=min(t,self.cues["visual_settle"]);end=ease((q-self.cues["last_compositional_onset"])/1.1)
        bg,ink="#F4E9D7","#532D36"
        c.clear(skia.ColorSetRGB(244,233,215))
        self.headers(c,"03","DOWNTEMPO / 90 BPM",ink,"AMBER HOURS     /     TAKE IT SLOW")
        kick=self.impulse(q,decay=9);snare=self.impulse(q,"snares",10)
        onset=self.impulse(q,"tonal_onsets",4)
        enter=ease(q/2.3);turn=(q*.085+.035*math.sin(q*.5))*(1-end)+2.4*end
        # Broad paper planes establish a warm layered world; they arrive in
        # order, creating an actual masked reveal of the record-like subject.
        c.save();c.clipRect(skia.Rect.MakeXYWH(720,145,1120,780))
        self.rect(c,760+250*(1-ease((q-.2)/1.4)),220,940,565,"#D68C62",1,r=10)
        c.save();c.translate(1320,555);c.rotate(-12+4*math.sin(q*.12)*(1-end))
        self.rect(c,-440,-300+260*(1-ease((q-.65)/1.4)),880,600,"#E5B850",1,r=12)
        c.restore()
        cx=1295+45*math.sin(q*.13)*(1-end);cy=549
        self.circle(c,cx+11,cy+23,298*enter,"#532D36",.12)
        unfold=ease((q-16)/2.3)*(1-ease((q-24)/2.6))
        # At the phrase variation the record separates into three paper
        # sectors. Each retains its groove and label, then returns home.
        for sector in range(3):
            angle=sector*120+60+math.degrees(turn)
            dx=math.cos(math.radians(angle))*unfold*52
            dy=math.sin(math.radians(angle))*unfold*52
            c.save();c.translate(cx+dx,cy+dy);c.rotate(math.degrees(turn))
            wedge=skia.Path();wedge.moveTo(0,0)
            wedge.arcTo(skia.Rect.MakeLTRB(-400,-400,400,400),sector*120,120,False);wedge.close()
            c.clipPath(wedge,doAntiAlias=True)
            self.circle(c,0,0,(298+kick*6)*enter,ink)
            for j in range(24):self.circle(c,0,0,(118+j*6.5)*enter,"#B57864",.24 if j%3 else .43,1.2)
            self.circle(c,0,0,111,["#D8865B","#E8B64C","#F4E9D7"][sector])
            self.circle(c,0,0,16,ink)
            c.restore()
        # The key motif lifts three small orbiting pieces; actual key onsets
        # determine their gentle emphasis, rather than a fake fixed beat.
        for j in range(3):
            a=turn*.8+j*2.094
            x=cx+math.cos(a)*350;y=cy+math.sin(a)*255
            self.circle(c,x+3,y+5,23+onset*9,"#532D36",.10)
            self.circle(c,x,y,23+onset*9,["#D47A55","#F2C966","#8B9C7A"][j])
        # Tone arm settles into place and lifts clear for the final resolution.
        c.save();c.translate(1690,285)
        arm=-38+38*ease((q-2)/3)-22*end-18*unfold
        c.rotate(arm)
        self.circle(c,0,0,32,"#7C826A")
        p=skia.Path();p.moveTo(0,0);p.lineTo(-28,217);p.lineTo(-133,270)
        c.drawPath(p,paint("#EFE4D1",1,18))
        self.rect(c,-157,254,56,27,"#8B9C7A",1,r=5)
        c.restore();c.restore()
        self.text(c,"AMBER",80,347,145,ink)
        self.text(c,"HOURS",80,483,145,ink)
        self.text(c,"Leave a little space.",88,550,29,ink)
        self.line(c,(88,725),(405,725),ink,.3,1)
        self.text(c,"WARM KEYS",88,776,24,ink)
        self.text(c,"BROKEN RHYTHM",88,819,24,ink)
        self.text(c,"SLOW ORBITS",88,862,24,ink)
        # Snare response only changes a small coloured underline.
        self.rect(c,88,895,85+65*snare,9,"#C97850")

    def save(self,t,file):
        arr=self.frame(t).toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
        Image.fromarray(arr).convert("RGB").save(file,quality=94)

    def preview(self):
        folder=self.root/"work/visual-review";folder.mkdir(exist_ok=True)
        times=[1.8,self.duration*.28,self.duration*.52,self.duration*.76,self.duration-1,self.duration-1/FPS]
        images=[]
        for i,t in enumerate(times):
            file=folder/f"key-{i:02d}.jpg";self.save(t,file)
            image=Image.open(file).resize((640,360));images.append(image)
        sheet=Image.new("RGB",(1920,720))
        for i,image in enumerate(images):sheet.paste(image,(i%3*640,i//3*360))
        sheet.save(folder/"storyboard.jpg",quality=94)
        motion_times=[self.duration*.5+v/30 for v in (0,2,4,6,8,10)]
        strip=Image.new("RGB",(1920,720))
        for i,t in enumerate(motion_times):
            arr=self.frame(t).toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)
            strip.paste(Image.fromarray(arr).convert("RGB").resize((640,360)),(i%3*640,i//3*360))
        strip.save(folder/"motion-filmstrip.jpg",quality=94)
        a=self.frame(5.123).tobytes();self.frame(1.0);b=self.frame(5.123).tobytes()
        if a!=b:raise ValueError("Render must reproduce an arbitrary time exactly")
        (folder/"checks.json").write_text(json.dumps({"deterministic_seek":True,"key_times":times,
            "motion_times":motion_times,"final_settle":self.cues["visual_settle"],
            "limits":"Keyframes and filmstrips do not certify full-motion or listening quality."},indent=2))
        self.save(2.8,self.root/"outputs"/f"{self.id}-poster.jpg")
        print("PREVIEW",self.id,flush=True)

    def encode(self,start=0,seconds=None,suffix="picture"):
        duration=self.duration if seconds is None else seconds
        dest=self.root/"work"/f"{suffix}.mp4"
        command=[imageio_ffmpeg.get_ffmpeg_exe(),"-hide_banner","-loglevel","error","-y",
                 "-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgba","-s",f"{W}x{H}",
                 "-r",str(FPS),"-i","pipe:0","-an","-c:v","libx264","-preset","fast",
                 "-crf","19","-pix_fmt","yuv420p","-movflags","+faststart",str(dest)]
        with (self.root/"work"/f"{suffix}-encode.log").open("w") as log:
            process=subprocess.Popen(command,stdin=subprocess.PIPE,stderr=log)
            try:
                for frame in range(round(duration*FPS)):
                    image=self.frame(start+frame/FPS)
                    process.stdin.write(image.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType).tobytes())
                    if frame%240==0:print("FRAMES",self.id,frame,round(duration*FPS),flush=True)
            finally:process.stdin.close()
            if process.wait():raise RuntimeError("Encoding failed; see render log")
        print("PICTURE_COMPLETE",self.id,flush=True)


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project",type=Path,required=True)
    ap.add_argument("--mode",choices=("preview","study","render"),default="preview")
    args=ap.parse_args();film=Film(args.project.resolve())
    if args.mode=="preview":film.preview()
    elif args.mode=="study":film.encode(start=film.duration*.49,seconds=1.5,suffix="motion-study")
    else:film.encode()
