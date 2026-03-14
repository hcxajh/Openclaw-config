---
name: comfyui
description: ComfyUI AI 图像生成工具。支持文生图、图生图。用于：(1) 文生图 - 输入提示词生成图片；(2) 图生图 - 上传图片+提示词进行变换。默认连接 http://10.1.1.90:8188/，默认模型 flux1-dev.safetensors，默认尺寸 1024x1024
---

# ComfyUI 技能

与本地 ComfyUI 服务交互，生成 AI 图像。

## ⚠️ 重要：路径逻辑

脚本使用 `os.getcwd()` 获取当前工作目录，因此：

- **每个代理生成图片会保存到各自的工作空间**
- 如果你在 `~/.openclaw/workspace-daily` 运行 → 图片保存到 `~/.openclaw/workspace-daily/comfyui/`
- 如果你在 `~/.openclaw/workspace-code` 运行 → 图片保存到 `~/.openclaw/workspace-code/comfyui/`
- 依此类推

**注意**：是当前工作空间，不是技能所在目录！

## 快速开始

### 确认连接

首次使用，确认 ComfyUI 服务是否可达：

```bash
curl http://10.1.1.90:8188/system_stats
```

### 基本流程

1. **文生图** - 输入提示词，生成图片
2. **图生图** - 上传参考图 + 提示词，生成变换后的图片

## 功能详解

### 1. 文生图 (Text to Image)

用户提供：
- **正面提示词** (required): 描述想要的内容

可选参数：
- **尺寸**: 默认 1024x1024
- **步数**: 默认 20
- **CFG**: 默认 1
- **模型**: 默认 flux1-dev.safetensors

执行脚本：`scripts/txt2img.py`

### 2. 图生图 (Image to Image)

用户提供：
- **参考图片** (required): 上传图片路径
- **正面提示词** (required): 描述想要的内容

可选参数：
- **重绘幅度**: 默认 0.7
- **尺寸**: 默认 1024x1024

执行脚本：`scripts/img2img.py`

## 脚本使用

### txt2img.py

```bash
python ~/.openclaw/skills/comfyui/scripts/txt2img.py \
  --prompt "a beautiful sunset over ocean" \
  --width 1024 \
  --height 1024 \
  --steps 20 \
  --model flux1-dev.safetensors
```

**默认参数**:
- 尺寸: 1024x1024
- 步数: 20
- CFG: 1
- 模型: flux1-dev.safetensors

**输出路径**: `{当前工作空间}/comfyui/{日期}/IMG001.png`

**文件名规则**: IMG001, IMG002, IMG003... 自动递增

### img2img.py

```bash
python ~/.openclaw/skills/comfyui/scripts/img2img.py \
  --input ./input.png \
  --prompt "anime style" \
  --strength 0.7
```

**输出路径**: `{当前工作空间}/comfyui/{日期}/IMG002.png`

## ⚠️ 发送图片给用户

**重要**：生成图片后，必须用 `path` 参数发送图片给用户！

```python
message(
    action="send",
    channel="feishu",
    message="图片描述",
    path="图片完整路径",
    target="user:xxx"
)
```

## 可用模型

| 模型 | 说明 |
|------|------|
| flux1-dev.safetensors | Flux 开发版 (默认) |
| flux1-schnell-fp8.safetensors | Flux 快速版 |
| flux1-dev-fp8.safetensors | Flux 开发版 FP8 |
| majicmixRealistic_v7.safetensors | 写实风格 |
| anything-v5-PrtRE.safetensors | 动漫风格 |

## 性能

- **首次生成**: 需要加载模型，约 30-40 秒
- **后续生成**: 模型已加载，约 10-15 秒
- 脚本会显示实际生成耗时

## 注意事项

1. 首次生成需要加载模型，等待时间较长
2. 生成完成后图片保存在工作空间的 comfyui 目录
3. 可以通过 API 查看队列状态：`GET /queue`

## ⚠️ 封面生成规则（强制）

1. **ComfyUI 优先**：生成封面必须使用 ComfyUI
2. **连不上则跳过**：如果 ComfyUI 服务不可达（连接超时/拒绝），直接跳过封面生成，不要尝试其他方案
3. **禁止 Minimax**：严禁使用 Minimax 生成封面，必须使用 ComfyUI
4. **无封面可继续**：如果无法生成封面，继续发布故事（正文必须有封面，封面可以暂时没有）
