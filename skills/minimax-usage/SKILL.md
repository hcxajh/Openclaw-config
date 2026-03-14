# MiniMax 额度查询技能

查询 MiniMax 账户剩余额度。

## 使用方法

```bash
python ~/.openclaw/skills/minimax-usage/scripts/query.py
```

或直接问我"我还有多少额度"

## 自动读取

skill 会自动从以下位置读取 API Key：
1. 环境变量 `MINIMAX_API_KEY`
2. `minimax-image/config/api_key.txt`
3. `minimax-usage/config/api_key.txt`

## 输出示例

```json
{
  "model_remains": [
    {
      "model_name": "MiniMax-M2.5",
      "current_interval_total_count": 1500,
      "current_interval_usage_count": 999,
      "remains_time": 3859441
    }
  ]
}
```

注意：`current_interval_usage_count` 是**未使用次数（剩余）**，不是已使用！

含义：
- `current_interval_total_count`: 本周期总配额 (1500)
- `current_interval_usage_count`: **剩余次数** (999)
- `remains_time`: 账户总剩余时间（秒）
- 已使用 = 总配额 - 剩余次数
