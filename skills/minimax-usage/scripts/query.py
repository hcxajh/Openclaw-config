#!/usr/bin/env python3
"""
MiniMax 额度查询
"""
import os
import sys
import time
import requests
import json

API_URL = "https://www.minimaxi.com/v1/api/openplatform/coding_plan/remains"


def get_api_key():
    """获取 API Key"""
    # 优先从环境变量读取
    key = os.environ.get("MINIMAX_API_KEY")
    if key:
        return key
    
    # 尝试从 minimax-image skill 读取
    config_path = os.path.join(os.path.dirname(__file__), "../../minimax-image/config/api_key.txt")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return f.read().strip()
    
    # 尝试从自身配置读取
    config_path = os.path.join(os.path.dirname(__file__), "../config/api_key.txt")
    if os.path.exists(config_path):
        with open(config_path) as f:
            return f.read().strip()
    
    print("错误: 请设置 MINIMAX_API_KEY 环境变量")
    sys.exit(1)


def query_remain():
    """查询剩余额度"""
    api_key = get_api_key()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(API_URL, headers=headers)
    data = response.json()
    
    if data.get("base_resp", {}).get("status_code") == 1004:
        print("错误: API Key 已过期，请检查")
        sys.exit(1)
    
    return data


def format_output(data):
    """格式化输出"""
    model_data = data.get("model_remains", [])
    if not model_data:
        return "未获取到额度数据"
    
    m = model_data[0]
    total = m.get("current_interval_total_count", 0)
    remaining = m.get("current_interval_usage_count", 0)
    used = total - remaining
    
    # 计算周期结束时间
    end_time_ms = m.get("end_time", 0)
    end_time = end_time_ms / 1000
    now = time.time()
    remaining_seconds = max(0, end_time - now)
    hours = int(remaining_seconds // 3600)
    minutes = int((remaining_seconds % 3600) // 60)
    
    # 当前使用的模型
    current_model = "MiniMax-M2.5-highspeed"
    
    output = f"""**当前模型额度情况：**

| 项目 | 数值 |
|------|------|
| 模型 | {current_model} |
| 本周期总配额 | {total} 次 |
| **本周期剩余** | **{remaining} 次** |
| 本周期已使用 | {used} 次 |
| 周期结束 | {hours}小时{minutes}分钟后 |"""
    
    return output


def main():
    try:
        result = query_remain()
        print(format_output(result))
    except Exception as e:
        print(f"查询失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
