# Video Generation Skill

使用 MiniMax 视频生成 API 进行视频创作。支持**自动提示词优化**，将简单描述扩展为专业视频提示词。

## 支持的模式

1. **文生视频 (T2V)** - 根据文本描述生成视频
2. **图生视频 (I2V)** - 首帧图片 + 文本生成视频
3. **首尾帧生成** - 首帧 + 尾帧图片生成视频
4. **主体参考** - 人脸参考保持人物特征一致性

## 快速开始

### 1. 配置 API Key

```bash
export MINIMAX_API_KEY="sk-api-xxxxx"
```

### 2. 基本用法

**文生视频（自动优化提示词）：**
```bash
python scripts/t2v.py --prompt "一只小狗在公园奔跑"
```

**图生视频：**
```bash
python scripts/i2v.py --first-frame image.png --prompt "人开始跳舞"
```

**首尾帧生成：**
```bash
python scripts/start_end.py --first-frame start.png --last-frame end.png --prompt "女孩成长"
```

**主体参考：**
```bash
python scripts/subject.py --reference face.png --prompt "模特走秀"
```

---

## 提示词优化

脚本会自动优化简单提示词，使用以下公式：

### 基础公式
```
主要表现物 + 场景空间 + 运动/变化
```

### 精确公式
```
主要表现物 + 场景空间 + 运动/变化 + 镜头运动 + 美感氛围
```

### 优化示例

| 原始提示词 | 优化后 |
|-----------|--------|
| 一只小狗在公园奔跑 | 阳光明媚的公园草坪上，一只金黄色的小狗欢快地在草地上奔跑，它的尾巴随风摇摆，镜头跟随小狗移动，画面色调温暖明亮，氛围轻松愉悦 |
| 女人在咖啡馆思考 | 镜头拍摄一个女性坐在咖啡馆里，女人抬头思考着，镜头缓缓移动拍摄到窗外的街道，画面色调偏暖，色彩浓郁，氛围惬意 |

### 优化参数

添加 `--no-optimize` 跳过自动优化：
```bash
python scripts/t2v.py --prompt "你的原始prompt" --no-optimize
```

---

## 参数说明

### 通用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--model` | 模型: `MiniMax-Hailuo-2.3`, `MiniMax-Hailuo-02`, `S2V-01` | MiniMax-Hailuo-2.3 |
| `--duration` | 视频时长: 5, 6, 10 秒 | 6 |
| `--resolution` | 分辨率: 720P, 1080P | 1080P |
| `--output, -o` | 输出目录 | ./outputs/ |
| `--no-optimize` | 跳过提示词优化 | false |

### 文生视频 (t2v.py)

| 参数 | 说明 | 必填 |
|------|------|------|
| `--prompt, -p` | 视频描述文本 | ✅ |

### 图生视频 (i2v.py)

| 参数 | 说明 | 必填 |
|------|------|------|
| `--first-frame, -f` | 首帧图片 URL 或本地路径 | ✅ |
| `--prompt, -p` | 动态描述文本 | ✅ |

### 首尾帧 (start_end.py)

| 参数 | 说明 | 必填 |
|------|------|------|
| `--first-frame, -f` | 首帧图片 | ✅ |
| `--last-frame, -l` | 尾帧图片 | ✅ |
| `--prompt, -p` | 变化描述 | ✅ |

### 主体参考 (subject.py)

| 参数 | 说明 | 必填 |
|------|------|------|
| `--reference, -r` | 参考人脸图片 | ✅ |
| `--prompt, -p` | 视频描述 | ✅ |

---

## 模型说明

| 模型 | 适用场景 | 支持时长 |
|------|---------|---------|
| MiniMax-Hailuo-2.3 | 文生视频、图生视频 | 5s, 6s |
| MiniMax-Hailuo-02 | 首尾帧 | 6s |
| S2V-01 | 主体参考 | 6s |

---

## 输出

生成的视频保存在指定目录，文件名格式：`video_{timestamp}.mp4`

---

## 注意事项

1. 视频生成是异步过程，需要轮询等待（约 1-3 分钟）
2. 推荐轮询间隔 10 秒，避免压力服务器
3. API Key 需要在 MiniMax 平台申请
