# 《乌鸦喝水》发布级整改研究样片

运行 `python3 render_pilot.py` 生成 1080×1920、真实 6fps、4 秒动作样片、三条独立音轨和 24 张源帧。运行 `python3 publish_gate.py` 检查媒体规格并读取 `review/director-decisions.json`。保留 `output/crow-action-pilot.mp4`、`output/music-original.wav`、`output/foley-original.wav`、`output/mix-no-voice.wav` 与 `output/contact-sheet.jpg` 作为实际媒体证据。

素材沿用上轮《乌鸦喝水》的水彩背景与乌鸦姿态，字体 Ma Shan Zheng 按随附 OFL 使用；音乐、音效由 `render_pilot.py` 在本轮原创合成，没有外部音频样本。该音乐权利来源可追溯，但声音导演试听尚未完成。当前环境没有中文 TTS，故无旁白，不能发布。

本样片保留了三张独立乌鸦姿态（低头接触、半抬头、举头），嘴尖锚点跟随单颗石子；石子进入罐口、下沉后水位才升高。仍需动作导演审看正常速度下的姿态衔接。本轮未扩展剩余五页。

质量状态见 `review/acceptance.json`。任务约束、旧版根因和 S0–S9 契约见 `OBSERVE_AND_DESIGN.md`。
