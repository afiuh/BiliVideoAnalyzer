import json
import os
from bilibili_api import search, sync
from bilibili_api.search import SearchObjectType

# ==================== 配置 ====================
SEARCH_KEYWORDS = ["深度", "体系", "权力"]
NORMAL_PAGES = 2               # 非测试模式下的默认页数
MAX_PAGES_PER_KEYWORD = NORMAL_PAGES
TEST_MODE = False                # True 表示测试模式，只爬取少量视频
if TEST_MODE:
    MAX_VIDEOS_TOTAL = 2         # 测试模式总视频数上限
    MAX_PAGES_PER_KEYWORD = 1    # 测试模式每个关键词只爬1页
# =============================================

async def search_videos(keyword, page):
    """异步搜索视频，返回视频信息列表"""
    try:
        result = await search.search_by_type(
            keyword=keyword,
            search_type=SearchObjectType.VIDEO,
            page=page
        )
        videos = []
        for item in result['result']:
            videos.append({
                'title': item['title'],
                'bvid': item['bvid'],
                'url': f"https://www.bilibili.com/video/{item['bvid']}",
                'author': item['author']
            })
        return videos
    except Exception as e:
        print(f"  搜索出错: {e}")
        return []

def main():
    all_videos = []
    seen_bvids = set()
    for keyword in SEARCH_KEYWORDS:
        print(f"\n开始爬取关键词 '{keyword}' 的视频...")
        for page in range(1, MAX_PAGES_PER_KEYWORD + 1):
            print(f"  正在爬取第 {page} 页...")
            videos = sync(search_videos(keyword, page))
            if not videos:
                print(f"  第 {page} 页无有效数据，停止当前关键词。")
                break
            for v in videos:
                if v['bvid'] not in seen_bvids:
                    seen_bvids.add(v['bvid'])
                    all_videos.append(v)
                    if TEST_MODE and len(all_videos) >= MAX_VIDEOS_TOTAL:
                        break
            if TEST_MODE and len(all_videos) >= MAX_VIDEOS_TOTAL:
                break
        if TEST_MODE and len(all_videos) >= MAX_VIDEOS_TOTAL:
            break

    os.makedirs("./data", exist_ok=True)
    output_path = "./data/video_urls.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_videos, f, ensure_ascii=False, indent=2)
    print(f"\n爬取完成！共获得 {len(all_videos)} 个去重后的视频，已保存到 {output_path}")

if __name__ == "__main__":
    main()