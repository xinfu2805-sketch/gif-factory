# XHS-STORYBOOK-R3E-B｜独立验收记录

日期：2026-11-10 UTC。权威仓库 `xinfu2805-sketch/gif-factory`；实时远端
`main=a4e2d6d853c91e9ec25d77c7819b3f09e0a11385`，R2
`research/xhs-storybook-production-r2=9f8d215e145cda5b91d73950b3b8c02c90f959ad`。
Draft PR #3 仍 open/draft/未合并。本轮仅使用新的
`research/xhs-storybook-english-r3e` 研究分支；未修改 main、R2 原画或冻结的
GIF Factory 核心算法。

## 复现路径

在新建的 `/tmp/xhs-r3e-clean.3YtxRf` 中复制经 R2 验证的无旁白画面、八张
WebP、水彩页、独立音乐与音效、官方 Kokoro 权重和本分支源码；新建 Python
3.12 venv，安装锁定的四项 Python 依赖。在该目录执行 `build.sh`，先生成
八段原速 `af_sol` 英语旁白，再从 R2 画面输入逐帧替换双语字幕，分轨混音并
编码新 MP4。最终转场修复在同一干净环境从输入画面重新渲染全部 799 帧，
没有把之前的 R3E MP4 当作输入。轻量工作包另提供 `build_from_voice.sh`：
从已附的八段可核查 WAV 重建画面与混音，无需打包 365 MB 模型权重。

**最终 MP4 SHA-256**：
`b8ae2445e5ca8df8649b593768a4774403fa8895a628cdfa7869eb076168ca27`
（与输入 R2 MP4 SHA `7e126011d097b39c69e0f272b0332d4ed83d776c0d598bb0c28b8b32147e60e8`
不同）。

## 实测

- `ffprobe`：33.300000 秒；1080×1920；H.264；编码 24 fps、799 帧；
  AAC 48 kHz 双声道。R2 原画动画是在 12 fps 合成后复制到 24 fps，**不是
  799 张独立角色动作原画**。
- FFmpeg 全片视频、音频解码无错误；最终 AAC 解码 RMS `0.047566`，非静音。
  八段 WAV 均非空、未越过页尾；原速语音长度依次为 1.084、2.432、
  1.369、1.830、2.063、1.906、1.811、2.833 秒。
- 独立 48 kHz 音轨 RMS：旁白 `0.042569`、动态压低后的音乐 `0.021302`、
  音效 `0.002581`、最终混音 `0.047653`。音乐在人声时目标增益 0.30，
  语句间目标增益 0.82，采用 0.11 秒入、0.68 秒回的平滑控制。
- 从最终 MP4 解码八页中段与七组翻页前后帧。英文大字、中文小字落在
  清理后的独立纸纹区域，未覆盖角色、石子、水罐重要动作。翻页前字幕淡出，
  翻页时文字区保持空白，下一页淡入；抽帧未见之前的碎字叠压。
- 对应的八帧插画上半区与 R2 画面的平均绝对像素差为 1.387–1.577/255，
  与 H.264 再编码一致；未发现角色或机位被重画。
- 两段 R3E-A 试听 WAV 均保留。用户选用 `af_sol` 的 B 版本音色；
  本轮八段新句子及完整混音未获得人耳逐句确认。

机器细节见 `technical_report.json`、`illustration_preservation.json`、
`eight_decoded_pages.jpg`、`seven_page_turns.jpg`、八段 `timeline.json` 和
工作包 `SHA256SUMS`。

## 分项签发

| 项目 | 结论 | 边界 |
| --- | --- | --- |
| TECHNICAL_PASS | **PASS** | 完整视频、AAC、字幕时间轴、分轨和全片解码实测通过 |
| VISUAL_PASS | **BLOCKED** | 抽帧检查通过技术避让；用户尚未认可整片美术与阅读体验 |
| ACTION_PASS | **BLOCKED** | R2 乌鸦连续关节动作、喙石罐口接触仍不足；换语言未修复 |
| ENGLISH_VOICE_PASS | **BLOCKED** | B 音色样本已被选中；八段新文案尚无人耳逐句验发音与情绪 |
| AUDIO_PASS | **BLOCKED** | 音轨非静音、动态混音技术通过；完整配音、音乐、音效未做独立人耳试听 |
| EDITORIAL_PASS | **BLOCKED** | 八页字幕与草稿文案齐备，尚无最终编辑确认 |
| COPYRIGHT_PASS | **BLOCKED** | Kokoro 官方包附 Apache-2.0；TimGM6mb 音色库 GPL-2 文本保留，但小红书分发适用性与原画权利链未完成核查 |
| PUBLISH_READY | **BLOCKED** | 上述关键审核未闭合 |

当前成果是《乌鸦喝水》**可播放的双语研究成片**，不能据此声称任意故事
已经能自动达到发布级品质。发布前须逐句试听英文旁白及最终混音、审查角色
真实动作，并闭合音源与原画的使用权。
