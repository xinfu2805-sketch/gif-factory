# 《乌鸦喝水》发布级整改研究样片

运行 `python3 render_pilot.py` 生成 1080×1920、真实 6fps、4 秒动作样片、三条独立音轨和 24 张源帧。运行 `python3 publish_gate.py` 检查媒体规格并读取 `review/director-decisions.json`。保留 `output/crow-action-pilot.mp4`、`output/music-pipeline-test.wav`、`output/foley-original.wav`、`output/mix-no-voice.wav` 与 `output/contact-sheet.jpg` 作为实际媒体证据。

素材沿用上轮《乌鸦喝水》的水彩背景与乌鸦姿态，字体 Ma Shan Zheng 按随附 OFL 使用；音效由 `render_pilot.py` 在本轮合成，没有外部音频样本。正弦波音乐只用于验证分轨与混音管线，不能作为正式配乐或签发音乐品质 PASS。正式配乐需有合法来源与独立人工试听。当前环境没有中文 TTS，故无旁白，不能发布。

本样片保留了三张独立乌鸦姿态（低头接触、半抬头、举头），嘴尖锚点跟随单颗石子；石子进入罐口、下沉后水位才升高。仍需动作导演审看正常速度下的姿态衔接。本轮未扩展剩余五页。

质量状态见 `review/acceptance.json`。任务约束、旧版根因和 S0–S9 契约见 `OBSERVE_AND_DESIGN.md`。

R1.1：`python3 publish_gate.py --scope pilot` 和 `python3 publish_gate.py --scope full` 分别输出 `review/acceptance-pilot.json` 与 `review/acceptance-full.json`。`stone_state.py` 与 `review/stone-audit.json` 逐帧记录单石状态及坐标；当前两处抬头跳变令 `ACTION_PASS` 保持 BLOCKED。`music-pipeline-test.wav` 只用于验证管线，正式音乐未制作。Kokoro 许可/资源/正规导入路径见 `KOKORO_ZH_ROUTE.md`；两段自然中文试听仍未生成。

后续导演签发时，按 `review/director-decisions.json` 填写审阅者、审阅时间、与当前媒体相同的 SHA-256、具体观察和独立证据文件及哈希；声音还要分别附两段 8–10 秒试听、旁白/正式音乐/音效的权利与逐轨试听证据、总混音试听证据。完整视频另需将 `review/full-spec.example.json` 填为 `review/full-spec.json`，并附混音来源清单。填写字段本身不能替代实际看片和听音。
