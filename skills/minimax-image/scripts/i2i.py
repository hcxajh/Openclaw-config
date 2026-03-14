#!/usr/bin/env python3
"""
MiniMax 图生图 (Image to Image) 脚本
用法: python i2i.py --reference 图片URL [选项]
"""

import argparse
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import call_api, save_images, parse_style, MODELS, ASPECT_RATIOS, STYLE_TYPES


def main():
    parser = argparse.ArgumentParser(
        description="MiniMax 图生图 (Image to Image) - 保持人物特征",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法 - 使用参考图
  python i2i.py --reference https://example.com/photo.jpg --prompt "穿西装"
  
  # 指定模型和画风
  python i2i.py --reference photo.jpg --prompt "穿汉服" --model image-01-live --style 漫画
  
  # 多张参考图
  python i2i.py --reference "photo1.jpg,photo2.jpg" --prompt "艺术照"
  
  # 指定宽高比
  python i2i.py --reference img.jpg --prompt "商务照" --aspect 16:9
        """
    )
    
    # 必需参数
    parser.add_argument("--reference", "-r", type=str, required=True,
                        help="参考图片 URL 或本地路径，多个用逗号分隔")
    
    # 提示词
    parser.add_argument("--prompt", "-p", type=str, required=True,
                        help="图像描述文本，最长 1500 字符")
    
    # 模型选项
    parser.add_argument("--model", "-m", type=str, default="image-01-live",
                        choices=MODELS,
                        help=f"模型名称 (默认: image-01-live)")
    
    # 画风选项 (仅 image-01-live)
    parser.add_argument("--style", "-s", type=str, 
                        choices=STYLE_TYPES,
                        help=f"画风类型 (仅 image-01-live): {', '.join(STYLE_TYPES)}")
    parser.add_argument("--style-weight", type=float, default=0.8,
                        help="画风权重 0-1 (默认: 0.8)")
    
    # 尺寸选项
    parser.add_argument("--aspect", "-a", type=str, default="9:16",
                        choices=ASPECT_RATIOS,
                        help=f"宽高比: {', '.join(ASPECT_RATIOS)} (默认: 9:16)")
    parser.add_argument("--width", type=int,
                        help="宽度 512-2048，必须是 8 的倍数")
    parser.add_argument("--height", type=int,
                        help="高度 512-2048，必须是 8 的倍数")
    
    # 生成选项
    parser.add_argument("--n", "-n", type=int, default=1, choices=range(1, 10),
                        help="生成图片数量 1-9 (默认: 1)")
    parser.add_argument("--seed", type=int, 
                        help="随机种子，用于复现结果")
    
    # 输出选项
    parser.add_argument("--output", "-o", type=str, default="./outputs/",
                        help="输出目录 (默认: ./outputs/)")
    parser.add_argument("--prefix", type=str, default="i2i",
                        help="输出文件前缀 (默认: i2i)")
    parser.add_argument("--format", type=str, default="url", choices=["url", "base64"],
                        help="返回格式 (默认: url)")
    
    # 其他选项
    parser.add_argument("--prompt-optimizer", action="store_true",
                        help="开启 prompt 自动优化")
    parser.add_argument("--watermark", action="store_true",
                        help="添加 AI 水印")
    parser.add_argument("--api-key", type=str,
                        help="API Key (或设置 MINIMAX_API_KEY 环境变量)")
    
    args = parser.parse_args()
    
    # 设置 API Key
    if args.api_key:
        os.environ["MINIMAX_API_KEY"] = args.api_key
    
    # 解析参考图
    references = [r.strip() for r in args.reference.split(",")]
    
    # 构建主体参考
    subject_reference = []
    for ref in references:
        # 判断是 URL 还是本地文件
        if ref.startswith("http://") or ref.startswith("https://"):
            image_file = ref
        elif ref.startswith("data:"):
            image_file = ref  # Base64 Data URL
        elif os.path.exists(ref):
            # 读取本地文件转为 Base64
            import base64
            with open(ref, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("utf-8")
            ext = os.path.splitext(ref)[1].lower()
            mime = "image/jpeg" if ext in [".jpg", ".jpeg"] else "image/png"
            image_file = f"data:{mime};base64,{b64}"
        else:
            print(f"⚠️  参考图不存在: {ref}")
            continue
        
        subject_reference.append({
            "type": "character",
            "image_file": image_file
        })
    
    if not subject_reference:
        raise ValueError("没有有效的参考图片")
    
    # 验证画风选项
    style = None
    if args.style:
        if args.model != "image-01-live":
            print(f"⚠️  画风选项仅在 model=image-01-live 时生效")
        else:
            style = parse_style(args.style, args.style_weight)
    
    print("=" * 50)
    print("🎨 MiniMax 图生图 (Image to Image)")
    print("=" * 50)
    print(f"📸 参考图: {len(references)} 张")
    print(f"📝 Prompt: {args.prompt[:50]}{'...' if len(args.prompt) > 50 else ''}")
    print(f"🤖 Model: {args.model}")
    if args.style:
        print(f"🎭 Style: {args.style} (权重: {args.style_weight})")
    if args.aspect:
        print(f"📐 Aspect: {args.aspect}")
    if args.seed:
        print(f"🎲 Seed: {args.seed}")
    print(f"🖼️  Count: {args.n}")
    print(f"📁 Output: {args.output}")
    print("=" * 50)
    
    try:
        # 调用 API
        result = call_api(
            prompt=args.prompt,
            model=args.model,
            aspect_ratio=args.aspect,
            width=args.width,
            height=args.height,
            response_format=args.format,
            seed=args.seed,
            n=args.n,
            prompt_optimizer=args.prompt_optimizer,
            aigc_watermark=args.watermark,
            style=style,
            subject_reference=subject_reference
        )
        
        # 打印结果
        task_id = result.get("id", "N/A")
        metadata = result.get("metadata", {})
        
        # 确保是整数类型
        try:
            success_count = int(metadata.get("success_count", 0))
            failed_count = int(metadata.get("failed_count", 0))
        except (ValueError, TypeError):
            success_count = 0
            failed_count = 0
        
        print(f"\n✅ 生成完成!")
        print(f"   任务 ID: {task_id}")
        print(f"   成功: {success_count} 张")
        print(f"   失败: {failed_count} 张")
        
        # 保存图片
        if success_count > 0:
            saved = save_images(result, args.output, args.prefix)
            print(f"\n📦 已保存 {len(saved)} 张图片到 {args.output}")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
