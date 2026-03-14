---
name: minimax-image
description: 使用 MiniMax API 进行图像生成。支持文生图 (T2I) 和图生图 (I2I) 两种模式。可选模型：image-01 (基础版) 和 image-01-live (支持画风转换)。支持画风：漫画、元气、中世纪、水彩。适用场景：AI 艺术创作、人物换装、风格迁移等。
metadata:
  {
    "openclaw":
      {
        "emoji": "🎨",
        "requires": { "bins": ["python3"], "python_packages": ["requests"] },
        "install": [
          {
            "id": "minimax-deps",
            "kind": "pip",
            "packages": ["requests"],
            "label": "安装 MiniMax 图像生成依赖 (pip)",
          },
          {
            "id": "minimax-api-key",
            "kind": "file",
            "path": "config/api_key.txt",
            "label": "创建 API Key 配置文件",
            "content": "sk-api-xxxxx  # 在此替换为您的 API Key"
          }
        ]
      }
  }
---

# MiniMax 图像生成技能

使用 MiniMax 强大的图像生成 API 进行文生图和图生图。

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API Key

有两种方式配置 API Key：

**方式 A：环境变量（推荐）**
```bash
export MINIMAX_API_KEY="sk-api-xxxxx"
```

**方式 B：配置文件**
```bash
echo "sk-api-xxxxx" > config/api_key.txt
```

### 3. 基本用法

**文生图：**
```bash
python scripts/t2i.py --prompt "一个穿汉服的女孩在樱花树下" --output ./images/
```

**图生图：**
```bash
python scripts/i2i.py --reference https://example.com/photo.jpg --prompt "穿西装" --output ./results/
```

---

## 功能说明

### 🎨 文生图 (Text to Image)

根据文本描述生成图像。

```bash
python scripts/t2i.py --prompt "描述文本" [选项]
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--prompt, -p` | **必填** 图像描述文本 | - |
| `--model, -m` | 模型: `image-01` 或 `image-01-live` | image-01-live |
| `--style, -s` | 画风: `漫画`/`元气`/`中世纪`/`水彩` | - |
| `--style-weight` | 画风权重 0-1 | 0.8 |
| `--aspect, -a` | 宽高比 (默认: **9:16** 竖版手机) | 9:16 |
| `--n, -n` | 生成数量 1-9 | 1 |
| `--seed` | 随机种子（复现结果）| 随机 |
| `--output, -o` | 输出目录 | ./outputs/ |
| `--prompt-optimizer` | 自动优化提示词 | 关闭 |
| `--watermark` | 添加 AI 水印 | 关闭 |

### 🖼️ 图生图 (Image to Image)

根据参考图像和文本描述生成新图像，保持人物特征。

```bash
python scripts/i2i.py --reference <图片> --prompt "描述文本" [选项]
```

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--reference, -r` | **必填** 参考图片 URL 或本地路径 | - |
| `--prompt, -p` | **必填** 图像描述文本 | - |
| `--model, -m` | 模型 | image-01-live |
| `--style, -s` | 画风 | - |
| `--aspect, -a` | 宽高比 | 1:1 |
| `--n, -n` | 生成数量 | 1 |
| `--output, -o` | 输出目录 | ./outputs/ |

---

## 支持的参数

### 模型

| 模型 | 说明 | 画风支持 |
|------|------|---------|
| `image-01` | 基础版 | ❌ |
| `image-01-live` | 进阶版 | ✅ |

### 宽高比

| 比例 | 尺寸 | 备注 |
|------|------|------|
| 1:1 | 1024×1024 | |
| 16:9 | 1280×720 | |
| 4:3 | 1152×864 | |
| 3:2 | 1248×832 | |
| 2:3 | 832×1248 | 竖版 |
| 3:4 | 864×1152 | 竖版 |
| 9:16 | 720×1280 | 竖版手机 |
| 21:9 | 1344×576 | 超宽，仅 image-01 |

### 画风类型 (仅 image-01-live)

- `漫画` - Manga/Anime style
- `元气` - Youthful/Vibrant style
- `中世纪` - Medieval style
- `水彩` - Watercolor style

---

## 使用示例

### 示例 1：生成二次元女孩

```bash
python scripts/t2i.py \
  --prompt "一个穿校服的二次元女孩，长发，大眼睛，微笑，阳光校园背景" \
  --model image-01-live \
  --style 漫画 \
  --aspect 2:3 \
  --n 3 \
  --output ./anime_girl/
```

### 示例 2：人物风格转换

```bash
python scripts/i2i.py \
  --reference https://example.com/photo.jpg \
  --prompt "穿汉服的古风美女" \
  --model image-01-live \
  --style 水彩 \
  --aspect 3:4 \
  --n 2 \
  --output ./hanfu/
```

### 示例 3：风景画生成

```bash
python scripts/t2i.py \
  --prompt "日落时的海滩，金色阳光，海浪，远处的帆船" \
  --model image-01 \
  --aspect 16:9 \
  --n 4 \
  --output ./landscape/
```

### 示例 4：使用种子复现结果

```bash
python scripts/t2i.py \
  --prompt "赛博朋克城市夜景" \
  --seed 12345 \
  --n 3 \
  --output ./cyberpunk/
```

---

## 与其他图像生成工具的对比

| 功能 | ComfyUI | MiniMax (本技能) | inference.sh |
|------|---------|------------------|-------------|
| 部署方式 | 本地 (需 GPU) | 云端 API | 云端 API |
| 人像保持 | 弱 | ✅ 强 | 弱 |
| 画风转换 | 强 | ✅ 4 种风格 | 强 |
| 上手难度 | 中等 | 低 | 低 |
| 响应速度 | 取决于配置 | 快 | 快 |

---

## 注意事项

1. **API Key 安全**：不要将 API Key 提交到公开仓库
2. **URL 有效期**：返回的图片 URL 有效期为 24 小时
3. **内容限制**：避免生成违规内容，可能触发内容安全检查
4. **费用**：按 API 调用计费，注意账户余额

---

## 脚本位置

所有脚本位于 `scripts/` 目录：

```
minimax-image/
├── SKILL.md              # 本文件
├── scripts/
│   ├── common.py         # 共享函数
│   ├── t2i.py           # 文生图
│   └── i2i.py           # 图生图
└── config/
    └── api_key.txt       # API Key 配置
```

---

## 常见问题

**Q: 返回 "invalid api key" 错误？**
A: 检查 API Key 是否正确，是否已过期

**Q: 生成失败 "图片描述涉及敏感内容"？**
A: 提示词包含敏感词，尝试修改描述

**Q: 如何提高生成质量？**
A: 使用 `--prompt-optimizer` 让 AI 自动优化提示词

**Q: 想要生成类似的结果？**
A: 使用 `--seed` 参数固定随机种子
