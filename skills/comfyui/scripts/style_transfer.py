#!/usr/bin/env python3
"""
Style Transfer - 风格迁移
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import ComfyUIClient, queue_prompt, get_output_images, download_image


# 默认输出目录
DEFAULT_OUTPUT_DIR = os.path.join(os.getcwd(), "comfyui")


def get_next_filename(output_dir: str, prefix: str = "IMG", ext: str = ".png") -> str:
    """获取下一个序号文件名"""
    os.makedirs(output_dir, exist_ok=True)
    
    existing = [f for f in os.listdir(output_dir) if f.startswith(prefix) and f.endswith(ext)]
    if existing:
        nums = []
        for f in existing:
            try:
                num = int(f.replace(prefix, "").replace(ext, ""))
                nums.append(num)
            except:
                pass
        next_num = max(nums) + 1 if nums else 1
    else:
        next_num = 1
    
    return os.path.join(output_dir, f"{prefix}{next_num:03d}{ext}")


def main():
    parser = argparse.ArgumentParser(description="ComfyUI Style Transfer")
    parser.add_argument("--input", "-i", required=True, help="内容图片路径")
    parser.add_argument("--prompt", "-p", required=True, help="风格提示词")
    parser.add_argument("--style", default="anime", help="风格类型")
    parser.add_argument("--width", "-W", type=int, default=512, help="宽度")
    parser.add_argument("--height", "-H", type=int, default=512, help="高度")
    parser.add_argument("--steps", "-s", type=int, default=20, help="采样步数")
    parser.add_argument("--seed", type=int, default=0, help="随机种子")
    parser.add_argument("--output", "-o", default=None, help="输出路径")
    parser.add_argument("--host", default="10.1.1.90", help="ComfyUI 主机")
    parser.add_argument("--port", type=int, default=8188, help="ComfyUI 端口")
    parser.add_argument("--model", "-m", default="flux1-dev-fp8.safetensors", help="模型名称")
    
    args = parser.parse_args()
    
    client = ComfyUIClient(args.host, args.port)
    
    # 生成输出路径
    if args.output:
        output_path = args.output
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        output_dir = os.path.join(DEFAULT_OUTPUT_DIR, today)
        output_path = get_next_filename(output_dir)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    print(f"✓ 连接到 ComfyUI: {args.host}:{args.port}")
    print(f"✓ 内容图片: {args.input}")
    print(f"✓ 风格: {args.style}")
    print(f"✓ 提示词: {args.prompt}")
    print(f"✓ 输出: {output_path}")
    print("⚠ 风格迁移功能需要特定工作流，请根据实际情况调整脚本")


if __name__ == "__main__":
    main()
