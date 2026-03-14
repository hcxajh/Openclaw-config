#!/usr/bin/env python3
"""
MiniMax Image Generation API - Common Functions
支持文生图 (T2I) 和 图生图 (I2I)
"""

import os
import json
import requests
import argparse
from typing import Optional, List, Dict, Any

# API 配置
API_BASE_URL = "https://api.minimaxi.com/v1/image_generation"
API_VERSION = "1.0.0"

# 支持的模型
MODELS = ["image-01", "image-01-live"]

# 支持的宽高比
ASPECT_RATIOS = ["1:1", "16:9", "4:3", "3:2", "2:3", "3:4", "9:16", "21:9"]

# 支持的画风仅 image-01 (-live)
STYLE_TYPES = ["漫画", "元气", "中世纪", "水彩"]


def get_api_key() -> str:
    """获取 API Key，优先从环境变量，其次从配置文件"""
    # 优先从环境变量读取
    api_key = os.environ.get("MINIMAX_API_KEY")
    if api_key:
        return api_key
    
    # 其次从配置文件读取
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "api_key.txt")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            api_key = f.read().strip()
            if api_key:
                return api_key
    
    raise ValueError("未找到 API Key，请设置 MINIMAX_API_KEY 环境变量或创建 config/api_key.txt")


def call_api(
    prompt: str,
    model: str = "image-01",
    aspect_ratio: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    response_format: str = "url",
    seed: Optional[int] = None,
    n: int = 1,
    prompt_optimizer: bool = False,
    aigc_watermark: bool = False,
    style: Optional[Dict[str, Any]] = None,
    subject_reference: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    调用 MiniMax 图像生成 API
    
    Args:
        prompt: 图像描述文本
        model: 模型名称 (image-01 或 image-01-live)
        aspect_ratio: 宽高比
        width: 宽度 (512-2048, 必须是 8 的倍数)
        height: 高度 (512-2048, 必须是 8 的倍数)
        response_format: 返回格式 (url 或 base64)
        seed: 随机种子
        n: 生成数量 (1-9)
        prompt_optimizer: 是否开启 prompt 自动优化
        aigc_watermark: 是否添加水印
        style: 画风设置 (仅 image-01-live)
        subject_reference: 人物主体参考 (图生图用)
    
    Returns:
        API 响应结果
    """
    api_key = get_api_key()
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构建请求体
    payload = {
        "model": model,
        "prompt": prompt,
        "response_format": response_format,
        "n": n,
        "prompt_optimizer": prompt_optimizer,
        "aigc_watermark": aigc_watermark
    }
    
    # 添加宽高比或自定义尺寸
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    elif width and height:
        payload["width"] = width
        payload["height"] = height
    
    # 添加种子
    if seed is not None:
        payload["seed"] = seed
    
    # 添加画风 (仅 image-01-live)
    if style:
        payload["style"] = style
    
    # 添加主体参考 (图生图)
    if subject_reference:
        payload["subject_reference"] = subject_reference
    
    # 发送请求
    response = requests.post(
        API_BASE_URL,
        headers=headers,
        json=payload,
        timeout=60
    )
    
    if response.status_code != 200:
        raise Exception(f"API 请求失败: {response.status_code} - {response.text}")
    
    result = response.json()
    
    # 检查业务错误
    base_resp = result.get("base_resp", {})
    if base_resp.get("status_code", 0) != 0:
        status_code = base_resp.get("status_code")
        status_msg = base_resp.get("status_msg", "未知错误")
        raise Exception(f"API 错误 [{status_code}]: {status_msg}")
    
    return result


def save_images(
    result: Dict[str, Any],
    output_dir: str,
    prefix: str = "image"
) -> List[str]:
    """保存生成的图片到本地"""
    import urllib.request
    import base64
    import os
    
    os.makedirs(output_dir, exist_ok=True)
    
    data = result.get("data", {})
    
    # 兼容不同的返回格式
    if isinstance(data, dict):
        image_urls = data.get("image_urls", [])
        image_base64 = data.get("image_base64", [])
    elif isinstance(data, list):
        # 可能是直接返回图片列表
        image_urls = []
        image_base64 = []
        for item in data:
            if isinstance(item, str):
                if item.startswith("data:"):
                    image_base64.append(item.split(",", 1)[1] if "," in item else "")
                else:
                    image_urls.append(item)
    else:
        image_urls = []
        image_base64 = []
    
    saved_paths = []
    
    # 处理 URL 格式
    if image_urls:
        for i, url in enumerate(image_urls):
            filename = f"{prefix}_{i+1}.png"
            filepath = os.path.join(output_dir, filename)
            try:
                urllib.request.urlretrieve(url, filepath)
                saved_paths.append(filepath)
                print(f"✓ 已保存: {filepath}")
            except Exception as e:
                print(f"✗ 保存失败 [{url}]: {e}")
    
    # 处理 Base64 格式
    if image_base64:
        import base64
        for i, b64 in enumerate(image_base64):
            filename = f"{prefix}_{i+1}.png"
            filepath = os.path.join(output_dir, filename)
            try:
                img_data = base64.b64decode(b64)
                with open(filepath, "wb") as f:
                    f.write(img_data)
                saved_paths.append(filepath)
                print(f"✓ 已保存: {filepath}")
            except Exception as e:
                print(f"✗ 保存失败 [base64]: {e}")
    
    return saved_paths


def parse_style(style_str: str, weight: float = 0.8) -> Optional[Dict[str, Any]]:
    """解析画风参数"""
    if not style_str:
        return None
    
    if style_str not in STYLE_TYPES:
        raise ValueError(f"不支持的画风: {style_str}，可选: {', '.join(STYLE_TYPES)}")
    
    return {
        "style_type": style_str,
        "style_weight": weight
    }


def main():
    parser = argparse.ArgumentParser(description="MiniMax Image Generation API")
    parser.add_argument("--api-key", type=str, help="API Key (或设置 MINIMAX_API_KEY 环境变量)")
    args = parser.parse_args()
    
    if args.api_key:
        os.environ["MINIMAX_API_KEY"] = args.api_key
    
    # 测试 API 连接
    try:
        result = call_api(
            prompt="test",
            model="image-01",
            n=1
        )
        print("✓ API 连接成功!")
        print(f"  任务 ID: {result.get('id')}")
    except Exception as e:
        print(f"✗ API 连接失败: {e}")


if __name__ == "__main__":
    main()
