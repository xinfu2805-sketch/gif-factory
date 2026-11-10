#!/usr/bin/env python3
"""Fresh render from accepted eight images; use the previously approved audio WAV as sound bed.
Does not treat an existing MP4 as a render input. Prints technical evidence; no narrated finished film.
"""
from pathlib import Path
import subprocess, hashlib, json
ROOT=Path(__file__).resolve().parent.parent
GEN=ROOT/'reproduced'; GEN.mkdir(exist_ok=True)
subprocess.run(['python3',str(ROOT/'source'/'render_story.py')],check=True)
raw=GEN/'乌鸦喝水_完整绘本_动态预览_无旁白.mp4'
audio=ROOT/'audio'/'music_foley_mix_33s.flac'
out=GEN/'bedtime_rebuilt_1080p_no_voice.mp4'
subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(raw),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','33.3','-movflags','+faststart',str(out)],check=True)
p=subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=codec_name,codec_type,width,height,r_frame_rate','-of','json',str(out)],text=True)
obj=json.loads(p); streams=obj['streams']; v=next(s for s in streams if s['codec_type']=='video'); a=next(s for s in streams if s['codec_type']=='audio')
subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
result={'scope':'fresh render using eight approved illustrations + separately stored music/fx mix; not copied from the pre-existing mp4','output':str(out.relative_to(ROOT)),'duration_s':float(obj['format']['duration']),'dimensions':[v['width'],v['height']],'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'technical_pass':v['width']==1080 and v['height']==1920 and abs(float(obj['format']['duration'])-33.3)<.1,'VOICE_PASS':'BLOCKED','PUBLISH_READY':'BLOCKED'}
(ROOT/'review').mkdir(exist_ok=True)
(ROOT/'review'/'fresh_rebuild_result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
