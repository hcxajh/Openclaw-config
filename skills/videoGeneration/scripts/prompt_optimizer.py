#!/usr/bin/env python3
"""
MiniMax 视频生成 - 提示词优化模块
"""
import random


def optimize_prompt(prompt: str) -> str:
    """
    优化简单提示词，扩展为专业视频提示词
    
    公式: 主要表现物 + 场景空间 + 运动/变化 + 镜头运动 + 美感氛围
    """
    # 如果提示词已经足够详细，不再优化
    if len(prompt) > 100 or "镜头" in prompt or "色调" in prompt:
        return prompt
    
    # 镜头运动选项
    camera_movements = [
        "镜头缓缓移动拍摄",
        "镜头从侧面跟随",
        "镜头缓慢推进",
        "镜头从远到近",
        "镜头环绕拍摄",
        "镜头从高空俯拍",
        "镜头从特写拉开",
        "镜头稳定固定拍摄",
    ]
    
    # 色调氛围选项
    warm_moods = [
        "画面呈现暖色调，色彩浓郁，氛围轻松惬意",
        "画面色调偏暖，阳光充足，氛围温馨",
        "画面色调明亮，色彩鲜艳，氛围欢快",
        "画面暖色调，氛围浪漫",
    ]
    
    cool_moods = [
        "画面色调偏冷，氛围宁静",
        "画面色调灰暗，色彩低饱和，氛围阴郁",
        "画面冷色调，氛围孤独",
        "画面明暗对比强烈，氛围紧张",
    ]
    
    natural_moods = [
        "画面色调自然写实",
        "画面色彩真实自然",
        "画面呈现自然光效",
    ]
    
    # 选择合适的扩展
    camera = random.choice(camera_movements)
    mood = random.choice(warm_moods + natural_moods)
    
    # 根据关键词判断氛围
    if any(k in prompt for k in ["夜晚", "黑暗", "阴", "孤独", "悲伤"]):
        mood = random.choice(cool_moods)
    elif any(k in prompt for k in ["阳光", "快乐", "开心", "温暖", "春天"]):
        mood = random.choice(warm_moods)
    
    # 构建优化后的提示词
    optimized = f"{prompt}，{camera}，{mood}。"
    
    return optimized


if __name__ == "__main__":
    # 测试
    test_prompts = [
        "一只小狗在公园奔跑",
        "女人在咖啡馆思考",
        "男人在雨中行走",
        "学生在图书馆看书",
    ]
    
    for p in test_prompts:
        print(f"原始: {p}")
        print(f"优化: {optimize_prompt(p)}")
        print("---")
