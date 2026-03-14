#!/usr/bin/env python3
"""
MiniMax 视频生成 - 主体参考生成视频
"""
import os
import sys
import time
import argparse
import requests
from prompt_optimizer import optimize_prompt

API_BASE = "https://api.minimaxi.com"
TIMEOUT = 300


def get_api_key():
    key = os.environ.get("MINIMAX_API_KEY")
    if not key:
        print("错误: 请设置 MINIMAX_API_KEY 环境变量")
        sys.exit(1)
    return key


def create_task(reference: str, prompt: str, model: str = "S2V-01", duration: int = 6, resolution: str = "1080P"):
    url = f"{API_BASE}/v1/video_generation"
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "subject_reference": [
            {
                "type": "character",
                "image": [reference]
            }
        ],
        "model": model,
        "duration": duration,
        "resolution": resolution
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()["task_id"]


def query_status(task_id: str) -> str:
    url = f"{API_BASE}/v1/query/video_generation"
    headers = {"Authorization": f"Bearer {get_api_key()}"}
    
    print(f"正在等待视频生成... (任务ID: {task_id})")
    while True:
        response = requests.get(url, headers=headers, params={"task_id": task_id}, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
        status = data["status"]
        
        if status == "Success":
            return data["file_id"]
        elif status == "Fail":
            raise Exception(f"视频生成失败: {data.get('error_message', '未知错误')}")
        
        print(f"当前状态: {status}，等待 10 秒...")
        time.sleep(10)


def download_video(file_id: str, output_path: str):
    url = f"{API_BASE}/v1/files/retrieve"
    headers = {"Authorization": f"Bearer {get_api_key()}"}
    response = requests.get(url, headers=headers, params={"file_id": file_id}, timeout=TIMEOUT)
    response.raise_for_status()
    download_url = response.json()["file"]["download_url"]
    
    print(f"正在下载视频...")
    response = requests.get(download_url, timeout=TIMEOUT * 3)
    response.raise_for_status()
    
    with open(output_path, "wb") as f:
        f.write(response.content)
    print(f"视频已保存至: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="MiniMax 主体参考生成视频")
    parser.add_argument("--reference", "-r", required=True, help="参考人脸图片 URL")
    parser.add_argument("--prompt", "-p", required=True, help="视频描述文本")
    parser.add_argument("--model", "-m", default="S2V-01", help="模型名称")
    parser.add_argument("--duration", "-d", type=int, default=6, help="视频时长(秒)")
    parser.add_argument("--resolution", "-r", default="1080P", help="分辨率")
    parser.add_argument("--output", "-o", default="./outputs/", help="输出目录")
    parser.add_argument("--no-optimize", action="store_true", help="跳过提示词优化")
    
    args = parser.parse_args()
    
    # 优化提示词
    if not args.no_optimize:
        original = args.prompt
        args.prompt = optimize_prompt(args.prompt)
        print(f"提示词优化:")
        print(f"  原始: {original}")
        print(f"  优化: {args.prompt}")
    
    os.makedirs(args.output, exist_ok=True)
    
    task_id = create_task(args.reference, args.prompt, args.model, args.duration, args.resolution)
    print(f"\n任务已提交，任务ID: {task_id}")
    
    file_id = query_status(task_id)
    print(f"任务成功，文件ID: {file_id}")
    
    output_file = os.path.join(args.output, f"video_{int(time.time())}.mp4")
    download_video(file_id, output_file)


if __name__ == "__main__":
    main()
