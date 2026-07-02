#!/usr/bin/env python3
"""信息完整性感知视频切片器 (Gemini Layer3 + Qwen SAD 融合架构).

核心能力:
    - 基于 Block Matching SAD 的动态采样（快密慢疏）
    - 基于尾首模板匹配的物理断层检测
    - 输出带状态标签的切片图片与 document_chain.json

依赖（已由环境预装）:
    pip install decord opencv-python numpy tqdm
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from decord import VideoReader, cpu
from tqdm import tqdm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


class FrameStatus(Enum):
    """切片帧的状态标签."""

    FIRST_FRAME = "FIRST_FRAME"      # 视频首帧
    CONTINUOUS = "CONTINUOUS"        # 与前一帧存在内容重叠（连续滚动）
    NEW_PAGE = "NEW_PAGE"            # 全新页面 / 硬切翻页
    MISSING_GAP = "MISSING_GAP"      # 物理断层，可能丢失信息


class InfoAwareSlicer:
    """信息完整性感知视频切片器.

    Attributes:
        video_path: 输入视频路径。
        output_dir: 输出目录路径。
        sad_threshold: SAD 运动触发阈值。
        template_match_thresh: 尾首模板匹配相似度阈值。
        overlap_ratio: 取上一帧底部作为模板的高度比例。
        base_step_sec: 基础步长（秒），NEW_PAGE 后默认前进量。
        max_step_sec: 最大步长（秒），低运动时大步跳过。
        still_sad: 静止判定 SAD 阈值，低于此值不保留当前帧且大步跳过。
    """

    def __init__(
        self,
        video_path: str,
        output_dir: str,
        sad_threshold: float = 8.0,
        template_match_thresh: float = 0.75,
        overlap_ratio: float = 0.15,
        base_step_sec: float = 0.3,
        max_step_sec: float = 1.0,
        still_sad: float = 2.0,
    ) -> None:
        self.video_path = str(video_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.sad_threshold = float(sad_threshold)
        self.template_match_thresh = float(template_match_thresh)
        self.overlap_ratio = float(overlap_ratio)
        self.base_step_sec = float(base_step_sec)
        self.max_step_sec = float(max_step_sec)
        self.still_sad = float(still_sad)
        self._validate_thresholds()

        self.vr = VideoReader(self.video_path, ctx=cpu(0))
        self.fps = float(self.vr.get_avg_fps())
        if self.fps <= 0:
            self.fps = 30.0
        self.total_frames = int(len(self.vr))

        self.frame_chain: list[dict] = []

        logger.info(
            "Video ready: %d frames | %.2f FPS | output=%s",
            self.total_frames,
            self.fps,
            self.output_dir,
        )

    def _validate_thresholds(self) -> None:
        """校验用户输入阈值是否合法."""
        if not 0 < self.overlap_ratio <= 0.5:
            raise ValueError("overlap-ratio must be in (0, 0.5]")
        if not 0 < self.template_match_thresh <= 1:
            raise ValueError("template-match-thresh must be in (0, 1]")
        if self.sad_threshold <= 0:
            raise ValueError("sad-threshold must be positive")
        if self.base_step_sec <= 0:
            raise ValueError("base-step-sec must be positive")
        if self.max_step_sec <= 0:
            raise ValueError("max-step-sec must be positive")
        if self.base_step_sec > self.max_step_sec:
            raise ValueError("base-step-sec must not exceed max-step-sec")
        if self.still_sad < 0:
            raise ValueError("still-sad must be non-negative")

    def _calc_block_sad(
        self,
        prev_frame: np.ndarray,
        curr_frame: np.ndarray,
        block_size: int = 16,
    ) -> float:
        """Layer 1: Block Matching SAD 运动检测.

        将两帧按 block_size 网格分块，计算每块的平均 SAD，再取全局均值。
        使用 int16 避免 uint8 溢出。

        Args:
            prev_frame: 前一帧 RGB 图像。
            curr_frame: 当前帧 RGB 图像。
            block_size: 分块大小，默认 16。

        Returns:
            全局平均 SAD（浮点数）。
        """
        h, w = prev_frame.shape[:2]
        h = (h // block_size) * block_size
        w = (w // block_size) * block_size
        if h == 0 or w == 0:
            return 0.0

        prev_gray = cv2.cvtColor(prev_frame[:h, :w], cv2.COLOR_RGB2GRAY).astype(np.int16)
        curr_gray = cv2.cvtColor(curr_frame[:h, :w], cv2.COLOR_RGB2GRAY).astype(np.int16)

        diff = np.abs(prev_gray - curr_gray)
        h_blocks = h // block_size
        w_blocks = w // block_size

        # reshape 为 (h_blocks, block_size, w_blocks, block_size) 后聚合
        block_sads = (
            diff.reshape(h_blocks, block_size, w_blocks, block_size)
            .transpose(0, 2, 1, 3)
            .reshape(h_blocks, w_blocks, block_size * block_size)
            .mean(axis=2)
        )
        return float(block_sads.mean())

    def _check_tail_head_match(
        self,
        prev_frame: np.ndarray,
        curr_frame: np.ndarray,
    ) -> tuple[bool, float]:
        """Layer 3: 尾首模板匹配，并加入 X 轴几何约束。

        取上一帧底部 overlap_ratio 高度的区域作为模板，在当前帧上半部分搜索。
        文档滚动主要为垂直方向，因此要求匹配位置的 X 偏移不超过画面宽度的 5%。

        Args:
            prev_frame: 前一帧 RGB 图像（关键帧）。
            curr_frame: 当前帧 RGB 图像。

        Returns:
            (是否匹配成功, 归一化互相关系数最大值)。
        """
        h, w = prev_frame.shape[:2]
        template_h = int(h * self.overlap_ratio)
        if template_h < 10:
            return False, 0.0

        template = cv2.cvtColor(prev_frame[-template_h:, :], cv2.COLOR_RGB2GRAY)
        search_region = cv2.cvtColor(curr_frame[: h // 2, :], cv2.COLOR_RGB2GRAY)

        if (
            template.shape[0] > search_region.shape[0]
            or template.shape[1] > search_region.shape[1]
        ):
            return False, 0.0

        result = cv2.matchTemplate(search_region, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)

        x_offset = abs(max_loc[0])
        is_valid_geometry = x_offset < (w * 0.05)
        is_matched = (max_val >= self.template_match_thresh) and is_valid_geometry
        return is_matched, float(max_val)

    @staticmethod
    def _safe_imwrite(path: Path, image_bgr: np.ndarray, quality: int = 90) -> None:
        """兼容 CJK 路径的图片写入.

        cv2.imwrite 在 Windows 上处理非 ASCII 路径可能失败，因此使用
        cv2.imencode 编码后通过 open(path, 'wb') 写入字节流。

        Args:
            path: 目标文件路径。
            image_bgr: 待保存的 BGR 图像。
            quality: JPEG 质量，默认 90。
        """
        ext = path.suffix.lower()
        if ext in (".jpg", ".jpeg"):
            success, buffer = cv2.imencode(
                ".jpg", image_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality]
            )
        elif ext == ".png":
            success, buffer = cv2.imencode(".png", image_bgr)
        else:
            success, buffer = cv2.imencode(
                ".jpg", image_bgr, [cv2.IMWRITE_JPEG_QUALITY, quality]
            )

        if not success:
            raise RuntimeError(f"Failed to encode image: {path}")

        with open(path, "wb") as f:
            f.write(buffer.tobytes())

    def run(self) -> None:
        """执行切片主流程."""
        logger.info("Start info-aware slicing...")

        # Layer 2: 基于帧率的自适应步长（可通过 CLI 调整）
        base_step = max(1, int(round(self.fps * self.base_step_sec)))
        min_step = max(1, int(round(self.fps * 0.05)))      # 0.05 秒（高速滚动）
        max_step = max(1, int(round(self.fps * self.max_step_sec)))

        current_idx = 0
        prev_frame: Optional[np.ndarray] = None
        prev_status = FrameStatus.FIRST_FRAME
        sad = 0.0

        pbar = tqdm(
            total=self.total_frames,
            desc="Slicing",
            unit="frame",
            ncols=80,
        )

        while current_idx < self.total_frames:
            frame = self.vr[current_idx].asnumpy()
            pts_sec = current_idx / self.fps
            status = FrameStatus.FIRST_FRAME
            match_conf = 0.0

            if prev_frame is not None:
                sad = self._calc_block_sad(prev_frame, frame)

                # 几乎完全静止 -> 大步长跳过，不保留该帧
                if sad < self.still_sad:
                    step = min(max_step, self.total_frames - current_idx)
                    current_idx += step
                    pbar.update(step)
                    continue

                is_continuous, match_conf = self._check_tail_head_match(
                    prev_frame, frame
                )
                if is_continuous:
                    status = FrameStatus.CONTINUOUS
                elif sad > self.sad_threshold * 3 and match_conf < 0.3:
                    status = FrameStatus.MISSING_GAP
                else:
                    status = FrameStatus.NEW_PAGE

            # 保存切片图片
            filename = f"frame_{current_idx:08d}_{pts_sec:08.3f}s.jpg"
            out_path = self.output_dir / filename
            img_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            self._safe_imwrite(out_path, img_bgr, quality=90)

            # 记录到 Document Chain
            self.frame_chain.append(
                {
                    "filename": filename,
                    "pts_sec": round(pts_sec, 3),
                    "frame_idx": current_idx,
                    "status": status.value,
                    "match_confidence": round(match_conf, 4),
                    "prev_status": prev_status.value if prev_frame is not None else None,
                }
            )

            prev_frame = frame
            prev_status = status

            # Layer 2: 根据当前状态动态调整下一步步长
            if status == FrameStatus.FIRST_FRAME:
                step = base_step
            elif status in (FrameStatus.CONTINUOUS, FrameStatus.MISSING_GAP):
                step = min_step
            elif sad < self.sad_threshold:
                step = max_step
            else:
                step = base_step

            step = min(step, self.total_frames - current_idx)
            current_idx += step
            pbar.update(step)

        pbar.close()

        # 保存 document_chain.json
        chain_path = self.output_dir / "document_chain.json"
        with open(chain_path, "w", encoding="utf-8") as f:
            json.dump(self.frame_chain, f, ensure_ascii=False, indent=2)

        # 统计摘要
        status_counts: dict[str, int] = {}
        for item in self.frame_chain:
            s = item["status"]
            status_counts[s] = status_counts.get(s, 0) + 1

        logger.info("Slicing complete! Total saved frames: %d", len(self.frame_chain))
        for status_name, count in status_counts.items():
            logger.info("  %s: %d", status_name, count)
        logger.info("Document Chain saved to: %s", chain_path)


def parse_args() -> argparse.Namespace:
    """解析命令行参数."""
    parser = argparse.ArgumentParser(
        description="信息完整性感知视频切片器：动态采样 + 物理断层检测。"
    )
    parser.add_argument(
        "--video",
        required=True,
        help="输入视频文件路径。",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="输出目录路径（切片图片与 document_chain.json 保存于此）。",
    )
    parser.add_argument(
        "--sad-threshold",
        type=float,
        default=8.0,
        help="SAD 运动触发阈值（默认 8.0）。",
    )
    parser.add_argument(
        "--template-match-thresh",
        type=float,
        default=0.75,
        help="尾首模板匹配相似度阈值（默认 0.75）。",
    )
    parser.add_argument(
        "--overlap-ratio",
        type=float,
        default=0.15,
        help="取上一帧底部作为模板的高度比例（默认 0.15）。",
    )
    parser.add_argument(
        "--base-step-sec",
        type=float,
        default=0.3,
        help="基础步长/秒，NEW_PAGE 后默认前进量（默认 0.3，原硬编码 0.5）。",
    )
    parser.add_argument(
        "--max-step-sec",
        type=float,
        default=1.0,
        help="最大步长/秒，低运动/静止时大步跳过（默认 1.0，原硬编码 2.0）。",
    )
    parser.add_argument(
        "--still-sad",
        type=float,
        default=2.0,
        help="静止判定 SAD，低于此值跳过当前帧（默认 2.0）。",
    )
    return parser.parse_args()


def main() -> None:
    """CLI 入口."""
    args = parse_args()

    if not Path(args.video).exists():
        logger.error("Video file not found: %s", args.video)
        sys.exit(1)

    slicer = InfoAwareSlicer(
        video_path=args.video,
        output_dir=args.output_dir,
        sad_threshold=args.sad_threshold,
        template_match_thresh=args.template_match_thresh,
        overlap_ratio=args.overlap_ratio,
        base_step_sec=args.base_step_sec,
        max_step_sec=args.max_step_sec,
        still_sad=args.still_sad,
    )
    slicer.run()


if __name__ == "__main__":
    main()
