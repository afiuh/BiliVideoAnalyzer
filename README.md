


#  B站视频质量自动分析工具

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个自动化分析B站视频质量的工具，包含爬取视频、音频转文字、多维评分、AI审核等功能。

## ✨ 功能特性

- **视频爬取**：根据关键词搜索B站视频，获取BV号、标题等信息。
- **语音识别**：自动下载视频音频，使用 `faster-whisper` 转写为文字（支持GPU加速）。
- **质量评分**：基于文案的虚词密度、逻辑连词、专有名词等指标，计算信息密度分、理性思辨分、体验思辨分，并输出 S/A/B/C/D 评级。
- **AI深度审核**：对 S/A 档视频调用 DeepSeek API 进行内容分析，生成详细的评价报告（Word文档）。
- **立场检测**：自动识别恶意贬低、阴阳怪气等内容，并生成批判文本。
- **结果汇总**：生成 Excel 报告，包含所有视频的评分和评级，并为 S/A 档视频提供可点击的超链接打开 Word 文档。

## 🛠️ 使用教程

### 环境配置要求
- Python 3.11 ～ 3.12（作者用的3.12）
- NVIDIA GPU + CUDA 12.x（用于语音识别）
下载网址https://developer.nvidia.com/cuda-downloads

### 安装步骤
1.下载语音识别模型 faster-whisper-small：
https://hf-mirror.com/guillaumekln/faster-whisper-small
   将模型文件夹放在任意位置，后续通过配置指定路径。

2.安装 ffmpeg：
   - Windows：下载 [ffmpeg](https://ffmpeg.org/download.html) 并将 `ffmpeg.exe` 放在项目根目录。
### 使用步骤
1.下载release里的文件，解压

2.运行set.bat(帮你检测并下载必要的运行库)，

3.configure.bat(帮你把关键信息改到脚本里)
填写必要信息：
   ```python
   # DeepSeek API 密钥（必填）
   DEEPSEEK_API_KEY = "sk-你的密钥"

   # 语音识别模型路径（必填，指向 faster-whisper 模型文件夹）
   MODEL_PATH = r"D:/models/faster-whisper-small"


   ```
4.运行crawler_config.bat，设置爬虫功能，建议一开始设为测试模式，
只爬取少量视频看看整个过程能否跑通

5.运行start.bat

## 📊 评分体系说明

### 基础指标
- 虚词密度、逻辑连词密度、设问密度、第一人称密度、词汇丰富度、专有名词密度、文本长度惩罚系数。

### 复合维度
- **信息密度分**：专有名词密度 × 0.8 + 词汇丰富度 × 100，再乘以长度惩罚。
- **理性思辨分**：设问密度 × 2.0 + 逻辑连词密度 × 0.5。
- **体验思辨分**：第一人称密度 × 10。

### 评级决策
| 评级 | 条件 |
|------|------|
| S | 理性分≥5.0 且 信息分≥50 且 总字符≥12000 |
| A(体验) | 体验分≥30 |
| A(分析) | 理性分≥3.0 且 信息分≥40 |
| B(资讯) | 信息分≥50 |
| B(一般) | 信息分≥30 |
| C | 信息分≥15 |
| D | 信息分<15 |

字数不足 800 的视频直接归为 D，不足 1500 的高分视频降至 C。

## ⚠️ 注意事项

1. **API 密钥安全**：`config.py`里如果有真实密钥，就不要公开到公共仓库里了
2. **B站爬虫**：请合理控制爬取频率（脚本已默认设置延时），遵守 B站 用户协议，勿用于商业或大规模抓取，每次最多只能爬300个视频
3. **语音识别模型**：模型文件较大，请自行下载，并通过配置指定路径。
4. **CUDA 环境**：如需 GPU 加速，确保已安装 CUDA 12.x 及 cuDNN，并正确设置 `DEVICE = "cuda"`。
5. **文件占用**：运行前请关闭 Excel 和 Word，否则可能导致写入失败。


## 🤝 贡献

欢迎提交 Issue 或 Pull Request。

## 📧 联系
本人邮箱：3458742916@qq.com

如有问题，可在此仓库提交 Issue。
