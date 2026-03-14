#!/usr/bin/env python3
"""
Image to Image - 图生图
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


def build_i2i_workflow(
    input_image_path: str,
    positive_prompt: str,
    negative_prompt: str = "",
    width: int = 512,
    height: int = 512,
    steps: int = 20,
    cfg: float = 3.5,
    strength: float = 0.7,
    seed: int = 0,
    model: str = "flux1-dev-fp8.safetensors"
) -> dict:
    """构建图生图工作流"""
    
    client = ComfyUIClient()
    upload_result = client.upload_image(input_image_path)
    image_name = upload_result["name"]
    
    # Flux 模型使用不同的节点
    workflow = {
        "LoadImage": {
            "inputs": {
                "image": image_name,
                "upload": "input"
            },
            "class_type": "LoadImage",
            "_meta": {"title": "Load Image"}
        },
        "LoadCheckpoint": {
            "inputs": {
                "ckpt_name": model
            },
            "class_type": "CheckpointLoaderSimple",
            "_meta": {"title": "Load Checkpoint"}
        },
        "CLIPTextEncode_positive": {
            "inputs": {
                "text": positive_prompt,
                "clip": ["LoadCheckpoint", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Positive Prompt"}
        },
        "CLIPTextEncode_negative": {
            "inputs": {
                "text": negative_prompt,
                "clip": ["LoadCheckpoint", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "Negative Prompt"}
        },
        "VAEEncode": {
            "inputs": {
                "pixels": ["LoadImage", 0],
                "vae": ["LoadCheckpoint", 2]
            },
            "class_type": "VAEEncode",
            "_meta": {"title": "VAE Encode"}
        },
        "KSampler": {
            "inputs": {
                "model": ["LoadCheckpoint", 0],
                "positive": ["CLIPTextEncode_positive", 0],
                "negative": ["CLIPTextEncode_negative", 0],
                "latent_image": ["VAEEncode", 0],
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": strength
            },
            "class_type": "KSampler",
            "_meta": {"title": "KSampler"}
        },
        "VAEDecode": {
            "inputs": {
                "samples": ["KSampler", 0],
                "vae": ["LoadCheckpoint", 2]
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"}
        },
        "SaveImage": {
            "inputs": {
                "images": ["VAEDecode", 0],
                "filename_prefix": "ComfyUI"
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Image"}
        }
    }
    
    return workflow


def main():
    parser = argparse.ArgumentParser(description="ComfyUI Image to Image")
    parser.add_argument("--input", "-i", required=True, help="输入图片路径")
    parser.add_argument("--prompt", "-p", required=True, help="正面提示词")
    parser.add_argument("--negative", "-n", default="", help="负面提示词")
    parser.add_argument("--width", "-W", type=int, default=512, help="宽度")
    parser.add_argument("--height", "-H", type=int, default=512, help="高度")
    parser.add_argument("--steps", "-s", type=int, default=20, help="采样步数")
    parser.add_argument("--cfg", type=float, default=3.5, help="CFG 引导强度")
    parser.add_argument("--strength", "-str", type=float, default=0.7, help="重绘幅度")
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
    print(f"✓ 输入: {args.input}")
    print(f"✓ 提示词: {args.prompt}")
    print(f"✓ 模型: {args.model}")
    print(f"✓ 重绘幅度: {args.strength}")
    print(f"✓ 输出: {output_path}")
    
    workflow = build_i2i_workflow(
        input_image_path=args.input,
        positive_prompt=args.prompt,
        negative_prompt=args.negative,
        width=args.width,
        height=args.height,
        steps=args.steps,
        cfg=args.cfg,
        strength=args.strength,
        seed=args.seed,
        model=args.model
    )
    
    print(f"✓ 提交生成任务...")
    prompt_id = queue_prompt(workflow, client)
    print(f"  Prompt ID: {prompt_id}")
    
    print(f"⏳ 正在生成...")
    images = get_output_images(prompt_id, client)
    
    if images:
        download_image(client, images[0], output_path)
        print(f"✓ 已保存到: {output_path}")
    else:
        print("✗ 生成超时")
        sys.exit(1)


if __name__ == "__main__":
    main()
