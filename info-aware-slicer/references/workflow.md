# 完整工作流：视频 → 文档

## 流水线总览

```
视频 (.mp4)
    │
    ▼
[1] info_aware_slicer.py     ← 信息完整性感知切片
    │  输出: 切片图片 + document_chain.json
    │
    ▼
[2] smart_dedup.py (可选)    ← SSIM + OCR 去重
    │  输出: 去重后的切片图片
    │
    ▼
[3] doc_reconstruct.py       ← OCR 提取文本 + 缺失标注
    │  输出: document.md (带图片引用)
```

## 阶段 1：动态切片

```powershell
cd C:\Users\Kerco\WorkBuddy\2026-06-25-22-51-10
.\.venv\Scripts\Activate.ps1

python info_aware_slicer.py `
  --video "<视频路径>.mp4" `
  --output-dir "<切片输出目录>" `
  --sad-threshold 8.0 `
  --template-match-thresh 0.75 `
  --overlap-ratio 0.15 `
  --base-step-sec 0.3 `
  --max-step-sec 1.0
```

输出：
- `frame_XXXXXXXX_XXXX.XXXs.jpg` — 切片图片
- `document_chain.json` — 每张切片的帧位置、PTS 时间、状态标签

### 调参指南

| 问题 | 调整 |
|------|------|
| 切片太多 | 提高 `--sad-threshold` |
| 切片太少、漏内容 | 降低 `--sad-threshold` 和 `--base-step-sec` |
| 连续滚动被误判为翻页 | 降低 `--template-match-thresh` |
| 翻页被误判为连续滚动 | 提高 `--template-match-thresh` |
| 两张切片之间跳了 1 秒+ | 降低 `--max-step-sec`（这是漏帧主因） |
| 需要极度精确（几乎不漏帧） | 参考 `references/params-guide.md` 的"精确模式" |

## 阶段 2：SSIM 去重（可选）

如果切片图中存在大量重复帧，运行去重：

```powershell
python smart_dedup.py `
  -i "<切片输出目录>" `
  -o "<去重结果目录>" `
  --gpu
```

## 阶段 3：文档重建

将切片图片 OCR 提取文本，并标注缺失位置：

```powershell
python doc_reconstruct.py `
  -i "<去重结果目录>" `
  -o "<最终文档路径>.md" `
  --gpu
```

输出：
- `document.md` — 包含图片引用 + OCR 文本 + 缺失警告（⚠️ MISSING_GAP 标记）

## 依赖安装

```powershell
pip install decord opencv-python numpy tqdm imagehash easyocr
```

EasyOCR 首次运行会自动下载模型（~100MB），后续缓存复用。
