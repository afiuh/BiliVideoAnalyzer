import os

# 配置路径
AUDIO_DIR = "./data/audios"
SUBTITLE_DIR = "./data/subtitles"

def count_files(directory):
    """统计目录中的文件数量"""
    if not os.path.exists(directory):
        return 0
    return len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])

def delete_files_in_dir(directory, description):
    """删除目录中的所有文件（保留空目录），不询问"""
    if not os.path.exists(directory):
        print(f"目录 {directory} 不存在，跳过。")
        return
    files = os.listdir(directory)
    if not files:
        print(f"{description}目录为空，无需清理。")
        return
    print(f"正在删除 {description} 目录下的 {len(files)} 个文件...")
    for f in files:
        file_path = os.path.join(directory, f)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"已删除: {f}")
        except Exception as e:
            print(f"删除 {file_path} 时出错: {e}")
    print(f"{description}目录清理完成。\n")

def main():
    print("=== 清理脚本 ===")
    print("此脚本将删除音频和字幕文件，以释放磁盘空间。")
    print("最终生成的 Excel 报告和 Word 文档不会被删除。\n")

    audio_count = count_files(AUDIO_DIR)
    sub_count = count_files(SUBTITLE_DIR)

    print(f"音频目录 ({AUDIO_DIR}) 中有 {audio_count} 个文件")
    print(f"字幕目录 ({SUBTITLE_DIR}) 中有 {sub_count} 个文件\n")

    if audio_count == 0 and sub_count == 0:
        print("没有需要清理的文件。")
        return

    print("请选择要清理的内容：")
    print("1. 仅清理音频文件")
    print("2. 仅清理字幕文件")
    print("3. 同时清理音频和字幕文件")
    print("0. 取消")
    choice = input("请输入数字 (0/1/2/3): ").strip()

    if choice == '1':
        delete_files_in_dir(AUDIO_DIR, "音频")
    elif choice == '2':
        delete_files_in_dir(SUBTITLE_DIR, "字幕")
    elif choice == '3':
        delete_files_in_dir(AUDIO_DIR, "音频")
        delete_files_in_dir(SUBTITLE_DIR, "字幕")
    else:
        print("操作已取消。")

if __name__ == "__main__":
    main()