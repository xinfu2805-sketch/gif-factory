# XHS-STORYBOOK-PRODUCTION-R2：33.3 秒源工程复现

2026-11-10，在 `/tmp/xhs-r2-clean-yfdF4B80` 新建的空目录中解压用户上传的 `XHS_R2_HQ_Codex_SourcePack.zip`。ZIP SHA-256：`322fe120b367eabd15e630c640509d5dc01fd62923300231fa2cd18d715060c8`；`unzip -t` 和包内 18 项 `sha256sum -c MANIFEST_SHA256.txt` 均通过。ZIP **不含预制 MP4**。交接文件实际名为 `README_FOR_CODEX.md`（上传包没有 `README_交接给Codex.md`），已阅读。

在该目录新建 Python 虚拟环境，使用 Python 3.12、NumPy 2.5.4、Pillow 13.0.0、OpenCV 5.0.0、SciPy 1.18.1，从包根目录运行 `python3 source/rebuild_from_artwork.py`。脚本读取 8 张 WebP 原画和独立的 `music_foley_mix_33s.flac`，没有把已有 MP4 作为输入。`run_rebuild.sh` 将哈希核对、原入口、解码检查与 ffprobe 连成一个便携入口；项目所需依赖仍须由运行环境提供。

## 实测媒体

- 新输出：`reproduced/bedtime_rebuilt_1080p_no_voice.mp4`，SHA-256 `7e126011d097b39c69e0f272b0332d4ed83d776c0d598bb0c28b8b32147e60e8`。
- 33.300000 秒容器；视频 1080×1920、H.264、24 fps、实解 799 帧（视频流 33.291667 秒）；音频 AAC、48 kHz、双声道、33.300000 秒。FFmpeg 全片解码无错误；AAC 音轨均值 −23.1 dBFS，峰值 −7.7 dBFS，非静音。
- 原画为 1080×1440 WebP；脚本先在 720×1280、12 fps 合成，再放大到 1080×1920、24 fps 编码。24 fps **不是 24 张独立动作原画**，输出像素尺寸也不等于原生 1080p 绘制细节。
- 用户给出的 `392e09b9e4c82d9cda291adc1f469bffdad82f7e14cf46d93aa1f23e8d14d8a0` 是原母版 SHA。此便携包将 PNG 转为 WebP，交接说明明确预期新输出不会字节一致；本次新 SHA 与它不同，因此**原母版字节一致性不通过**，但便携源码重建的技术检查通过。

解码抽帧证据：`decoded-eight-pages.jpg`（每页中段）、`decoded-page-ends.jpg`（每页末段）、`decoded-stone-action.jpg`（第 5 故事页石子运动）。它们从新 MP4 解码产生，并非输入源图片。观察到 8 页统一水彩角色、每页固定机位、每页一只原画水瓶；第 5 故事页有独立下落石子，原画中乌鸦仍持另一颗石子。翻页存在，末段文字可读。乌鸦的连续关节姿态、喙石接触与罐口物理关系**没有通过**；源码自身也将 articulated crow movement 标成 BLOCKED。

## 声音与版权

源包保留独立的 `lullaby_original_33s.opus`（实测均值 −28.9 dBFS）和 `foley_original_33s.opus`（−46.1 dBFS），以及供重建使用的 FLAC 混音。音乐来自原项目的 TimGM6mb 采样音色库，随包附 GPL-2 说明；小红书分发与其他权利链尚未得到审查。当前工具不能实际听取音频，因此听感审核未执行。中文旁白时间轴与合并脚本已保留，但无自然中文女声、无两段试听；不使用 eSpeak 冒充。

`source/optional_music_from_soundfont.py` 是原包留存的**历史可选脚本**，包含 `/mnt/data` 绝对路径，且需要未随包提供的 TimGM6mb.sf2；它不在便携复现入口中。正式复现使用包内 FLAC 和独立音轨，不运行该脚本。

## 签发边界

| 项目 | 结果 |
| --- | --- |
| 源包完整性与新视频技术复现 | PASS |
| TECHNICAL_PASS（33.3 秒无旁白研究预览） | PASS |
| VISUAL_PASS（发布审美） | BLOCKED：用户本轮未审新输出，抽帧不等于发布认可 |
| ACTION_PASS | BLOCKED：连续乌鸦动作与接触关系不足 |
| AUDIO_PASS | BLOCKED：缺自然女声、主观试听及配乐平台权利复核 |
| EDITORIAL_PASS | BLOCKED：无完整旁白成片及发布文案验收 |
| PUBLISH_READY | BLOCKED |

这次迁移证明：8 张可追溯原画 + 独立音轨 + 固定视角页内效果 + 翻页 + 字幕显现，可以从空目录重建 33.3 秒研究预览。它尚不能证明“只输入任意故事即自动生产发布级视频”，因为角色原画生成、真实关节动作、自然女声和版权/试听仍有制作与审核缺口。未修改仓库 `main`、冻结 GIF 算法，也未合并任何 PR。
