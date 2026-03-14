#!/usr/bin/env python3
"""
Text to Image - 文生图 (支持 Flux 完整工作流)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import ComfyUIClient, queue_prompt, get_output_images, download_image


# 默认输出目录（当前工作空间）
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


def build_t2i_workflow(
    positive_prompt: str,
    negative_prompt: str = "",
    width: int = 1024,
    height: int = 1024,
    steps: int = 20,
    cfg: float = 1,
    seed: int = 0,
    model: str = "flux1-dev.safetensors"
) -> dict:
    """构建文生图工作流 (Flux 完整版)"""
    
    workflow = {
        # 空 Latent 图像 (SD3)
        "27": {
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1
            },
            "class_type": "EmptySD3LatentImage",
            "_meta": {"title": "空Latent图像（SD3）"}
        },
        # UNet 加载器
        "38": {
            "inputs": {
                "unet_name": model,
                "weight_dtype": "default"
            },
            "class_type": "UNETLoader",
            "_meta": {"title": "UNet加载器"}
        },
        # VAE 加载器
        "39": {
            "inputs": {
                "vae_name": "ae.safetensors"
            },
            "class_type": "VAELoader",
            "_meta": {"title": "加载VAE"}
        },
        # CLIP 加载器 (双 CLiP)
        "40": {
            "inputs": {
                "clip_name1": "clip_l.safetensors",
                "clip_name2": "t5xxl_fp16.safetensors",
                "type": "flux",
                "device": "default"
            },
            "class_type": "DualCLIPLoader",
            "_meta": {"title": "双CLIP加载器"}
        },
        # 正面提示词 (Flux 格式)
        "41": {
            "inputs": {
                "clip_l": positive_prompt,
                "t5xxl": positive_prompt,
                "guidance": 3.5,
                "clip": ["40", 0]
            },
            "class_type": "CLIPTextEncodeFlux",
            "_meta": {"title": "CLIP文本编码（Flux）"}
        },
        # 负面提示词 (零化)
        "42": {
            "inputs": {
                "conditioning": ["41", 0]
            },
            "class_type": "ConditioningZeroOut",
            "_meta": {"title": "条件零化"}
        },
        # K 采样器
        "31": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1,
                "model": ["38", 0],
                "positive": ["41", 0],
                "negative": ["42", 0],
                "latent_image": ["27", 0]
            },
            "class_type": "KSampler",
            "_meta": {"title": "K采样器"}
        },
        # VAE 解码
        "8": {
            "inputs": {
                "samples": ["31", 0],
                "vae": ["39", 0]
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE解码"}
        },
        # 保存图像
        "9": {
            "inputs": {
                "filename_prefix": "ComfyUI",
                "images": ["8", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "保存图像"}
        }
    }
    
    return workflow


def main():
    parser = argparse.ArgumentParser(description="ComfyUI Text to Image (Flux)")
    parser.add_argument("--prompt", "-p", required=True, help="正面提示词")
    parser.add_argument("--negative", "-n", default="", help="负面提示词 (可选)")
    parser.add_argument("--width", "-W", type=int, default=1024, help="宽度 (默认 1024)")
    parser.add_argument("--height", "-H", type=int, default=1024, help="高度 (默认 1024)")
    parser.add_argument("--steps", "-s", type=int, default=20, help="采样步数 (默认 20)")
    parser.add_argument("--cfg", type=float, default=1, help="CFG 引导强度 (默认 1)")
    parser.add_argument("--seed", type=int, default=0, help="随机种子 (0=随机)")
    parser.add_argument("--output", "-o", default=None, help="输出路径")
    parser.add_argument("--host", default="10.1.1.90", help="ComfyUI 主机")
    parser.add_argument("--port", type=int, default=8188, help="ComfyUI 端口")
    parser.add_argument("--model", "-m", default="flux1-dev.safetensors", help="模型名称 (默认 flux1-dev.safetensors)")
    
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
    print(f"✓ 提示词: {args.prompt}")
    print(f"✓ 模型: {args.model}")
    print(f"✓ 尺寸: {args.width}x{args.height}")
    print(f"✓ 步数: {args.steps}")
    print(f"✓ CFG: {args.cfg}")
    print(f"✓ 输出: {output_path}")
    
    workflow = build_t2i_workflow(
        positive_prompt=args.prompt,
        negative_prompt=args.negative,
        width=args.width,
        height=args.height,
        steps=args.steps,
        cfg=args.cfg,
        seed=args.seed,
        model=args.model
    )
    
    print(f"✓ 提交生成任务...")
    prompt_id = queue_prompt(workflow, client)
    print(f"  Prompt ID: {prompt_id}")
    
    print(f"⏳ 正在生成...")
    gen_start = time.time()
    images = get_output_images(prompt_id, client)
    gen_time = time.time() - gen_start
    
    if images:
        download_image(client, images[0], output_path)
        print(f"✓ 已保存到: {output_path}")
        print(f"⏱️ 生成耗时: {gen_time:.1f} 秒")
    else:
        print("✗ 生成超时")
        sys.exit(1)


if __name__ == "__main__":
    main()
