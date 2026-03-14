---
name: tavily-search
description: 使用 Tavily API 进行联网搜索。触发词：搜索、联网搜索、网络搜索、tavily。
allowed-tools: Bash(python3 ~/.openclaw/skills/tavily-search/scripts/search.py *)
---

# Tavily Search

使用 Tavily API 进行 AI 优化的网页搜索。

## 环境变量

需要设置 `TAVILY_API_KEY`：
```bash
export TAVILY_API_KEY="你的API Key"
```

API Key 可从 https://tavily.com 获取（有免费额度）。

## 使用方法

```bash
python3 ~/.openclaw/skills/tavily-search/scripts/search.py "搜索内容"
python3 ~/.openclaw/skills/tavily-search/scripts/search.py "搜索内容" -n 10
```

## 参数

- `query`: 搜索关键词（必填）
- `-n`, `--max-results`: 返回结果数量，默认 5，最大 20

## 示例

搜索最新 AI 新闻：
```bash
python3 ~/.openclaw/skills/tavily-search/scripts/search.py "AI news"
```
