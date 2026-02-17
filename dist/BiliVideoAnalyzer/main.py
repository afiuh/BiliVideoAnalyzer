import subprocess
import sys
import os

# 步骤列表（按执行顺序）
STEPS = [
    ("step1_crawler.py", "爬取视频列表"),
    ("step2_subtitle_extractor.py", "提取字幕（音频转文字）"),
    ("step3_scorer.py", "评分与评级，生成 Excel"),
    ("step4_deepseek_review.py", "AI 审核（仅 S/A 档），生成 Word 文档")
]

def run_step_normal(script, description):
    """普通步骤，使用 run 方式（不实时统计）"""
    print(f"\n{'='*60}")
    print(f"开始执行：{description}")
    print(f"脚本文件：{script}")
    print('='*60)

    result = subprocess.run(
        [sys.executable, script],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    if result.stdout:
        print("\n--- 脚本输出 ---")
        print(result.stdout)

    if result.returncode != 0:
        print(f"\n❌ 步骤执行失败：{description}")
        if result.stderr:
            print("--- 错误信息 ---")
            print(result.stderr)
        sys.exit(1)
    else:
        print(f"\n✅ 步骤完成：{description}")

def run_step_with_stats(script, description):
    """运行 step2，实时统计下载和识别数量"""
    print(f"\n{'='*60}")
    print(f"开始执行：{description}")
    print(f"脚本文件：{script}")
    print('='*60)

    # 初始化统计变量
    downloaded = 0
    transcribed = 0

    # 启动子进程，实时捕获输出
    process = subprocess.Popen(
        [sys.executable, script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1  # 行缓冲
    )

    # 实时读取输出并统计
    for line in iter(process.stdout.readline, ''):
        if not line:
            break
        line = line.strip()
        if not line:
            continue
        print(line)
        if "音频下载完成" in line:
            downloaded += 1
        if "字幕已保存" in line:
            transcribed += 1

    # 读取剩余输出
    for line in process.stdout:
        line = line.strip()
        if line:
            print(line)

    process.wait()

    # 读取错误输出
    stderr = process.stderr.read()
    if stderr:
        print("--- 错误信息 ---")
        print(stderr)

    # 输出最终统计
    print(f"最终统计：已下载 {downloaded} 个音频，已识别 {transcribed} 个视频")

    print(f"step2 退出码: {process.returncode}")
    if process.returncode != 0:
        if transcribed > 0 or downloaded > 0:
            print(f"\n⚠️  步骤 {description} 底层退出码 {process.returncode}，但已成功处理 {transcribed} 个视频，将继续执行。")
        else:
            print(f"\n❌ 步骤执行失败：{description}")
            sys.exit(1)
    else:
        print(f"\n✅ 步骤完成：{description}")

def check_config():
    if not os.path.exists("config.py"):
        print("⚠️  警告：未找到 config.py 文件，请确保已创建并配置。")
        print("   如果缺少该文件，后续步骤可能失败。")

def main():
    print("开始执行 B 站视频质量自动化审核全流程")
    print("="*60)

    check_config()
    os.makedirs("./data", exist_ok=True)

    for script, desc in STEPS:
        if not os.path.exists(script):
            print(f"⚠️  跳过：{script} 不存在")
            continue
        if script == "step2_subtitle_extractor.py":
            run_step_with_stats(script, desc)
        else:
            run_step_normal(script, desc)

    print("\n" + "="*60)
    print("🎉 全流程执行完毕！最终结果：")
    print("   - Excel 报告：./data/video_scores.xlsx")
    print("   - Word 评价文件：./data/word_reviews/")
    print("   - 字幕文件：./data/subtitles/")
    print("="*60)

if __name__ == "__main__":
    main()