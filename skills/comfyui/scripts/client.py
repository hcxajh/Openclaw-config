#!/usr/bin/env python3
"""
ComfyUI API Client
"""

import json
import requests
import time
import os
import sys
from typing import Optional, Dict, Any
from PIL import Image
import base64
import io

class ComfyUIClient:
    def __init__(self, host: str = "10.1.1.90", port: int = 8188):
        self.base_url = f"http://{host}:{port}"
        self.client_id = "openclaw"
    
    def get_history(self, prompt_id: str) -> Dict:
        """获取生成历史"""
        resp = requests.get(f"{self.base_url}/history/{prompt_id}")
        return resp.json()
    
    def get_queue(self) -> Dict:
        """获取队列状态"""
        resp = requests.get(f"{self.base_url}/queue")
        return resp.json()
    
    def get_queue_running(self) -> Dict:
        """获取当前运行状态"""
        resp = requests.get(f"{self.base_url}/queue/running")
        return resp.json()
    
    def upload_image(self, image_path: str, folder: str = "input") -> Dict:
        """上传图片"""
        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {"folder": folder}
            resp = requests.post(f"{self.base_url}/upload/image", files=files, data=data)
        return resp.json()
    
    def load_workflow(self, workflow_path: str) -> Dict:
        """加载工作流 JSON"""
        with open(workflow_path, "r") as f:
            return json.load(f)
    
    def get_api_version(self) -> Dict:
        """获取 API 版本"""
        resp = requests.get(f"{self.base_url}/api")
        return resp.json()
    
    def interrupt(self) -> None:
        """中断当前生成"""
        requests.post(f"{self.base_url}/interrupt")
    
    def clear_queue(self) -> None:
        """清空队列"""
        requests.post(f"{self.base_url}/queue/clear")


def get_output_images(prompt_id: str, client: ComfyUIClient, timeout: int = 300, progress: bool = True) -> list:
    """等待并获取输出图片"""
    start_time = time.time()
    last_progress = -1
    
    while time.time() - start_time < timeout:
        history = client.get_history(prompt_id)
        
        if prompt_id in history:
            outputs = history[prompt_id].get("outputs", {})
            
            # 尝试获取进度
            if progress:
                try:
                    # 从 KSampler 节点获取进度
                    for node_id, node_data in outputs.items():
                        if "KSampler" in node_data.get("meta", {}).get("title", ""):
                            if "progress" in node_data:
                                current_progress = int(node_data["progress"] * 100)
                                if current_progress != last_progress:
                                    print(f"\r⏳ 生成进度: {current_progress}%", end="", flush=True)
                                    last_progress = current_progress
                except:
                    pass
            
            # 检查是否完成
            images = []
            for node_id, node_data in outputs.items():
                if "images" in node_data:
                    for img in node_data["images"]:
                        images.append({
                            "filename": img["filename"],
                            "subfolder": img.get("subfolder", ""),
                            "type": img.get("type", "output")
                        })
            if images:
                if progress:
                    print()  # 换行
                return images
        
        time.sleep(1)
    
    return []


def download_image(client: ComfyUIClient, image_info: dict, output_path: str) -> str:
    """下载图片"""
    filename = image_info["filename"]
    subfolder = image_info.get("subfolder", "")
    img_type = image_info.get("type", "output")
    
    params = {
        "filename": filename,
        "subfolder": subfolder,
        "type": img_type
    }
    
    resp = requests.get(f"{client.base_url}/view", params=params)
    
    if resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(resp.content)
        return output_path
    
    raise Exception(f"Failed to download image: {resp.status_code}")


def queue_prompt(prompt: dict, client: ComfyUIClient) -> str:
    """提交 prompt 并返回 prompt_id"""
    p = {"prompt": prompt, "client_id": client.client_id}
    resp = requests.post(f"{client.base_url}/prompt", json=p)
    
    if resp.status_code != 200:
        raise Exception(f"Failed to queue prompt: {resp.text}")
    
    return resp.json()["prompt_id"]
