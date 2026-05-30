# 萌辩岛语音输入/输出方案

## 结论

## 当前建议：云端大模型 + 本地语音服务

本项目的最佳起步方式是：大模型教练使用购买的云端 OpenAI-compatible API；Qwen3-ASR-0.6B 和 Kitten-TTS-Server 如果机器资源允许，再分别作为独立本地 HTTP 服务接入。这样主 FastAPI 后端只做业务编排、配置保存、音频上传和接口转发，不直接承载模型推理进程。


推荐第一阶段采用：

```text
浏览器录音 → FastAPI → Qwen3-ASR-0.6B → 辩论教练逻辑 → Kitten-TTS-Server → 前端播放
```

原因：

1. **输入识别优先中文准确率**：儿童辩论主要是普通话/中文场景，Qwen3-ASR-0.6B 是明确的 ASR 模型，适合先做中文语音识别。
2. **输出合成要轻量稳定**：Kitten-TTS-Server 是独立 TTS API 服务，模型体积小、可本地部署，便于后端用 HTTP 封装。
3. **Moonshine 更适合作为统一实时语音 Agent 备选**：Moonshine Voice 覆盖 STT、TTS、意图识别和实时语音 Agent；如果后续追求超低延迟实时打断、端侧部署、多语言统一栈，可以再整体评估引入。

## 方案对比

| 方案 | 类型 | 优点 | 风险/限制 | 本项目建议 |
| --- | --- | --- | --- | --- |
| Qwen3-ASR-0.6B | ASR 语音识别 | 中文/多语言 ASR 定位清晰；支持本地 Python 包和流式能力 | 本身不负责 TTS；流式能力通常需要更复杂运行时 | 作为首选语音输入 |
| Kitten-TTS-Server | TTS 语音合成 | 轻量、本地 API、适合 CPU/边缘设备；后端易集成 | 声音风格和中文自然度需要实测 | 作为首选语音输出 |
| Moonshine Voice | STT/TTS/语音 Agent 工具包 | 低延迟、端侧、多能力统一 | 对“只做 TTS 输出”来说可能偏重；中文儿童场景仍需实测 | 作为第二阶段实时语音 Agent 备选 |

## 后端接口设计

当前代码已预留：

- `POST /api/speech/transcribe`：上传浏览器录音文件，后续接 Qwen3-ASR-0.6B。
- `POST /api/speech/synthesize`：提交教练回复文本，后续请求 Kitten-TTS-Server 返回音频 URL 或二进制流。
- `GET /api/voice/plan`：让前端/管理页读取当前语音架构策略。

## 集成步骤

### 1. 语音识别：Qwen3-ASR-0.6B

后端新增 `SpeechRecognizer` 抽象：

```python
class SpeechRecognizer:
    def transcribe(self, audio_path: str, language: str = "Chinese") -> str:
        ...
```

实现时优先使用官方 `qwen-asr` Python 包。生产环境建议单独起一个 ASR worker，避免每次请求重复加载模型。

### 2. 语音合成：Kitten-TTS-Server

建议把 Kitten-TTS-Server 独立部署在内网，例如：

```text
http://127.0.0.1:8005
```

FastAPI 的 `/api/speech/synthesize` 负责：

1. 校验文本长度和儿童安全规则。
2. 请求 Kitten-TTS-Server。
3. 把音频文件 URL 或流返回给前端。

### 3. 前端播放

前端保留两层能力：

- MVP：点击“播放教练回复”后调用后端 TTS。
- 进阶：边收到教练文本边分句合成，实现更自然的等待体验。

## 儿童产品注意事项

- 默认不保存儿童原始音频；如需保存，必须有明确家长授权和删除机制。
- 对所有 ASR 文本进入教练模型前做敏感词和隐私信息过滤。
- TTS 音色应避免冒充真实老师/家长，使用明确的卡通教练音色。
- UI 上应提示“录音中/已停止/正在识别”，降低儿童误操作焦虑。

## 调研来源

- Moonshine Voice GitHub：低延迟、端侧语音 Agent 工具包，覆盖 STT/TTS/意图识别等能力。https://github.com/moonshine-ai/moonshine
- Qwen3-ASR-0.6B Hugging Face：官方模型卡提供 `qwen-asr` 安装、Transformers/vLLM 后端和流式推理说明。https://huggingface.co/Qwen/Qwen3-ASR-0.6B
- Kitten-TTS-Server GitHub：本地 TTS API/Web UI 服务，支持 CPU、CUDA、Docker 和 Raspberry Pi 5 场景。https://github.com/devnen/Kitten-TTS-Server
- animal-island-vue GitHub：Vue 3 动森风 UI 组件库；React 版 `animal-island-ui` 的 Vue 移植版本。https://github.com/guokaigdg/animal-island-vue
