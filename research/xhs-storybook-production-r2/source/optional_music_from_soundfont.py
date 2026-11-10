#!/usr/bin/env python3
"""Original sleep-time sampled-instrument score; no externally downloaded or commercial music.
Only mixes original existing approved visual master + existing FX, no robot voice.
Uses TimGM6mb.sf2 via FluidSynth; license text included in deliverables.
"""
from pathlib import Path
import ctypes as C
import math, subprocess, json, hashlib
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt
ROOT=Path(__file__).resolve().parent
BASE=Path('/mnt/data')
VIDEO=BASE/'xhs_crow_animation_v1/out/乌鸦喝水_完整绘本_动态预览_无旁白.mp4'
FOLEY=BASE/'xhs_crow_animation_v1/out/FX_ONLY_no_voice_no_music.wav'
SOUNDFONT=Path('/usr/share/sounds/sf2/TimGM6mb.sf2')
SR=48000; DUR=33.3; N=int(SR*DUR)
fl=C.CDLL('libfluidsynth.so.3')
fl.new_fluid_settings.restype=C.c_void_p
fl.fluid_settings_setnum.argtypes=[C.c_void_p,C.c_char_p,C.c_double]; fl.fluid_settings_setnum.restype=C.c_int
fl.fluid_settings_setint.argtypes=[C.c_void_p,C.c_char_p,C.c_int]; fl.fluid_settings_setint.restype=C.c_int
fl.new_fluid_synth.argtypes=[C.c_void_p]; fl.new_fluid_synth.restype=C.c_void_p
fl.fluid_synth_sfload.argtypes=[C.c_void_p,C.c_char_p,C.c_int]; fl.fluid_synth_sfload.restype=C.c_int
fl.fluid_synth_program_change.argtypes=[C.c_void_p,C.c_int,C.c_int]
fl.fluid_synth_noteon.argtypes=[C.c_void_p,C.c_int,C.c_int,C.c_int]
fl.fluid_synth_noteoff.argtypes=[C.c_void_p,C.c_int,C.c_int]
fl.fluid_synth_write_float.argtypes=[C.c_void_p,C.c_int,C.c_void_p,C.c_int,C.c_int,C.c_void_p,C.c_int,C.c_int]; fl.fluid_synth_write_float.restype=C.c_int
fl.delete_fluid_synth.argtypes=[C.c_void_p]; fl.delete_fluid_settings.argtypes=[C.c_void_p]
s=fl.new_fluid_settings(); fl.fluid_settings_setnum(s,b'synth.sample-rate',SR);fl.fluid_settings_setnum(s,b'synth.gain',0.33)
fl.fluid_settings_setint(s,b'synth.polyphony',128)
fl.fluid_settings_setnum(s,b'synth.reverb.room-size',.58);fl.fluid_settings_setnum(s,b'synth.reverb.level',.36)
fl.fluid_settings_setnum(s,b'synth.chorus.level',.16)
syn=fl.new_fluid_synth(s); assert fl.fluid_synth_sfload(syn,str(SOUNDFONT).encode(),1)>=0
# soft piano, harp, music box, quiet string pad, breathy flute
instruments={0:0,1:46,2:10,3:48,4:73}
for ch,prg in instruments.items():fl.fluid_synth_program_change(syn,ch,prg)
B=1.0 # 60 BPM, slow bedtime pulse
# very gentle, eight 4-second measures across 32s, one final sustained resolution
bars=[
 dict(name='Cmaj9',bass=48,chord=[60,64,67,74],mel=[(0,76,1.55),(2,79,.9),(3,76,.8)]),
 dict(name='G/B',bass=47,chord=[59,62,67,71],mel=[(.3,74,1.4),(2,76,.9),(3,72,.7)]),
 dict(name='Am7',bass=45,chord=[57,60,64,67],mel=[(.25,72,1.7),(2.5,76,1.1)]),
 dict(name='Fmaj7',bass=41,chord=[57,60,64,69],mel=[(.4,72,1.2),(2,69,1.7)]),
 dict(name='Dm7',bass=38,chord=[53,57,60,65],mel=[(.2,74,1.3),(2,72,1.4)]),
 dict(name='C/E',bass=40,chord=[55,60,64,67],mel=[(.1,76,1.55),(2.25,79,1.25)]),
 dict(name='Gsus4',bass=43,chord=[55,60,62,67],mel=[(.4,79,1.45),(2.4,74,1.3)]),
 dict(name='Cmaj9',bass=48,chord=[60,64,67,71],mel=[(.15,76,1.7),(2.3,72,1.7)]),
]
E=[]
def note(ch,p,v,start,dur):
 if start<0 or start>=DUR:return
 E.append((max(0,round(start*SR)),1,ch,p,int(v)))
 E.append((min(N-1,round((start+dur)*SR)),0,ch,p,0))
for i,b in enumerate(bars):
 t=i*4*B; c=b['chord']
 # quiet sustained harmonic bed, less prominent than piano
 for n in c[:3]:note(3,n,20 if i<5 else 23,t+.12,3.67)
 # soft piano warm sparse progression, not bright staccato
 note(0,b['bass']+12,42 if i%2 else 44,t+.02,2.9)
 note(0,c[1]+12,28,t+2.1,1.65)
 # low harp arpeggio in slow waves (5 notes/bar)
 for j,(offset,p) in enumerate([(0,c[0]+12),(.8,c[1]+12),(1.65,c[2]+12),(2.55,c[1]+12),(3.25,c[0]+12)]):
  note(1,p,30 if j%2 else 34,t+offset,.8)
 # only 2–3 melody notes each bar; rest matters for sleepy feel
 for j,(off,p,dur) in enumerate(b['mel']):
  note(2,p,36 if i<5 else 32,t+off,dur)
 # very slight flute lift for resolution, avoid constant layer
 if i in (3,7):note(4,c[2]+12,26,t+.6,2.4)
E.sort(key=lambda x:(x[0],x[1]))
y=np.zeros((N,2),dtype=np.float32);l=np.zeros(512,np.float32);r=np.zeros(512,np.float32)
i=0;j=0
while i<N:
 while j<len(E) and E[j][0]<=i:
  _,on,ch,p,v=E[j];(fl.fluid_synth_noteon(syn,ch,p,v) if on else fl.fluid_synth_noteoff(syn,ch,p)); j+=1
 nextt=E[j][0] if j<len(E) else N
 n=min(512,N-i,max(1,nextt-i))
 fl.fluid_synth_write_float(syn,n,l.ctypes.data,0,1,r.ctypes.data,0,1)
 y[i:i+n,0]=l[:n];y[i:i+n,1]=r[:n];i+=n
fl.delete_fluid_synth(syn);fl.delete_fluid_settings(s)
# soften GM soundfont's harsh highs, retain spacious but quiet dynamics
for ch in range(2):y[:,ch]=sosfilt(butter(2,4500,fs=SR,output='sos'),y[:,ch])
# 120ms cross channel reflection for warm space, not echoey
ref=y.copy();d=int(.13*SR)
y[d:,0]+=.085*ref[:-d,1];y[d:,1]+=.085*ref[:-d,0]
t=np.arange(N,dtype=np.float32)/SR
fade=np.clip(t/2.2,0,1)*np.clip((DUR-t)/2.8,0,1)
y*=fade[:,None]
# keep musical headroom, avoid loud score near sound effects
pk=float(np.max(np.abs(y))); y*=.21/max(pk,1e-6)
sf.write(ROOT/'睡前摇篮曲_原创配乐_33秒.wav',y,SR,subtype='PCM_16')
fx,srf=sf.read(FOLEY,dtype='float32',always_2d=True)
if srf!=SR: raise ValueError('foley sample rate mismatch')
if len(fx)<N: fx=np.pad(fx,((0,N-len(fx)),(0,0)))
fx=fx[:N]
# preserve original environmental effects, but lower them to avoid startling children
mix=np.clip((y*.87+fx*.52)*2.2387,-.95,.95)  # +7dB mobile listening master, preserves music/FX balance
sf.write(ROOT/'睡前摇篮曲_音乐加音效_独立混音.wav',mix,SR,subtype='PCM_16')
video_out=ROOT/'乌鸦喝水_33秒睡前摇篮曲版_无旁白.mp4'
subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-v','error','-i',str(VIDEO),'-i',str(ROOT/'睡前摇篮曲_音乐加音效_独立混音.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t',str(DUR),'-movflags','+faststart',str(video_out)],check=True)
manifest={
 'video':str(video_out.name), 'source_video':str(VIDEO), 'source_foley':str(FOLEY),
 'duration_s':DUR,'recorded_instrument_sample_bank':'TimGM6mb.sf2 / GPL-2',
 'track_status':'ORIGINAL_NEW_SCORE_NOT_MIXKIT_SELECTED_TRACK',
 'original_track_name':'睡前摇篮曲_原创配乐_33秒.wav',
 'voice_status':'NO_VOICE_ROBOTIC_DEMO_REMOVED',
 'legal_note':'Sampled instrument soundfont copyright/license copied as reference. Mixkit Close Your Eyes Now was not downloaded or used.',
 'score_structure':[b['name'] for b in bars],
 'checksums':{str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in [video_out,ROOT/'睡前摇篮曲_原创配乐_33秒.wav',ROOT/'睡前摇篮曲_音乐加音效_独立混音.wav']}
}
(ROOT/'制作与版权说明.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'video':str(video_out),'music_peak':pk,'mix_peak':float(np.max(np.abs(mix))), 'size':video_out.stat().st_size},ensure_ascii=False))
