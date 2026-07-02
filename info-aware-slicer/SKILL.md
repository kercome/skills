---
name: info-aware-slicer
description: 信息完整性感知视频切片器。适用于文档或网页录屏视频的动态切片场景。基于 Block Matching SAD 自适应采样和尾首模板匹配断层检测。输出带 PTS 时间戳的切片图片和 document_chain.json 状态链。当用户需要将视频切片为图片、从录屏视频中提取文档帧、或有上传视频需要切片处理时使用此 skill。
agent_created: true
---

# 信息完整性感知视频切片器

将文档/网页录屏视频智能切片为图片，通过运动感知自适应步长避免漏帧。

## 触发条件

- 用户提到"视频切片"、"录屏切片"、"视频转图片"、"提取文档帧"
- 用户上传了一段 `.mp4` 视频并要求切片或提取内容
- 用户说"把这个视频每一页切出来"
- 用户提到 `info_aware_slicer.py`、`document_chain.json`

## 完整流程

```
用户上传视频.mp4
     │
     ▼
Step 1: 动态切片（info_aware_slicer.py）
     输出: 切片图片 + document_chain.json
     │
     ▼
Step 2: SSIM+OCR 去重（smart_dedup.py，可选）
     输出: 去重后的切片图片
     │
     ▼
Step 3: OCR 文本重建（doc_reconstruct.py，可选）
     输出: document.md（图片引用 + 文本 + 缺失标注）
```

## Step 1: 动态切片

### 快速启动

向用户确认：
1. 视频文件路径
2. 输出目录（建议默认 `H:\AAA\切片` 或视频同目录下新建 `_slices`）

如果用户没有特殊参数需求，使用默认参数即可：

```powershell
cd C:\Users\Kerco\WorkBuddy\2026-06-25-22-51-10
.\.venv\Scripts\Activate.ps1

python scripts/info_aware_slicer.py `
  --video "<用户视频路径>" `
  --output-dir "<输出目录>"
```

### 调参决策

当用户反馈切片结果有问题时，参考以下决策树：

| 问题 | 诊断 | 调整 |
|------|------|------|
| "两张图中间跳了 1 秒+" | `--max-step-sec` 太大 | 降到 0.5 ~ 0.8 |
| "切了太多张，很多重复" | `--sad-threshold` 太低 | 提高到 12.0 ~ 15.0 |
| "漏掉了一页内容" | `--sad-threshold` 太高或 `--max-step-sec` 太大 | 降低两者 |
| "连续滚动被切成多张" | `--template-match-thresh` 太高 | 降到 0.65 ~ 0.70 |
| "翻页被当成连续滚动" | `--template-match-thresh` 太低 | 提高到 0.80 ~ 0.85 |

完整的参数调优参考 `references/params-guide.md`。

### 判断本次切片质量

切片完成后，读取 `<输出目录>/document_chain.json`，统计 status 分布并告知用户：

- `FIRST_FRAME`: 永远是 1 个
- `CONTINUOUS`: 连续滚动帧数。> 50% 但用户说"这明明是翻页" → 提高 `--template-match-thresh`
- `NEW_PAGE`: 硬切换/翻页帧数。文档视频以此为主是正常的
- `MISSING_GAP`: 可能丢帧数。> 10% → 需要调整步长或阈值

同时抽查前后相邻帧的文件名，计算帧间隔。如果相邻帧的帧号差 > `fps × max-step-sec + 10`，说明有异常跳跃，建议减小 `--max-step-sec`。

## Step 2: SSIM + OCR 去重（按需）

如果切片后发现重复帧较多，可以执行 SSIM 去重。但通常 Step 1 已经做到较好的帧间区分，此步骤可选。

详见 `references/workflow.md` 中的去重章节。

## Step 3: OCR 文档重建（按需）

将切片图片转换为带文本的 Markdown 文档，并标注缺失位置。

```powershell
python scripts/doc_reconstruct.py `
  -i "<切片图片目录>" `
  -o "<输出路径>.md" `
  --gpu
```

## 输出解读

### document_chain.json 字段

| 字段 | 含义 |
|------|------|
| `filename` | 切片图片文件名（含帧序号和时间戳） |
| `pts_sec` | 该帧在视频中的时间位置（秒） |
| `frame_idx` | 该帧在视频中的帧序号 |
| `status` | FIRST_FRAME / CONTINUOUS / NEW_PAGE / MISSING_GAP |
| `match_confidence` | 尾首模板匹配的相关系数（CONTINUOUS 时接近 1.0） |
| `prev_status` | 上一帧的状态 |

### FrameStatus 含义

| 状态 | 含义 | 人工判断 |
|------|------|---------|
| `FIRST_FRAME` | 视频首帧 | — |
| `CONTINUOUS` | 当前帧顶部能匹配上一帧底部 → 连续滚动 | 滚动中 |
| `NEW_PAGE` | 尾首匹配失败，但运动幅度正常 → 翻页或新内容 | 翻页中 |
| `MISSING_GAP` | 尾首匹配失败 + SAD 极高 → 可能丢帧 | ⚠️ 内容缺失！ |

## 依赖

脚本运行环境：
- Python 3.10+
- decord, opencv-python, numpy, tqdm（切片必需）
- imagehash（可选，去重用）
- easyocr（可选，OCR 文本重建用）

安装指令：
```powershell
pip install decord opencv-python numpy tqdm imagehash easyocr
```
