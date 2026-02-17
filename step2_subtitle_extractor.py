import os
import json
import subprocess
import time
import logging
import sys
import traceback
import multiprocessing
from faster_whisper import WhisperModel
from config import SUBTITLE_DIR, AUDIO_DIR, MODEL_PATH, DEVICE, COMPUTE_TYPE

# 配置日志记录到文件
logging.basicConfig(
    filename='step2_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# 添加 CUDA 路径
cuda_bin_path = r"C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.0\bin"
os.environ['PATH'] = cuda_bin_path + os.pathsep + os.environ.get('PATH', '')

# ==================== 配置 ====================
MAX_VIDEOS = 300  # 最多处理视频数
# =============================================

def process_single_video(bvid, title):
    """处理单个视频的函数，将在子进程中运行"""
    try:
        print(f"子进程 {os.getpid()} 开始处理视频 {bvid}...")
        sys.stdout.flush()

        # 下载音频（如果不存在）
        audio_file = download_audio(bvid, AUDIO_DIR)
        if not audio_file:
            return False

        # 语音识别
        transcribe_audio(audio_file, bvid, SUBTITLE_DIR)
        return True
    except Exception as e:
        print(f"子进程处理视频 {bvid} 时出错: {e}")
        traceback.print_exc()
        return False

def download_audio(bvid, save_dir):
    url = f"https://www.bilibili.com/video/{bvid}"
    audio_path = os.path.join(save_dir, f"{bvid}.mp3")

    if os.path.exists(audio_path):
        print(f"  音频已存在: {audio_path}")
        return audio_path

    print(f"  正在下载音频: {url}")
    ffmpeg_location = r"C:\Users\c3458\Desktop\世界\学习\重要学习\计算机\b站视频测试\ffmpeg-2026-02-09-git-9bfa1635ae-essentials_build\bin\ffmpeg.exe"
    cmd = [
        "yt-dlp",
        "-x", "--audio-format", "mp3",
        "--ffmpeg-location", ffmpeg_location,
        "-o", audio_path,
        url
    ]
    try:
        # 添加 timeout=600 秒（10分钟）
        result = subprocess.run(cmd, check=True, capture_output=True, text=True,
                                encoding='utf-8', timeout=600)
        print(f"  音频下载完成: {audio_path}")
        return audio_path
    except subprocess.TimeoutExpired:
        print(f"  音频下载超时（超过10分钟），跳过视频 {bvid}")
        return None
    except subprocess.CalledProcessError as e:
        print(f"  音频下载失败: {e.stderr}")
        return None
def transcribe_audio(audio_path, bvid, save_dir):
    print(f"  开始语音识别（GPU）...")
    sys.stdout.flush()
    # 注意：每个子进程都会独立加载模型，这可能会增加内存占用，但可以隔离崩溃
    model = WhisperModel(MODEL_PATH, device=DEVICE, compute_type=COMPUTE_TYPE)
    segments, info = model.transcribe(audio_path, beam_size=5)
    transcript = " ".join([segment.text for segment in segments])
    print(f"  识别完成，时长: {info.duration:.2f}秒")
    sys.stdout.flush()
    txt_path = os.path.join(save_dir, f"{bvid}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(transcript)
    print(f"  字幕已保存: {txt_path}")
    sys.stdout.flush()
    return transcript

def main():
    input_file = "./data/video_urls.json"
    if not os.path.exists(input_file):
        print(f"错误：找不到 {input_file}，请先运行爬虫脚本。")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        videos = json.load(f)

    os.makedirs(SUBTITLE_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)

    processed = 0   # 仅用于统计成功数，不用于限制循环
    for video in videos:
        bvid = video.get('bvid')
        if not bvid:
            continue

        print(f"\n处理视频 {bvid}...")
        audio_file = download_audio(bvid, AUDIO_DIR)
        if not audio_file:
            continue

        try:
            transcribe_audio(audio_file, bvid, SUBTITLE_DIR)
            processed += 1
        except Exception as e:
            print(f"  语音识别出错: {e}")

        print(f"\n处理完成，共成功处理 {processed} 个视频，字幕文件保存在 {SUBTITLE_DIR}，音频文件保存在 {AUDIO_DIR}")
        sys.stdout.flush()
        time.sleep(3)  # 等待底层资源释放

if __name__ == "__main__":
    # 必须使用 spawn 方式启动进程，避免 Windows 上的问题
    multiprocessing.set_start_method('spawn', force=True)
    try:
        logging.info("主进程开始运行")
        main()
        logging.info("主进程正常结束")
    except Exception as e:
        logging.exception("主进程发生未捕获异常")
        print("="*60)
        print("❌ 主进程发生未捕获异常，详情见 step2_debug.log")
        traceback.print_exc()
        print("="*60)
    finally:
        sys.exit(0)