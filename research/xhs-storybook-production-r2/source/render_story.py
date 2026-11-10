#!/usr/bin/env python3
"""Faithful single-camera (within each page) 8-page animation of user-accepted watercolor cards.
No added jar, no unlicensed music, no claimed TTS. Creates genuine localized motion and a GIF of moving stone.
"""
import os,math, json,random, subprocess,hashlib,wave,zipfile
from pathlib import Path
import numpy as np, cv2
from PIL import Image,ImageDraw,ImageFilter

ROOT=Path(__file__).resolve().parent
SRC=ROOT.parent/'artwork'
OUT=ROOT.parent/'reproduced';OUT.mkdir(exist_ok=True)
W,H=720,1280
FPS=12
DURS=[2.8,4.3,4.3,4.3,4.3,5.2,4.3,3.8]
TOTAL=sum(DURS)
START=[0.0]
for d in DURS[:-1]:START.append(START[-1]+d)
filenames=['00_封面.webp','01_故事第1页.webp','02_故事第2页.webp','03_故事第3页.webp','04_故事第4页.webp','05_故事第5页.webp','06_故事第6页.webp','07_故事启发.webp']
# Books contain a single jar already; it is never recreated. Crop only outside margins.
raw=[]
for i,f in enumerate(filenames):
 im=Image.open(SRC/f).convert('RGB')
 # Cover and moral pages are centered as originally designed
 bbox=(100,0,980,1440) if i in [0,7] else (120,0,960,1440)
 im=im.crop(bbox).resize((W,H),Image.Resampling.LANCZOS)
 raw.append(im)

# Inpaint only the printed lower-story sentences to reveal them with a soft brush wipe.
text_zones={1:(125,958,635,1130),2:(125,960,635,1133),3:(125,965,640,1140),4:(125,960,645,1135),5:(125,965,645,1145),6:(125,955,645,1140)}
clean=[]
for i,im in enumerate(raw):
 if i not in text_zones:
  clean.append(im)
  continue
 a=np.array(im)
 x0,y0,x1,y1=text_zones[i]
 region=a[y0:y1,x0:x1,:]
 # dark-green ink only; keep original parchment and unaltered title
 mask=(np.max(region,axis=2)<140).astype(np.uint8)*255
 # Green text has R/G low but preserved paper brown shadows; use stronger darkness threshold
 m2=(region[:,:,0]<153)&(region[:,:,1]<160)&(region[:,:,2]<137)
 mask=np.maximum(mask,(m2.astype(np.uint8)*255))
 mask=cv2.dilate(mask,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
 full=np.zeros(a.shape[:2],np.uint8);full[y0:y1,x0:x1]=mask
 b=cv2.inpaint(a,full,12,cv2.INPAINT_TELEA)
 clean.append(Image.fromarray(b))

# Page 5: move an actual pebble. Its static old pebble is erased only after release.
page=raw[5]; p=np.array(page)
# These coordinates are on resized accepted card, not arbitrary new jar shape.
stone_center=(487,427);stone_r=(27,25)
sm=np.zeros((H,W),dtype=np.uint8)
cv2.ellipse(sm,stone_center,(31,30),0,0,360,255,-1)
removed=Image.fromarray(cv2.inpaint(p,sm,9,cv2.INPAINT_TELEA))
# Sprite from the original painted pebble, alpha feathered into the existing scene.
x,y=stone_center
stone_img=page.crop((x-31,y-29,x+31,y+29)).convert('RGBA')
a=np.zeros((58,62),dtype=np.uint8)
cv2.ellipse(a,(31,29),(25,23),0,0,360,255,-1)
a=cv2.GaussianBlur(a,(5,5),1.1)
stone_img.putalpha(Image.fromarray(a))
# Prepare page5 versions for text-reveal: no-stone page and text removed
removed_no_text=removed.copy()
arr=np.array(removed_no_text)
x0,y0,x1,y1=text_zones[5]
region=arr[y0:y1,x0:x1]
mask=((region[:,:,0]<153)&(region[:,:,1]<160)&(region[:,:,2]<137)).astype(np.uint8)*255
mask=cv2.dilate(mask,np.ones((5,5),np.uint8));full=np.zeros((H,W),np.uint8);full[y0:y1,x0:x1]=mask
removed_no_text=Image.fromarray(cv2.inpaint(arr,full,12,cv2.INPAINT_TELEA))

# Palette and particle details deliberately watercolor-soft, not CGI.
LEAVES=[(0,87,.70,.75),(1,565,1.05,1.05),(2,360,.88,.6)]
COLS=[(177,153,77,155),(203,169,77,140),(153,164,99,120)]


def draw_accents(base, i, t):
    im=base.convert('RGBA')
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    # Tiny drifting leaves: one-time fall, no global camera movement.
    for k,(kid,x0,v,sv) in enumerate(LEAVES):
        tt=(t*sv+(i*.37+k*.6))%7.8
        xx=x0+23*math.sin(t*.8+k*2.1)
        yy=50+tt*88
        if yy>720:continue
        col=COLS[k]
        r=9+k*2
        d.ellipse((xx-r,yy-r/2,xx+r,yy+r/2), fill=col)
        d.line([(xx-7,yy+5),(xx+7,yy-4)],fill=(96,111,75,95),width=1)
    # Fixed-frame FX: restrained ripple exactly within EXISTING jar, no outline drawn.
    if i in (3,5,6):
        # Coordinates on accepted page; original glass stays untouched.
        rx=505 if i in (5,6) else 522
        ry=661 if i==5 else (671 if i==6 else 670)
        if i==5:strength=max(0,min(1,(t-2.8)*2.2))*max(0,min(1,(5.15-t)*2))
        else:strength=.34+.16*math.sin(2*math.pi*t*.8)
        for k in range(2):
            ph=(t*18+k*19)%42
            w=9+ph;h=3+ph*.11
            col=(233,249,243,int((72 if k==0 else 43)*strength*(1-ph/65)))
            d.arc((rx-w,ry-h,rx+w,ry+h),3,173,fill=col,width=2)
    if i==4:
        # Discovery sparkle stays near the existing loose stones, not on the jar.
        flash=(.4+.6*(1+math.sin(t*5))/2)
        for xx,yy in [(380,730),(410,716)]:
            c=(241,177,72,int(150*flash))
            d.line((xx-7,yy,xx+7,yy),fill=c,width=3)
            d.line((xx,yy-7,xx,yy+7),fill=c,width=3)
    if i==1:
        # Delicate thirsty drop already belongs to original drawing; add tiny motion drop.
        v=(t*.33)%1
        xx,yy=424+9*math.sin(t*3),400+45*v
        d.ellipse((xx-4,yy-7,xx+4,yy+7),fill=(91,167,201,int(115*(1-v))))
    if i==2:
        # Two hand-drawn run-marks; no fake moving camera.
        s=(1+math.sin(t*7))*.5
        c=(150,125,94,int(100*s))
        for a,b in [((161,658),(190,654)),((157,670),(180,666))]: d.line([a,b],fill=c,width=2)
    if i in (0,7,6):
        # A short happy glint, occasional and subtle.
        s=(1+math.cos(t*4))*.5
        c=(239,179,69,int(140*s))
        for cx,cy in ([(440,370)] if i!=7 else [(492,610)]):
            d.line((cx-8,cy,cx+8,cy),fill=c,width=3)
            d.line((cx,cy-8,cx,cy+8),fill=c,width=3)
    im=Image.alpha_composite(im,layer)
    return im

def compose_page(i, local_t):
    i=int(i);t=float(local_t)
    src=raw[i]
    base=clean[i].copy() if i in text_zones else src.copy()
    # Keep the already approved bird artwork intact; never inpaint its wing and create a smear.
    # Apply print-text as left-to-right calligraphy reveal without changing the written Chinese.
    if i in text_zones:
        x0,y0,x1,y1=text_zones[i]
        # Fade from y0 onwards as a narrow painting brush moves across the line.
        p=max(0.,min(1.,(t-.52)/2.6))
        if p>0:
            original=src
            alpha=Image.new('L',(W,H),0)
            if p>=1:ImageDraw.Draw(alpha).rectangle((x0,y0,x1,y1),fill=255)
            else:
                lim=int(x0+(x1-x0)*p)
                ImageDraw.Draw(alpha).rectangle((x0,y0,lim,y1),fill=255)
                # deliberate soft brush-tip (no text outside mask)
                for n in range(1,16):
                    if lim+n<x1:
                        ImageDraw.Draw(alpha).line([(lim+n,y0),(lim+n,y1)],fill=max(0,255-16*n),width=1)
            base.paste(original,(0,0),alpha)
    out=draw_accents(base,i,t)
    if i==5 and 1.45<=t<=3.17:
        # An additional pebble drops into the already existing jar while the bird holds the next one.
        # Existing bird/rock art is never erased, avoiding clone-smear and duplicate-container defects.
        u=(t-1.45)/(3.17-1.45)
        x=500 - 4*math.sin(math.pi*u)
        y=490 + 175*u*u
        item=stone_img.resize((34,31),Image.Resampling.LANCZOS)
        out.alpha_composite(item,(int(x-17),int(y-15)))
    return out.convert('RGB')

# Separate ambient + folies: no synthetic music and no synthetic narrator.
SR=48000
n=int(round(TOTAL*SR));rng=np.random.default_rng(20261110)
fx=np.zeros(n,dtype=np.float32)
# Quiet forest air as filtered pinkish noise; foley only.
a=rng.standard_normal(n).astype('float32')
b=np.zeros(n,dtype=np.float32)
# 2-stage recursive smoothing at audio rate (fast via scipy.signal)
from scipy.signal import lfilter
b=lfilter([.008],[1,-.992],a).astype('float32')
b/=max(np.std(b),1e-7)
fx+=.006*b*(.65+.25*np.sin(np.linspace(0,TOTAL*2.1,n)))

def noise_hit(st,dur,amp=.05,decay=17,pitch=0):
  start=int(st*SR);count=int(dur*SR)
  if start<0 or start>=n:return
  nn=min(count,n-start)
  z=rng.standard_normal(nn).astype(np.float32)
  z=lfilter([1,-.93],[1,-.55],z)
  t=np.arange(nn)/SR
  env=(1-np.exp(-t*250))*np.exp(-t*decay)
  fx[start:start+nn]+=amp*z[:nn]*env

def water_pop(st):
  start=int(st*SR);nn=int(.45*SR);nn=min(nn,n-start)
  t=np.arange(nn)/SR
  # damped acoustic bubble gliss, not musical accompaniment
  freq=430*np.exp(-t*15)+290
  phase=2*np.pi*np.cumsum(freq)/SR
  val=.035*np.sin(phase)*np.exp(-t*15)
  val+=.014*lfilter([1],[1,-.74],rng.standard_normal(nn).astype(np.float32))*np.exp(-t*23)
  fx[start:start+nn]+=val

for s in START[1:]:noise_hit(s,.33,.018,10)
for s in (START[2]+1.0,START[4]+.7):noise_hit(s,.24,.009,18)
water_pop(START[5]+3.15)
water_pop(START[6]+2.15)
# Normalized safely below -7 dBFS
fx=np.tanh(fx*1.1)
with wave.open(str(OUT/'FX_ONLY_no_voice_no_music.wav'),'wb') as o:
 o.setnchannels(1);o.setsampwidth(2);o.setframerate(SR)
 o.writeframes((np.clip(fx,-.7,.7)*32767).astype('<i2').tobytes())

# Render 720p native frames, encoded to full-height vertical 1080x1920 24fps. No global camera zoom.
video=OUT/'乌鸦喝水_完整绘本_动态预览_无旁白.mp4'
cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
 '-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-i',str(OUT/'FX_ONLY_no_voice_no_music.wav'),
 '-vf','scale=1080:1920:flags=lanczos,fps=24','-c:v','libx264','-preset','ultrafast','-crf','22','-pix_fmt','yuv420p',
 '-c:a','aac','-b:a','160k','-movflags','+faststart','-shortest',str(video)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
contact=[]
frames=int(round(TOTAL*FPS))
for k in range(frames):
 now=k/FPS
 i=max(j for j,s in enumerate(START) if s<=now)
 t=now-START[i]
 image=compose_page(i,t)
 # Real book-like page swap in last 0.25 seconds with a thin paper seam.
 if i<7 and t>DURS[i]-.28:
  v=(t-(DURS[i]-.28))/.28
  nextimg=compose_page(i+1,0)
  # Left side old page, right side next page as a vertical page wipe
  px=int(W*(1-v))
  a=image.copy()
  if px<W:a.paste(nextimg.crop((px,0,W,H)),(px,0))
  d=ImageDraw.Draw(a)
  if 0<=px<W:
   d.rectangle((max(0,px-10),0,min(W,px+9),H),fill=(239,224,193))
   d.line((px,0,px,H),fill=(159,125,85),width=2)
  image=a
 if k%max(1,int(FPS*4.2))==0: contact.append((now,image.copy()))
 try: proc.stdin.write(image.tobytes())
 except BrokenPipeError:break
proc.stdin.close();err=proc.stderr.read().decode('utf-8','ignore');ret=proc.wait()
if ret!=0:raise RuntimeError('ffmpeg FAILED: '+err[-1500:])

# GIF: actual moving stone in fixed single page, with the same page from user's approved images.
gifframes=[]
for j in range(24):
 t=1.2+j*(2.3/23)
 im=compose_page(5,t).resize((405,720),Image.Resampling.LANCZOS)
 gifframes.append(im)
gifpath=OUT/'乌鸦投石_真实动效_固定视角.gif'
gifframes[0].save(gifpath,save_all=True,append_images=gifframes[1:],duration=95,loop=0,optimize=False,disposal=2)

# Contact sheet snapshots
idx=[0,1,2,3,4,5,6,7]
thumb=Image.new('RGB',(4*240,2*340),(245,238,222))
for j in idx:
 snap=compose_page(j,min(DURS[j]-1,2.7)).resize((232,330),Image.Resampling.LANCZOS)
 thumb.paste(snap,((j%4)*240+4,(j//4)*340+5))
thumb.save(OUT/'8页动画关键帧预览.jpg',quality=88)

def shellcmd(cmd):return json.loads(subprocess.run(cmd,text=True,capture_output=True,check=True).stdout)
pr=shellcmd(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)])
codec=[{'codec_type':x['codec_type'],'codec_name':x['codec_name'],'width':x.get('width'),'height':x.get('height'),'avg_frame_rate':x.get('avg_frame_rate')} for x in pr['streams']]
status={'story':'乌鸦喝水','source_art':'8 user-approved Chinese watercolor storybook pages','source_page_sha256':{filenames[i]:hashlib.sha256((SRC/filenames[i]).read_bytes()).hexdigest() for i in range(8)},'video':video.name,'duration':TOTAL,'encoded_media':codec,'single_container_per_page':True,'fixed_camera_within_each_page':True,'animation_types':['falling watercolor leaves','ink-text reveal','an added separately animated pebble falling while another remains held in the artwork','water ripple on existing jar','paper-page wipes'],'articulated_crow_movement':'BLOCKED (no accepted intermediate pose assets); bird with held pebble is part of original artwork','speech':'BLOCKED (network unavailable and no natural Mandarin TTS installed)','formal_background_music':'BLOCKED (no approved recorded musical source)','foley':'soft forest ambient and page/pebble/water Foley; no music','publish_ready':'BLOCKED','description':'A real animated 8-scene storybook preview, not a voiceover-complete final publication.'}
(OUT/'验收及限制说明.json').write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf-8')
readme='''# 《乌鸦喝水》八页动画验证版

本实验严格使用用户先前认可的8张萌系水彩绘本图。每页内固定机位，保留原画中的水瓶，不重新绘制第二只水瓶。

真正的局部动效：纸页翻动、文字逐笔显现、飘落叶子、水面波纹、第五页独立一颗额外石子下落（原画里鸟还拿着下一颗）。附有真实循环GIF，不是单张PNG冒充GIF。

**尚未通过发布级验收**：原乌鸦未建立可信的连续角色动作；当前环境自然中文TTS请求不可用，未加入机械旁白；也未获得试听合格的免费授权背景乐，故只有环境及动作拟音。若要求完整有声直接发布，仍需解决旁白与音乐来源并完成听感审核。

视频是实际编码MP4，不是静态单帧；请优先观看第5页石子落水情节及单独GIF验证动态效果。

动画没有修改GitHub仓库main，素材引用详见验收JSON。
'''
(OUT/'制作说明.md').write_text(readme,encoding='utf-8')
zipfile_path=OUT/'乌鸦喝水_动态绘本实验工作包.zip'
with zipfile.ZipFile(zipfile_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=3) as z:
 for f in OUT.iterdir():
  if f.is_file() and f!=zipfile_path:
   z.write(f,arcname=f.name)
 z.write(__file__,arcname='build.py')
print(json.dumps({'video':str(video),'gif':str(gifpath),'package':str(zipfile_path),'video_bytes':video.stat().st_size,'gif_bytes':gifpath.stat().st_size,'duration_sec':TOTAL,'media':codec},ensure_ascii=False,indent=2))
