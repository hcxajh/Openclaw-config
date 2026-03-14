---
name: cron-manager
description: OpenClaw 定时任务管理技能。用于添加、查看、删除定时任务，管理 Cron Jobs。
---

# 定时任务管理

## 触发条件

用户说：定时任务 / cron / 添加定时 / 删除定时 / 任务列表

## 核心功能

### 1. 查看任务列表

```bash
openclaw cron list
```

或直接读取文件：
```bash
cat ~/.openclaw/cron/jobs.json
```

### 2. 添加定时任务

#### 命令行方式
```bash
openclaw cron add \
  --name "任务名" \
  --cron "cron表达式" \
  --message "消息内容" \
  --channel feishu \
  --to "user:用户ID" \
  --account 账号名 \
  --announce
```

#### 手动编辑方式
直接修改 `~/.openclaw/cron/jobs.json`，添加新任务到 `jobs` 数组。

### 3. 删除定时任务

```bash
openclaw cron remove 任务ID
```

或手动编辑 jobs.json，删除对应任务。

## Cron 表达式

格式：`分 时 日 月 周`

| 表达式 | 含义 |
|--------|------|
| `0 8 * * *` | 每天 8:00 |
| `30 7 * * *` | 每天 7:30 |
| `25 9 * * 1-5` | 工作日 9:25 |
| `*/15 * * * *` | 每15分钟 |
| `*/4 * * * *` | 每4分钟 |

## 目标格式

- 飞书用户：`user:ou_xxxxxxxx`
- 飞书群聊：`chat:oc_xxxxxxxx`
- 电报用户：`user:ID或用户名`
- 电报群组：`chat:群组ID`

## 常用账号

| 渠道 | 账号名 |
|------|--------|
| 飞书 | daily, coding, art, video |
| 电报 | daily, coding, art |

## 任务结构

```json
{
  "id": "唯一ID",
  "name": "任务名",
  "enabled": true,
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * *"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "要执行的消息"
  },
  "delivery": {
    "mode": "announce",
    "channel": "feishu",
    "to": "user:ou_xxx",
    "accountId": "daily"
  }
}
```

## 文件位置

- 任务配置：`~/.openclaw/cron/jobs.json`
- 日志文件：`~/.openclaw/logs/gateway.log`

## 故障排查

1. **任务不执行** → 检查 Gateway 状态 `openclaw gateway status`
2. **消息发不出** → 检查目标ID格式和账号是否正确
3. **查看日志** → `tail -f ~/.openclaw/logs/gateway.log | grep cron`

## 使用示例

### 添加每日天气任务
```
用户：帮我设置一个每天早上7点半的天气提醒
操作：
1. 确认目标用户ID
2. 添加任务到 jobs.json
3. 确认添加成功
```

### 添加股票提醒
```
用户：每天早上9点25分提醒我查股票
操作：
1. 确认股票代码和用户ID
2. cron表达式：25 9 * * 1-5
3. 添加任务
```
