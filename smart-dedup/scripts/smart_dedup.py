#!/usr/bin/env python3
"""
smart_dedup.py — 文档类视频切片智能去重工具

组合方案：SSIM 三层分流 + EasyOCR 灰色地带裁决

核心逻辑：
  1. SSIM ≥ 0.98 → 绝对重复帧（静止画面/光标闪烁/压缩噪点）→ 直接移除，跳过 OCR
  2. SSIM < 0.70 → 绝对新页面（翻页/切换窗口）→ 直接保留，跳过 OCR
  3. 0.70 ~ 0.98 → 灰色地带，触发 OCR 文本比对：
     - 文本相似度 ≥ 0.90 → 内容未变，视为重复
     - 文本相似度 < 0.90 → 局部文字更新，保留

适用场景：PPT 录屏、代码演示、网页滚动、文档展示等 10 分钟级视频切片（约 600 张）

用法：
  python smart_dedup.py -i ./frames -o ./unique_slides
  python smart_dedup.py -i ./frames -o ./unique_slides --gpu --strict-ssim 0.98 --loose-ssim 0.70 --text-thresh 0.90
"""

import os
import re
import sys
import glob
import shutil
import time
import logging
import difflib
import argparse
from datetime import datetime
from pathlib import Path

# ============================================================
#  依赖检查（友好提示，而非崩溃）
# ============================================================

def check_dependencies():
    """检查必要依赖是否安装，未安装则给出友好提示"""
    missing = []
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    try:
        from skimage.metrics import structural_similarity
    except ImportError:
        missing.append("scikit-image")
    try:
        import easyocr
    except ImportError:
        missing.append("easyocr")

    if missing:
        print("=" * 60)
        print("缺少以下依赖，请先安装：\n")
        print("  pip install " + " ".join(missing))
        print("\n或使用 requirements.txt：")
        print("  pip install -r requirements.txt")
        print("=" * 60)
        sys.exit(1)


check_dependencies()

import cv2
import numpy as np
import easyocr
from skimage.metrics import structural_similarity as ssim


# ============================================================
#  日志配置
# ============================================================

def setup_logger(log_dir: str) -> logging.Logger:
    """配置日志：同时输出到控制台和文件"""
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f"dedup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

    logger = logging.getLogger("smart_dedup")
    logger.setLevel(logging.DEBUG)

    # 文件日志：详细级别
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-7s | %(message)s"))

    # 控制台日志：简要级别
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("%(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(f"日志文件: {log_file}")
    return logger


# ============================================================
#  核心函数
# ============================================================

def extract_number(file_path: str) -> int:
    """提取文件名中的数字，确保 frame_2 排在 frame_10 前面"""
    match = re.search(r'\d+', os.path.basename(file_path))
    return int(match.group()) if match else 0


def imread_cjk(file_path: str, flags=cv2.IMREAD_GRAYSCALE):
    """
    安全读取图片，兼容含中文/日文等非 ASCII 字符的路径。
    OpenCV 的 cv2.imread() 在 Windows 上无法处理 CJK 路径，
    需要用 imdecode 绕行。
    """
    file_path = os.path.normpath(file_path)
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        img = cv2.imdecode(np.frombuffer(data, np.uint8), flags)
        return img
    except Exception:
        return None


def calculate_ssim(img1_path: str, img2_path: str) -> float:
    """
    计算两张图片的结构相似度 (SSIM)
    返回 0.0 ~ 1.0，1.0 表示完全相同
    """
    img1 = imread_cjk(img1_path)
    img2 = imread_cjk(img2_path)

    if img1 is None or img2 is None:
        return 0.0

    # 统一尺寸（SSIM 要求两张图同尺寸）
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    return ssim(img1, img2)


def get_text_similarity(text1: str, text2: str) -> float:
    """
    计算两段文本的相似度 (0.0 ~ 1.0)
    使用 difflib.SequenceMatcher，先去除所有空白字符防止排版干扰
    """
    t1 = re.sub(r'\s+', '', text1)
    t2 = re.sub(r'\s+', '', text2)
    if not t1 and not t2:
        return 1.0
    if not t1 or not t2:
        return 0.0
    return difflib.SequenceMatcher(None, t1, t2).ratio()


def extract_text(reader, img_path: str) -> str:
    """使用 EasyOCR 提取图片中的文字（兼容 CJK 路径）"""
    # EasyOCR 内部也用 cv2.imread()，同样有 CJK 路径问题。
    # 先用 imread_cjk 读成 numpy 数组再传给 readtext
    img = imread_cjk(img_path, cv2.IMREAD_COLOR)  # EasyOCR 需要彩色图
    results = reader.readtext(img)
    return " ".join([res[1] for res in results])


# ============================================================
#  GPU 检测
# ============================================================

def detect_gpu() -> bool:
    """检测是否有可用的 NVIDIA GPU（用于 EasyOCR 加速）"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        # 没有 PyTorch，尝试通过 nvidia-smi 检测
        try:
            import subprocess
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=5
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except Exception:
            return False
    except Exception:
        return False


# ============================================================
#  主去重逻辑
# ============================================================

def deduplicate(
    input_dir: str,
    output_dir: str,
    dup_dir: str,
    strict_ssim: float,
    loose_ssim: float,
    text_thresh: float,
    use_gpu: bool,
    ocr_lang: list,
    logger: logging.Logger,
):
    """
    三层分流去重主逻辑
    注意：所有路径均通过 os.path.normpath() 规范化，防止
    Git Bash 的 Unix 风格路径 (H:/...) 与 Windows 反斜杠混用
    导致 OpenCV cv2.imread() 无法读取图片。"""

    # 规范化所有路径，避免正反斜杠混用
    input_dir = os.path.normpath(input_dir)
    output_dir = os.path.normpath(output_dir)
    dup_dir = os.path.normpath(dup_dir)

    start_time = time.time()

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(dup_dir, exist_ok=True)

    # 收集并排序图片
    extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.webp']
    image_files = []
    for ext in extensions:
        image_files.extend(glob.glob(os.path.join(input_dir, ext)))
        # 也匹配大写扩展名
        image_files.extend(glob.glob(os.path.join(input_dir, ext.upper())))
    # 去重（大小写扩展名可能匹配到同一文件）
    image_files = list(set(image_files))
    image_files = sorted(image_files, key=extract_number)

    if not image_files:
        logger.error(f"在目录 {input_dir} 中未找到任何图片！")
        return

    total = len(image_files)
    logger.info("=" * 60)
    logger.info(f"  文档切片智能去重工具 v1.0")
    logger.info(f"  组合方案: SSIM 三层分流 + EasyOCR 灰色地带裁决")
    logger.info("=" * 60)
    logger.info(f"输入目录:     {input_dir}")
    logger.info(f"保留输出:     {output_dir}")
    logger.info(f"重复存放:     {dup_dir}")
    logger.info(f"图片总数:     {total} 张")
    logger.info(f"SSIM 严格阈值: {strict_ssim} (≥此值 → 绝对重复)")
    logger.info(f"SSIM 宽松阈值: {loose_ssim} (<此值 → 绝对新页面)")
    logger.info(f"文本相似阈值:  {text_thresh} (≥此值 → 文字未变)")
    logger.info(f"GPU 加速:     {'是' if use_gpu else '否'}")
    logger.info(f"OCR 语言:     {ocr_lang}")
    logger.info("=" * 60)

    # 初始化 EasyOCR
    logger.info("正在加载 OCR 模型 (首次运行需下载约 100MB 模型，请稍候)...")
    ocr_load_start = time.time()
    reader = easyocr.Reader(ocr_lang, gpu=use_gpu)
    logger.info(f"OCR 模型加载完成，耗时 {time.time() - ocr_load_start:.1f}s")

    # 统计计数器
    kept_images = [image_files[0]]
    last_img_path = image_files[0]
    dup_count = 0
    ocr_call_count = 0

    # 灰色地带分类统计
    tier1_strict_dup = 0    # SSIM ≥ 严格阈值
    tier2_new_page = 0      # SSIM < 宽松阈值
    tier3_ocr_dup = 0       # 灰色地带 → OCR 判定重复
    tier3_ocr_keep = 0      # 灰色地带 → OCR 判定新内容

    # 提取第一张图的文本作为基准（延迟加载策略：只在需要时才 OCR）
    last_text = None  # 延迟加载

    logger.info(f"\n开始分析 {total} 张图片...")
    logger.info("-" * 60)

    for i, img_path in enumerate(image_files):
        filename = os.path.basename(img_path)
        progress = f"[{i+1}/{total}]"

        if i == 0:
            # 第一张图始终保留
            logger.info(f"{progress} ✅ [保留] {filename} (初始基准帧)")
            continue

        # === 第 1 步：极速 SSIM 计算（毫秒级）===
        current_ssim = calculate_ssim(last_img_path, img_path)

        if current_ssim >= strict_ssim:
            # === Tier 1：绝对重复帧 ===
            # SSIM ≥ 0.98 → 静止画面/光标闪烁/压缩噪点，直接移除
            dup_count += 1
            tier1_strict_dup += 1
            shutil.move(img_path, os.path.join(dup_dir, filename))
            logger.info(
                f"{progress} ❌ [剔除] {filename} | "
                f"SSIM: {current_ssim:.3f} | "
                f"Tier1-绝对重复 (跳过OCR)"
            )

        elif current_ssim < loose_ssim:
            # === Tier 2：绝对新页面 ===
            # SSIM < 0.70 → 翻页/切换窗口，直接保留，跳过 OCR
            kept_images.append(img_path)
            last_img_path = img_path
            last_text = None  # 清空 OCR 缓存，下次需要时重新提取
            tier2_new_page += 1
            logger.info(
                f"{progress} 🚀 [保留] {filename} | "
                f"SSIM: {current_ssim:.3f} | "
                f"Tier2-画面大变化 (跳过OCR)"
            )

        else:
            # === Tier 3：灰色地带 (loose_ssim ~ strict_ssim) ===
            # 画面有变化但不大，可能是局部文字更新或轻微动画，触发 OCR 裁决
            ocr_call_count += 1

            # 延迟加载：只在第一次进入灰色地带时才提取基准帧文本
            if last_text is None:
                last_text = extract_text(reader, last_img_path)

            current_text = extract_text(reader, img_path)
            text_sim = get_text_similarity(last_text, current_text)

            if text_sim >= text_thresh:
                # 文字没变 → 判定为静止废帧，剔除
                dup_count += 1
                tier3_ocr_dup += 1
                shutil.move(img_path, os.path.join(dup_dir, filename))
                logger.info(
                    f"{progress} ❌ [剔除] {filename} | "
                    f"SSIM: {current_ssim:.3f} | "
                    f"文本: {text_sim:.3f} | "
                    f"Tier3-OCR判定重复 (内容未变)"
                )
            else:
                # 文字变了 → 判定为局部内容更新，保留
                kept_images.append(img_path)
                last_img_path = img_path
                last_text = current_text
                tier3_ocr_keep += 1
                logger.info(
                    f"{progress} ✅ [保留] {filename} | "
                    f"SSIM: {current_ssim:.3f} | "
                    f"文本: {text_sim:.3f} | "
                    f"Tier3-OCR判定新内容 (局部文字更新)"
                )

    # === 导出结果 ===
    logger.info("\n" + "-" * 60)
    logger.info("正在导出保留的图片...")
    for idx, img_path in enumerate(kept_images):
        ext = os.path.splitext(img_path)[1]
        new_name = f"slide_{idx + 1:03d}{ext}"
        dst = os.path.join(output_dir, new_name)
        # 如果原文件还在原位（没有被 move 走），copy 过去
        if os.path.exists(img_path):
            shutil.copy2(img_path, dst)
        else:
            # 文件可能已经被 move 到 dup_dir（不应该发生，但防御性处理）
            logger.warning(f"文件不存在: {img_path}，跳过")

    # === 统计报告 ===
    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 60)
    logger.info("  去重完成 — 统计报告")
    logger.info("=" * 60)
    logger.info(f"总处理图片:     {total} 张")
    logger.info(f"最终保留:       {len(kept_images)} 张")
    logger.info(f"移出重复:       {dup_count} 张")
    logger.info(f"压缩率:         {dup_count / total * 100:.1f}%")
    logger.info("-" * 60)
    logger.info(f"Tier1 绝对重复: {tier1_strict_dup} 张 (SSIM ≥ {strict_ssim})")
    logger.info(f"Tier2 绝对新页: {tier2_new_page} 张 (SSIM < {loose_ssim})")
    logger.info(f"Tier3 OCR重复:  {tier3_ocr_dup} 张 (灰色地带, 文字未变)")
    logger.info(f"Tier3 OCR保留:  {tier3_ocr_keep} 张 (灰色地带, 文字更新)")
    logger.info(f"OCR 介入次数:   {ocr_call_count} 次 (占比 {ocr_call_count / total * 100:.1f}%)")
    logger.info("-" * 60)
    logger.info(f"保留图片目录:   {output_dir}")
    logger.info(f"重复图片目录:   {dup_dir}")
    logger.info(f"总耗时:         {elapsed:.1f}s")
    if total > 0:
        logger.info(f"平均速度:       {elapsed / total:.3f}s/张")
    logger.info("=" * 60)


# ============================================================
#  CLI 入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="文档类视频切片智能去重工具 (SSIM + OCR 组合方案)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python smart_dedup.py -i ./frames -o ./unique_slides

  # 启用 GPU 加速
  python smart_dedup.py -i ./frames -o ./unique_slides --gpu

  # 自定义阈值
  python smart_dedup.py -i ./frames -o ./unique_slides --strict-ssim 0.98 --loose-ssim 0.70 --text-thresh 0.90

  # 纯中文识别（更快）
  python smart_dedup.py -i ./frames -o ./unique_slides --lang ch_sim

参数调优指南:
  --strict-ssim  0.98  绝对重复阈值。翻页带平滑动画可调低至 0.95
  --loose-ssim   0.70  新页面阈值。硬切翻页保持 0.70，柔和过渡可调至 0.60
  --text-thresh  0.90  文本重复阈值。代码演示调低至 0.80，PPT小字变化调高至 0.95
        """,
    )

    parser.add_argument(
        "-i", "--input",
        required=True,
        help="原始切片图片目录",
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="去重后保留图片的输出目录",
    )
    parser.add_argument(
        "--dup-dir",
        default=None,
        help="重复图片存放目录 (默认: <input>/_duplicates)",
    )
    parser.add_argument(
        "--strict-ssim",
        type=float,
        default=0.98,
        help="SSIM 严格阈值，≥此值判定为绝对重复 (默认: 0.98)",
    )
    parser.add_argument(
        "--loose-ssim",
        type=float,
        default=0.70,
        help="SSIM 宽松阈值，<此值判定为绝对新页面 (默认: 0.70)",
    )
    parser.add_argument(
        "--text-thresh",
        type=float,
        default=0.90,
        help="文本相似度阈值，≥此值判定为文字未变 (默认: 0.90)",
    )
    parser.add_argument(
        "--gpu",
        action="store_true",
        default=False,
        help="启用 GPU 加速 (需安装 CUDA + PyTorch，速度提升 10 倍)",
    )
    parser.add_argument(
        "--lang",
        nargs="+",
        default=["ch_sim", "en"],
        help="EasyOCR 识别语言 (默认: ch_sim en。纯中文可用: ch_sim)",
    )
    parser.add_argument(
        "--auto-gpu",
        action="store_true",
        default=False,
        help="自动检测 GPU 并启用 (无需手动指定 --gpu)",
    )

    args = parser.parse_args()

    # 验证输入目录
    if not os.path.isdir(args.input):
        print(f"错误: 输入目录不存在: {args.input}")
        sys.exit(1)

    # 设置重复目录
    dup_dir = args.dup_dir or os.path.join(args.input, "_duplicates")

    # GPU 自动检测
    use_gpu = args.gpu
    if args.auto_gpu and not use_gpu:
        if detect_gpu():
            use_gpu = True
            print("检测到 NVIDIA GPU，已自动启用 GPU 加速")
        else:
            print("未检测到 GPU，使用 CPU 模式")

    # 初始化日志
    log_dir = os.path.join(args.output, "_logs")
    logger = setup_logger(log_dir)

    # 运行去重
    try:
        deduplicate(
            input_dir=args.input,
            output_dir=args.output,
            dup_dir=dup_dir,
            strict_ssim=args.strict_ssim,
            loose_ssim=args.loose_ssim,
            text_thresh=args.text_thresh,
            use_gpu=use_gpu,
            ocr_lang=args.lang,
            logger=logger,
        )
    except KeyboardInterrupt:
        logger.info("\n用户中断，已处理的图片保留在输出目录中。")
        sys.exit(130)
    except Exception as e:
        logger.error(f"运行出错: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
