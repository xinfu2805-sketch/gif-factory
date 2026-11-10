#!/usr/bin/env python3
"""True-6fps fixed-camera watercolor storybook compositor for R4."""
import argparse
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT=Path(__file__).resolve().parent.parent
W,H,FPS=1080,1920,6
EN_FONT='/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf'
ZH_FONT='/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
INK=(54,69,66)


def page_base(path):
    im=Image.open(path).convert('RGB')
    w,h=im.size
    crop_w=min(w,round(h*9/16))
    left=(w-crop_w)//2
    im=im.crop((left,0,left+crop_w,h)).resize((W,H),Image.Resampling.LANCZOS)
    return im.convert('RGBA')


def wrap(text,font,draw,max_width):
    parts=text.split(' ')
    lines=[];line=''
    for word in parts:
        trial=(line+' '+word).strip()
        if line and draw.textlength(trial,font=font)>max_width:
            lines.append(line);line=word
        else:line=trial
    if line:lines.append(line)
    return lines


def add_caption(im,page,opacity):
    if opacity<=0:return im
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    if page['page']==0:
        ef=ImageFont.truetype(EN_FONT,76);zf=ImageFont.truetype(ZH_FONT,53)
        for text,font,y in [(page['english'],ef,138),(page['chinese'],zf,245)]:
            width=d.textlength(text,font=font)
            d.text(((W-width)/2,y),text,font=font,fill=(255,248,225,255),stroke_width=2,stroke_fill=(78,75,105,210))
    else:
        en=page['english'];zh=page['chinese']
        size=58 if len(en)<56 else 52
        ef=ImageFont.truetype(EN_FONT,size)
        zf=ImageFont.truetype(ZH_FONT,44)
        enlines=wrap(en,ef,d,875)
        for j,text in enumerate(enlines):
            width=d.textlength(text,font=ef)
            d.text(((W-width)/2,1400+j*68),text,font=ef,fill=INK+(255,))
        zh_y=1400+len(enlines)*71+25
        # Chinese is intentionally smaller and always below the English.
        zhline='';zhlines=[]
        for char in zh:
            trial=zhline+char
            if zhline and d.textlength(trial,font=zf)>850:
                zhlines.append(zhline);zhline=char
            else:zhline=trial
        if zhline:zhlines.append(zhline)
        for j,text in enumerate(zhlines):
            width=d.textlength(text,font=zf)
            d.text(((W-width)/2,zh_y+j*53),text,font=zf,fill=(76,87,80,255))
    a=layer.getchannel('A').point(lambda v:int(v*opacity))
    layer.putalpha(a)
    return Image.alpha_composite(im,layer)


def accents(im,cloud,i,t,dur):
    # Draw only local layers. The original rabbit and hill never move or scale.
    w=Image.new('RGBA',(W,H));d=ImageDraw.Draw(w)
    # Small individual stars; page 03 introduces them in order.
    stars=[(155,265),(460,165),(850,310),(775,480),(280,500)]
    if i in (0,3,4,5,6,7):
        for k,(x,y) in enumerate(stars):
            if i==3:
                visibility=max(0,min(1,(t-(k*.48+.22))/.65))
            else:visibility=.55
            pulse=.72+.28*math.sin(t*1.65+k*1.7)
            a=int(visibility*pulse*118)
            if a<=0:continue
            d.ellipse((x-11,y-11,x+11,y+11),fill=(255,236,180,a//4))
            d.line((x-4,y,x+4,y),fill=(255,244,207,a),width=2)
            d.line((x,y-4,x,y+4),fill=(255,244,207,a),width=2)
    # Quiet grass motion, localized to the hill sides and below the paws.
    for k,(x,y) in enumerate(((108,1250),(180,1275),(905,1254),(955,1290))):
        sway=3.5*math.sin(t*1.35+k*.8)
        d.line([(x,y),(x+sway+5,y-21),(x+sway+10,y-36)],fill=(114,132,91,58),width=3)
        d.ellipse((x+sway+7,y-39,x+sway+15,y-31),fill=(133,146,98,39))
    if i in (0,6,7):
        # Moon halo rises gradually for the reveal page, stays restrained elsewhere.
        glow=max(0,min(1,(t-.3)/(dur-.9))) if i==6 else .32
        cx,cy=(850,260) if i==6 else ((760,510) if i==0 else (820,220))
        for radius,alpha in ((150,8),(115,12),(80,17)):
            d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),fill=(255,237,188,int(alpha*glow)))
    im=Image.alpha_composite(im,w)
    # One separately generated watercolor cloud moves a few dozen pixels.
    if i!=7:
        cw,ch=(450,150) if i!=6 else (590,215)
        sprite=cloud.resize((cw,ch),Image.Resampling.LANCZOS)
        x={0:540,1:90,2:230,3:115,4:520,5:400,6:550}[i]+int(t*(8 if i!=6 else 100))
        y={0:380,1:240,2:270,3:220,4:200,5:260,6:100}[i]
        if i==6:
            strength=max(.35,1-.65*t/dur)
        else:strength=.36 if i in (1,2,3,5) else .53
        a=sprite.getchannel('A').point(lambda v:int(v*strength))
        sprite.putalpha(a)
        overlay=Image.new('RGBA',(W,H));overlay.alpha_composite(sprite,(x,y))
        im=Image.alpha_composite(im,overlay)
    return im


def page_frame(bases,cloud,page,local_frame,with_text=True):
    i=page['page'];dur=page['page_frames']/FPS;t=local_frame/FPS
    im=accents(bases[i].copy(),cloud,i,t,dur)
    fade_in=min(1,t/.5)
    fade_out=min(1,max(0,(dur-t)/.5))
    return add_caption(im,page,min(fade_in,fade_out) if with_text else 0).convert('RGB')


def frames_for_full(bases,cloud,timeline):
    pages=timeline['pages']
    for i,page in enumerate(pages):
        for k in range(page['page_frames']):
            yield page_frame(bases,cloud,page,k)
        if i<7:
            old=page_frame(bases,cloud,page,page['page_frames']-1,False)
            new=page_frame(bases,cloud,pages[i+1],0,False)
            for k in range(timeline['transition_frames']):
                seam=int(W*(1-(k+1)/(timeline['transition_frames']+1)))
                frame=old.copy()
                frame.paste(new.crop((seam,0,W,H)),(seam,0))
                d=ImageDraw.Draw(frame)
                d.rectangle((seam-8,0,seam+8,H),fill=(235,219,199))
                d.line((seam,0,seam,H),fill=(143,122,139),width=2)
                yield frame


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--pilot-page',type=int,choices=range(8))
    a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True)
    timeline=json.loads((ROOT/'timeline.json').read_text())
    bases=[page_base(ROOT/f'artwork/page_{i:02d}.png') for i in range(8)]
    cloud=Image.open(ROOT/'artwork/cloud_layer.png').convert('RGBA')
    if a.pilot_page is None:
        frames=frames_for_full(bases,cloud,timeline)
        expected=timeline['total_frames']
    else:
        page=timeline['pages'][a.pilot_page]
        frames=(page_frame(bases,cloud,page,k) for k in range(page['page_frames']))
        expected=page['page_frames']
    cmd=['ffmpeg','-hide_banner','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24',
        '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast',
        '-crf','18','-pix_fmt','yuv420p',str(a.output)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    count=0
    for im in frames:
        proc.stdin.write(im.tobytes());count+=1
    proc.stdin.close()
    err=proc.stderr.read().decode('utf8','replace')
    if proc.wait() or count!=expected:raise RuntimeError(f'Render failed: {count}/{expected} frames {err[-1000:]}')
    (a.output.parent/(a.output.stem+'_render.json')).write_text(json.dumps(dict(
        frames=count,fps=FPS,width=W,height=H,pilot_page=a.pilot_page),indent=2)+'\n')
    print(f'{a.output}: {count} distinct timeline frames at {FPS} fps')


if __name__=='__main__':main()
