#!/usr/bin/env python3
"""Separate objective media checks from director approvals for the pilot."""
from pathlib import Path
import json,subprocess,re,hashlib,sys
ROOT=Path(__file__).resolve().parent;VIDEO=ROOT/'output/crow-action-pilot.mp4'

def run(*args):return subprocess.run(args,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
probe=json.loads(run('ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(VIDEO)).stdout)
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
level=run('ffmpeg','-hide_banner','-i',str(VIDEO),'-vn','-af','volumedetect','-f','null','-').stderr
peak=re.search(r'max_volume: ([^ ]+) dB',level);mean=re.search(r'mean_volume: ([^ ]+) dB',level)
decode=run('ffmpeg','-v','error','-i',str(VIDEO),'-f','null','-')
objective={'resolution':[v['width'],v['height']],'avg_fps':v['avg_frame_rate'],'decoded_frames':int(v['nb_read_frames']),'duration_s':float(probe['format']['duration']),'audio_codec':a['codec_name'],'audio_duration_s':float(a['duration']),'audio_start_s':float(a['start_time']),'video_start_s':float(v['start_time']),'audio_peak_dbfs':float(peak.group(1)) if peak else None,'audio_mean_dbfs':float(mean.group(1)) if mean else None,'decode_errors':decode.stderr.strip()}
tech=(objective['resolution']==[1080,1920] and objective['avg_fps']=='6/1' and objective['decoded_frames']==24 and abs(objective['duration_s']-4)<.02 and objective['audio_codec']=='aac' and abs(objective['audio_duration_s']-4)<.04 and objective['audio_peak_dbfs']>-50 and not objective['decode_errors'])
# Director decisions require an actual reviewer and hash-bound evidence, never inferred from ffprobe.
reviews=json.loads((ROOT/'review/director-decisions.json').read_text())
results={'TECHNICAL_PASS':'PASS' if tech else 'FAIL'}
for key in ['VISUAL_PASS','ACTION_PASS','AUDIO_PASS','EDITORIAL_PASS']:
 d=reviews[key]; e=ROOT/d.get('evidence_file','__missing__')
 evidence_valid=e.is_file() and e.resolve().is_relative_to(ROOT.resolve()) and hashlib.sha256(e.read_bytes()).hexdigest()==d.get('evidence_sha256')
 valid=d.get('decision')=='PASS' and bool(d.get('reviewer')) and evidence_valid
 if key=='AUDIO_PASS':
  auditions=d.get('voice_auditions',[])
  voice_files=[ROOT/f for f in auditions]
  durations=[]
  for f in voice_files:
   if f.is_file():
    info=json.loads(run('ffprobe','-v','error','-show_format','-of','json',str(f)).stdout)
    durations.append(float(info['format']['duration']))
  rights=ROOT/d.get('audio_rights_file','__missing__')
  valid=valid and len(auditions)==2 and len(durations)==2 and all(8<=seconds<=10 for seconds in durations) and rights.is_file() and bool(d.get('music_foley_listening_notes'))
 if key=='EDITORIAL_PASS':
  rights=ROOT/d.get('rights_ledger','__missing__')
  valid=valid and (ROOT/d.get('cover_file','__missing__')).is_file() and rights.is_file() and bool(d.get('title')) and bool(d.get('note_copy'))
 results[key]='PASS' if valid else 'BLOCKED'
results['PUBLISH_READY']='PASS' if all(results[k]=='PASS' for k in ['TECHNICAL_PASS','VISUAL_PASS','ACTION_PASS','AUDIO_PASS','EDITORIAL_PASS']) else 'BLOCKED'
report={'status':results,'objective':objective,'sample_sha256':hashlib.sha256(VIDEO.read_bytes()).hexdigest(),'directors':reviews,'limitations':['No Chinese TTS voices were available; two natural 8–10 s auditions have not been made.','Music and Foley are original procedural stems; independent human listening has not occurred.','Visual and action director approval remain pending.','A pilot is not a completed publish package.']}
(ROOT/'review/acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
if not tech:sys.exit(1)
