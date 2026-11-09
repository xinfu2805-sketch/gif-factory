#!/usr/bin/env python3
"""Four-second close-up pilot: contact -> lift -> release -> sink -> water rise."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math, json, subprocess, wave, hashlib
import numpy as np
from stone_state import BEAK, frame_state, audit
ROOT=Path(__file__).resolve().parent; AS=ROOT/'assets'; OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
W,H=1080,1920; FPS=6; SR=48000
POSES={n:Image.open(AS/f'crow-pose-{n:02d}.png').convert('RGBA').resize((780,650),Image.Resampling.LANCZOS) for n in (3,5,9)}
BG=Image.open(AS/'autumn-clearing.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS)
FONT=ImageFont.truetype(str(AS/'MaShanZheng-Regular.ttf'),78)
# All contact points are measured in final-canvas coordinates. Foot baseline stays fixed.
jar=(850,812,1060,1300); neck=(900,755,1000,860); stone_ground=(828,1223)

def draw_water(draw,top,inside):
    draw.rounded_rectangle((864,top,1047,1282),radius=25,fill=(110,186,212,95))
    draw.ellipse((864,top-9,1047,top+12),fill=(143,212,230,145),outline=(240,250,245,210),width=3)

def render(i):
    state=frame_state(i)
    im=BG.copy().convert('RGBA');scene=Image.new('RGBA',(W,H));ground=Image.new('RGBA',(W,H));d=ImageDraw.Draw(ground)
    d.ellipse((780,1270,1070,1320),fill=(72,70,58,47))
    for x,y in [(680,1268),(730,1292),(765,1250)]:d.ellipse((x,y,x+28,y+17),fill=(130,120,103,245),outline=(78,76,70,250),width=2)
    scene.alpha_composite(ground)
    pose=state['pose_asset']
    scene.alpha_composite(POSES[pose],(180,650))
    # The stone appears once: ground contact, attached to beak, free flight, then inside jar.
    overlay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(overlay)
    if state['stage'] in {'GROUND','HELD','RELEASED'}:
        x,y=state['point_px'][0]+80,state['point_px'][1]
        d.ellipse((x-14,y-10,x+14,y+10),fill=(133,120,101,255),outline=(80,77,69,255),width=2)
    scene.alpha_composite(overlay)
    glass=Image.new('RGBA',(W,H));d=ImageDraw.Draw(glass)
    # Water rises only after the released pebble passes the open neck and sinks.
    top=state['water_top_px']
    d.rounded_rectangle(jar,radius=55,fill=(197,225,230,25))
    d.rounded_rectangle(neck,radius=22,fill=(197,225,230,18))
    draw_water(d,top,i>=19)
    d.rounded_rectangle(jar,radius=55,outline=(82,116,130,190),width=6)
    d.rounded_rectangle(neck,radius=22,outline=(82,116,130,180),width=5)
    d.ellipse((894,746,1005,776),outline=(77,114,131,175),width=5)
    d.line((870,875,870,1190),fill=(255,255,250,150),width=7)
    if state['stage'] in {'FALLING_IN_JAR','SUNK'}:
        x,y=state['point_px'][0]+80,state['point_px'][1]
        d.ellipse((x-13,y-10,x+13,y+10),fill=(108,104,92,255),outline=(70,69,66,255),width=2)
        if state['stage']=='FALLING_IN_JAR' and i>=17:
            d.arc((900,top-14,1020,top+18),10,170,fill=(240,251,247,235),width=4)
    scene.alpha_composite(glass)
    im.alpha_composite(scene.crop((80,0,W,H)),(0,0))
    # Text has one strong readable line and a large close-up action area.
    paper=Image.new('RGBA',(W,H));d=ImageDraw.Draw(paper)
    d.rounded_rectangle((78,1450,990,1625),radius=35,fill=(255,249,235,215))
    d.text((540,1533),'一颗小石子，扑通！',font=FONT,anchor='mm',fill=(62,72,60,255),stroke_width=1)
    im.alpha_composite(paper)
    return im.convert('RGB')

def save_wav(path,a):
    a=np.clip(a,-.95,.95);pcm=(a*32767).astype('<i2')
    with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes(pcm.tobytes())

def make_audio():
    N=SR*4;music=np.zeros((N,2),np.float32);fx=np.zeros_like(music);rng=np.random.default_rng(20261109)
    def add(buf,start,waveform,pan=0):
        a=int(start*SR);b=min(N,a+len(waveform));
        if b>a:buf[a:b,0]+=waveform[:b-a]*math.sqrt((1-pan)/2);buf[a:b,1]+=waveform[:b-a]*math.sqrt((1+pan)/2)
    def instrument(f,dur,amp=.1,kind='bell'):
        t=np.arange(int(dur*SR))/SR
        if kind=='bell':base=np.sin(2*math.pi*f*t)+.22*np.sin(2*math.pi*2.01*f*t)+.08*np.sin(2*math.pi*3.97*f*t);env=(1-np.exp(-t*70))*np.exp(-t*4)
        else:base=np.sin(2*math.pi*f*t)+.16*np.sin(2*math.pi*2*f*t);env=np.minimum(1,t*6)*np.minimum(1,(dur-t)*4)
        return (amp*env*base).astype(np.float32)
    # Original 8-note rising-and-resolving melody over a sparse warm harmony.
    for start,notes in [(0,(261.63,329.63,392)),(2,(293.66,349.23,440))]:
        for f in notes:add(music,start,instrument(f,2,.055,'flute'),-.18)
    for j,f in enumerate([392,440,523.25,659.25,587.33,523.25,440,392]):add(music,.15+j*.46,instrument(f,.7,.085),.16)
    def soft_noise(dur,amp):
        n=int(dur*SR);x=rng.standard_normal(n);x=np.convolve(x,np.ones(45)/45,mode='same');x/=max(1e-8,np.max(np.abs(x)))
        return (x*amp*np.sin(np.linspace(0,math.pi,n))).astype(np.float32)
    add(fx,.72,soft_noise(.35,.025),-.35) # stone picked from soil
    add(fx,2.05,soft_noise(.25,.035),.2) # short release arc
    add(fx,2.55,instrument(740,.35,.12),.45) # glassy water plop
    add(fx,2.61,soft_noise(.32,.065),.45) # soft splash
    add(fx,3.1,instrument(520,.55,.045),.2) # lifted water shimmer
    mix=(music*.85+fx)*1.5
    fade=np.minimum(1,np.arange(N)/(.15*SR))*np.minimum(1,(N-np.arange(N))/(.35*SR));mix*=fade[:,None]
    save_wav(OUT/'music-pipeline-test.wav',music);save_wav(OUT/'foley-original.wav',fx);save_wav(OUT/'mix-no-voice.wav',mix)

def main():
    frames=OUT/'frames';frames.mkdir(exist_ok=True)
    for i in range(24):render(i).save(frames/f'{i:03d}.png',compress_level=1)
    make_audio()
    subprocess.run(['ffmpeg','-y','-v','error','-framerate','6','-i',str(frames/'%03d.png'),'-i',str(OUT/'mix-no-voice.wav'),'-t','4','-c:v','libx264','-pix_fmt','yuv420p','-r','6','-c:a','aac','-b:a','192k','-movflags','+faststart',str(OUT/'crow-action-pilot.mp4')],check=True)
    json.dump({'fps':6,'frames':24,'duration':4,'size':[W,H],'pose_assets':[3,5,9],'contact_points':{str(k):[x-80,y] for k,(x,y) in BEAK.items()},'stone_ground':[stone_ground[0]-80,stone_ground[1]],'stone_release_frame':12,'stone_sinks_frames':[15,18],'water_rise_frames':[19,23],'narration':'not available; music and foley only'},open(OUT/'timeline.json','w'),ensure_ascii=False,indent=2)
    checked=audit()
    checked['video_sha256']=hashlib.sha256((OUT/'crow-action-pilot.mp4').read_bytes()).hexdigest()
    checked['source_frame_sha256']={f'{i:03d}':hashlib.sha256((frames/f'{i:03d}.png').read_bytes()).hexdigest() for i in range(24)}
    (ROOT/'review/stone-audit.json').write_text(json.dumps(checked,ensure_ascii=False,indent=2)+'\n')
if __name__=='__main__':main()
