#!/usr/bin/env python3
"""Freeze the eight-page, true-6fps timeline after measuring narration."""
import hashlib
import json
from pathlib import Path

from generate_voice import LINES

ROOT=Path(__file__).resolve().parent.parent
FPS=6
PAGE_FRAMES=[16,23,19,23,23,22,25,28]
TURN_FRAMES=3
MOTIONS=[
    "cover: quiet moon glow and one drifting cloud",
    "early dusk: faint grass sway",
    "waiting: slow cloud drift",
    "stars: several individual glints brighten in sequence",
    "hidden moon: cloud drifts over the pale glow",
    "patient pause: sparse stars and grass sway",
    "moon reveal: cloud layer shifts off the moon; glow rises",
    "sleep: a steady sleeping pose, faint breath-sized grass motion",
]


def main():
    generation=json.loads((ROOT/'voice/generation.json').read_text())
    assert len(generation)==len(PAGE_FRAMES)==8
    cursor=0
    pages=[]
    for i,(frames,(en,zh),g) in enumerate(zip(PAGE_FRAMES,LINES,generation)):
        assert g['english']==en and g['chinese']==zh
        start=cursor/FPS
        duration=frames/FPS
        voice_start=start+.25
        voice_end=voice_start+g['duration_s']
        if voice_end>start+duration-.28:
            raise RuntimeError(f"Page {i} voice overflows natural hold: {voice_end:.3f}")
        pages.append(dict(page=i,start_frame=cursor,page_frames=frames,
            start_s=round(start,3),duration_s=round(duration,3),
            end_s=round(start+duration,3),
            voice_start_s=round(voice_start,3),voice_end_s=round(voice_end,3),
            english=en,chinese=zh,voice_file=g['filename'],
            voice_sha256=g['sha256'],motion=MOTIONS[i],
            artwork=f"artwork/page_{i:02d}.png",
            artwork_sha256=hashlib.sha256((ROOT/f'artwork/page_{i:02d}.png').read_bytes()).hexdigest()))
        cursor+=frames
        if i<7:
            cursor+=TURN_FRAMES
    assert cursor==200,cursor
    result=dict(fps=FPS,total_frames=cursor,total_duration_s=round(cursor/FPS,3),
        transition_frames=TURN_FRAMES,transition_duration_s=TURN_FRAMES/FPS,pages=pages)
    (ROOT/'timeline.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
