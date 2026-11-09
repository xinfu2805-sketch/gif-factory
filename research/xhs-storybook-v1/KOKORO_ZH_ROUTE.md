# XHS-STORYBOOK-R1.1：免费中文 TTS 路线核查

## 已核实的上游资料

- 官方推理库：[hexgrad/kokoro](https://github.com/hexgrad/kokoro)，其 `LICENSE` 为 Apache-2.0；`README.md` 称 Kokoro 权重为 Apache 授权，并给出 `pip install kokoro>=0.9.4 soundfile`。
- 官方库 `pyproject.toml` 版本 0.9.4，Python 要求 `>=3.10,<3.14`；依赖 `huggingface_hub`、`loguru`、`misaki[en]>=0.9.4`、`numpy`、`torch`、`transformers`。中文还需 `misaki[zh]`。`KPipeline(lang_code='z')` 对应普通话。
- 官方库 `kokoro/model.py` 将 `hexgrad/Kokoro-82M-v1.1-zh` 映射到 `kokoro-v1_1-zh.pth`，并从同仓库读取 `config.json`；`kokoro/pipeline.py` 从 `voices/<voice>.pt` 读取音色，也支持传入本地 `.pt` 路径。
- 正规模型仓库地址：<https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh>。本任务从当前云环境访问该**确切地址**得到 HTTP CONNECT 403。模型卡、中文音色各自的许可与模型文件校验值因而**未能实测核实**。推理库的 Apache-2.0 不能自动代替特定模型快照和音色文件的权利核验。

上述代码、依赖和仓库映射来自上游 `main` 的 2026-11-09 只读查询；实际引入时应锁定提交或发布版本并重新检查许可。

## 当前资源和结论

当前执行环境 Python 3.12；cgroup 内存上限 8 GiB、CPU 配额约 2 核；`torch`、`kokoro`、`misaki`、`huggingface_hub`、`transformers` 未安装。82M 个 FP32 参数理论权重约 328 MB，实际运行还需要框架、G2P、声码器与中间张量，不能仅凭此估算签发资源 PASS。没有模型文件，未进行推理速度、自然度、发音或许可测试。两段 8–10 秒中文试听：**BLOCKED**。

## 正式可用的两条途径

1. **由环境所有者在正式 Codex Cloud 环境设置中授权模型域名和实际下载重定向域名。**生效后用当前任务的新请求验证模型卡、权重、音色及许可，并在项目局部虚拟环境装依赖。此次没有调用或重试云端配置接口，没有使用自建代理。
2. **离线导入经授权的上游快照。**提供官方仓库导出的 `config.json`、`kokoro-v1_1-zh.pth`、两份 `voices/*.pt`、模型卡/许可文本及逐文件 SHA-256。先核实模型与音色的使用范围，再以 `KModel(repo_id='hexgrad/Kokoro-82M-v1.1-zh', config=本地配置, model=本地权重)` 和 `KPipeline(lang_code='z', repo_id=同仓库, model=上述模型, device='cpu')` 加载；音色参数传入本地 `.pt` 路径，避免隐式下载。依赖在本项目局部虚拟环境安装，不重新部署整套环境。

两条途径都须生成**两段不同音色、各 8–10 秒**的中文试听，并分别检查发音、停顿、情绪、爆音和音色许可。声音导演实际试听后才能进入正式旁白；文件存在与音轨非静音都不足以签发 `AUDIO_PASS`。
