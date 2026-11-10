#!/usr/bin/env python3
"""Mix an approved Mandarin story narrator onto the existing 33.3s lullaby video.
No TTS network and no AI generation; supply your own authorized, approved voice files.
"""
from pathlib import Path
import json, subprocess, argparse, math
P=Path(__file__).resolve().parent

def probe_duration(p):
    r=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(p)],capture_output=True,text=True,check=True)
    return float(r.stdout.strip())

def main():
    ap=argparse.ArgumentParser(description='Add 1 full-length recording or 8 per-page voice segments to the bedtime story movie.')
    ap.add_argument('--audio', help='Single natural voice recording in WAV, MP3 or M4A. Start reading at 0.25s; follow page timing, or provide an already-synced 33.3s audio file.')
    ap.add_argument('--pages', help='Directory with 8 voice files voice_page_00.wav (or mp3/m4a), etc. Each starts at page time in timeline JSON.')
    ap.add_argument('--output',default='乌鸦喝水_睡前旁白正式混音.mp4')
    args=ap.parse_args()
    if bool(args.audio)==bool(args.pages): ap.error('Pass exactly one of --audio or --pages')
    movie=P.parent/'reproduced'/'bedtime_rebuilt_1080p_no_voice.mp4'
    if not movie.is_file():ap.error('missing source video')
    timing=json.loads((P/'narration_timeline.json').read_text(encoding='utf-8'))
    (P.parent/'reproduced').mkdir(parents=True,exist_ok=True)
    args_list=['ffmpeg','-y','-hide_banner','-v','error','-i',str(movie)]
    voice_chains=[]
    if args.audio:
        f=Path(args.audio)
        if not f.is_file():ap.error(f'missing {f}')
        dur=probe_duration(f)
        if dur>34.2: ap.error('Narration longer than video. Please shorten/re-time recording; do not cut voice mid-sentence.')
        args_list+=['-i',str(f)]
        voice_chains=['[1:a]aformat=channel_layouts=stereo,aresample=48000,volume=1.0,apad,atrim=duration=33.3[voice]']
    else:
        dir=Path(args.pages)
        pages=[]
        for seg in timing['voice_segments']:
            k=seg['page']; options=[dir/f'voice_page_{k:02d}.{ext}' for ext in ('wav','m4a','mp3','aac')]
            matches=[f for f in options if f.is_file()]
            if not matches:ap.error(f'missing voice_page_{k:02d} .wav/.m4a/.mp3/.aac in {dir}')
            f=matches[0]; dur=probe_duration(f)
            if dur>seg['max_length']+.12:ap.error(f'{f.name} {dur:.2f}s exceeds slot {seg["max_length"]:.2f}s. Rewrite or naturally shorten, do not crop.')
            pages.append(f)
            args_list+=['-i',str(f)]
        for j,s in enumerate(timing['voice_segments'],1):
            delay=int(s['start']*1000)
            voice_chains.append(f'[{j}:a]aformat=channel_layouts=stereo,aresample=48000,adelay={delay}|{delay},apad,atrim=duration=33.3[v{j}]')
        joined=''.join(f'[v{i}]' for i in range(1,9))
        voice_chains.append(f'{joined}amix=inputs=8:duration=longest:normalize=0,atrim=duration=33.3[voice]')
    # The existing track includes music + sound effects. Reduce its level so the voice stays upfront.
    voice_chains+=['[0:a]aformat=channel_layouts=stereo,volume=0.40[bed]',
                   '[voice]highpass=f=90,lowpass=f=11000,volume=1.05,alimiter=limit=0.85[narr]',
                   '[bed][narr]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.93[mix]']
    args_list+=['-filter_complex',';'.join(voice_chains),'-map','0:v:0','-map','[mix]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-t','33.3','-movflags','+faststart',str(P.parent/'reproduced'/args.output)]
    subprocess.run(args_list,check=True)
    print('Created:',P.parent/'reproduced'/args.output)
    print('NOTICE: Artistically review voice, volume, sync and permission before publishing.')

if __name__=='__main__':main()
