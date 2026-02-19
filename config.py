# config.py
# 本文件用于存储所有可调参数，方便统一管理

import os

# ==================== 路径配置 ====================
SUBTITLE_DIR = "./data/subtitles"          # 字幕文件存放目录（音频转写或下载的字幕）
MODEL_PATH = os.getenv("WHISPER_MODEL_PATH", r"C:\useful\models\faster-whisper-small")
# ==================== 音频/字幕目录配置 ====================
AUDIO_DIR = "./data/audios"          # 下载的音频文件存放目录

# ==================== 语音识别设备配置 ====================
DEVICE = "cuda"                       # 可选 "cuda" 或 "cpu"
COMPUTE_TYPE = "float16"               # GPU 推荐 "float16"，CPU 推荐 "int8"
# ==================== B站爬虫配置 ====================
BILIBILI_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Referer": "https://www.bilibili.com"
}

# ==================== 评分体系配置 ====================

# 虚词黑名单（空洞的情绪大词）
VIRTUAL_WORDS = ['本质', '彻底', '绝对', '一定', '真相', '底层逻辑', '降维打击']

# 逻辑连词白名单（体现辩证思考）
LOGIC_WORDS = ['但是', '然而', '另一方面', '尽管如此', '不过']

# 专有名词过滤词（常见的口语/通用词，不计入专有名词）
EXCLUDE_PHRASES = ['什么', '如何', '这个', '可以', '就是', '那个', '我们', '他们', '一个', '没有', '不是']

# 复合维度权重（用于计算信息密度分、理性思辨分、体验思辨分）
SCORE_WEIGHTS = {
    'propernoun_weight': 0.8,      # 专有名词密度权重
    'richness_weight': 100,        # 词汇丰富度权重（因丰富度是0~1小数，乘100与专有名词密度量级匹配）
    'question_weight': 2.0,        # 设问密度权重
    'logic_weight': 0.5,            # 逻辑连词密度权重
    'firstperson_weight': 10        # 第一人称密度权重
}

# 决策树阈值（用于最终评级）
DECISION_THRESHOLDS = {
    # S档要求
    'S_rational_min': 5.0,          # 理性思辨分最低值
    'S_info_min': 50,                # 信息密度分最低值
    'S_chars_min': 12000,            # 最少字符数（防止短片上S档）

    # A档（体验优先）
    'A_experience_min': 30,           # 体验思辨分最低值

    # A档（深度分析）
    'A_rational_min': 3.0,            # 理性思辨分最低值
    'A_info_min': 40,                 # 信息密度分最低值

    # B档（资讯汇编）
    'B_info_high': 50,                 # 信息密度分达到此值即为“资讯汇编”

    # B档（一般内容）
    'B_info_low': 30,                  # 信息密度分低于50但高于等于此值为“一般”

    # C档（轻度水货）
    'C_info_min': 15,                  # 信息密度分低于30但高于等于此值为C档
}

# ==================== DeepSeek API 配置 ====================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-34ee930b3f264152af50f8afcd348388")  # 建议从环境变量读取
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"