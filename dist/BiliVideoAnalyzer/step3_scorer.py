import os
import json
import re
import time
import jieba
import subprocess
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from config import (
    VIRTUAL_WORDS, LOGIC_WORDS, EXCLUDE_PHRASES,
    SCORE_WEIGHTS, DECISION_THRESHOLDS
)

SUBTITLE_DIR = "./data/subtitles"
EXCEL_OUTPUT = "./data/video_scores.xlsx"
EXCEL_BACKUP_DIR = "./data/excel_backups"  # 备份文件夹
def force_close_office_apps():
    """强制关闭所有 Excel 和 Word 进程（Windows）"""
    try:
        # 关闭 Excel
        subprocess.run('taskkill /f /im excel.exe', shell=True, capture_output=True)
        # 关闭 Word
        subprocess.run('taskkill /f /im winword.exe', shell=True, capture_output=True)
        print("已尝试关闭 Excel 和 Word 进程。")
    except Exception as e:
        print(f"关闭进程时出错: {e}")


class VideoScorer:
    def __init__(self):
        self.virtual_words = set(VIRTUAL_WORDS)
        self.logic_words = set(LOGIC_WORDS)
        self.exclude_phrases = set(EXCLUDE_PHRASES)
        self.weights = SCORE_WEIGHTS
        self.thresholds = DECISION_THRESHOLDS

    def calculate_basic_metrics(self, text):
        """计算所有基础指标，返回字典"""
        total_chars = len(text)
        if total_chars == 0:
            return {
                'density_virtual': 0.0,
                'density_logic': 0.0,
                'density_question': 0.0,
                'density_firstperson': 0.0,
                'vocab_richness': 0.0,
                'density_propernoun': 0.0,
                'length_penalty': 0.0,
                'total_chars': 0
            }

        # 1. 虚词密度
        virtual_count = sum(text.count(word) for word in self.virtual_words)
        density_virtual = virtual_count / total_chars * 1000

        # 2. 逻辑连词密度
        logic_count = sum(text.count(word) for word in self.logic_words)
        density_logic = logic_count / total_chars * 1000

        # 3. 设问密度
        density_question = text.count('？') / total_chars * 1000

        # 4. 第一人称密度
        density_firstperson = text.count('我') / total_chars * 1000

        # 5. 词汇丰富度（分词后去重）
        words = jieba.lcut(text)
        filtered_words = [w for w in words if re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', w)]
        total_words = len(filtered_words)
        unique_words = len(set(filtered_words))
        vocab_richness = unique_words / total_words if total_words > 0 else 0

        # 6. 专有名词密度
        candidates = re.findall(r'[\u4e00-\u9fa5]{2,}', text)
        proper_candidates = [c for c in candidates if c not in self.exclude_phrases]
        unique_proper = len(set(proper_candidates))
        density_propernoun = unique_proper / total_chars * 1000

        # 7. 文本长度惩罚系数
        length_penalty = min(1.0, total_chars / 1000)

        return {
            'density_virtual': density_virtual,
            'density_logic': density_logic,
            'density_question': density_question,
            'density_firstperson': density_firstperson,
            'vocab_richness': vocab_richness,
            'density_propernoun': density_propernoun,
            'length_penalty': length_penalty,
            'total_chars': total_chars
        }

    def compute_composite_scores(self, metrics):
        """计算三个复合维度分"""
        w = self.weights
        info_score = (
            metrics['density_propernoun'] * w.get('propernoun_weight', 0.8) +
            metrics['vocab_richness'] * w.get('richness_weight', 100)
        ) * metrics['length_penalty']

        rational_score = (
            metrics['density_question'] * w.get('question_weight', 2.0) +
            metrics['density_logic'] * w.get('logic_weight', 0.5)
        )

        experience_score = (
            metrics['density_firstperson'] * w.get('firstperson_weight', 10)
        )

        return {
            'info_score': round(info_score, 2),
            'rational_score': round(rational_score, 2),
            'experience_score': round(experience_score, 2)
        }

    def decide_rating(self, scores, metrics):
        """决策树判定最终档次"""
        th = self.thresholds
        info = scores['info_score']
        rational = scores['rational_score']
        experience = scores['experience_score']
        chars = metrics['total_chars']

        # 先计算临时评级
        if (rational >= th.get('S_rational_min', 5.0) and
            info >= th.get('S_info_min', 50) and
            chars >= th.get('S_chars_min', 12000)):
            temp_rating = 'S'
        elif experience >= th.get('A_experience_min', 30):
            temp_rating = 'A(体验)'
        elif (rational >= th.get('A_rational_min', 3.0) and
              info >= th.get('A_info_min', 40)):
            temp_rating = 'A(分析)'
        elif info >= th.get('B_info_high', 50):
            temp_rating = 'B(资讯)'
        elif info >= th.get('B_info_low', 30):
            temp_rating = 'B(一般)'
        elif info >= th.get('C_info_min', 15):
            temp_rating = 'C'
        else:
            temp_rating = 'D'

        # 字数限制调整
        if chars < 800:
            return 'D'
        elif chars < 1500:
            if temp_rating in ['S', 'A(体验)', 'A(分析)', 'B(资讯)', 'B(一般)']:
                return 'C'
            else:
                return temp_rating
        else:
            return temp_rating

    def score_video(self, text):
        metrics = self.calculate_basic_metrics(text)
        composite = self.compute_composite_scores(metrics)
        rating = self.decide_rating(composite, metrics)
        return metrics, composite, rating


def main():
    force_close_office_apps()  # 在开始前关闭 Office 进程
    if not os.path.exists(SUBTITLE_DIR):
        print(f"错误：字幕文件夹 {SUBTITLE_DIR} 不存在，请先运行 step2。")
        return

    # 获取所有 .txt 文件
    txt_files = [f for f in os.listdir(SUBTITLE_DIR) if f.endswith('.txt')]
    if not txt_files:
        print("字幕文件夹中没有 .txt 文件，退出。")
        return

    print(f"找到 {len(txt_files)} 个字幕文件，开始评分...")

    # 准备 Excel（去掉标题列）
    wb = Workbook()
    ws = wb.active
    ws.title = "评分结果"
    headers = ["BV号", "信息密度分", "理性思辨分", "体验思辨分", "最终评级"]
    ws.append(headers)
    ws.column_dimensions['A'].width = 15
    for col in ['B','C','D','E']:
        ws.column_dimensions[col].width = 12

    scorer = VideoScorer()
    processed = 0

    for filename in txt_files:
        bvid = filename.replace('.txt', '')
        txt_path = os.path.join(SUBTITLE_DIR, filename)
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception as e:
            print(f"读取文件 {filename} 失败: {e}")
            continue

        metrics, composite, rating = scorer.score_video(text)
        ws.append([
            bvid,
            composite['info_score'],
            composite['rational_score'],
            composite['experience_score'],
            rating
        ])
        processed += 1
        print(f"已评分 ({processed}/{len(txt_files)})：{bvid} -> {rating}")

    # 保存新文件
    wb.save(EXCEL_OUTPUT)
    print(f"评分完成，结果已保存到 {EXCEL_OUTPUT}")

if __name__ == "__main__":
    main()