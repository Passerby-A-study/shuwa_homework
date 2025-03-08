import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
import time
from random import randint
max_posts=20 #爬取帖子的最大数目，数目不够时应该是这个最大数目没到达这个
# 替换成你的Cookie
yourUser_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
yourcookie = 'SCF=ArVImN-rAa93jAX7-lP8kOsuGIeGDyRt3JbNyr-b3Kkql-yQ0LHDcV_RR9uH8pe-dJoW_-jqio1nh3CKNlRchzc.; SINAGLOBAL=2811722820605.9.1734250707227; UOR=,,origin.eqing.tech; ALF=1737784441; SUB=_2A25KaJ8pDeRhGeFH71cT9izIzDWIHXVpB57hrDV8PUJbkNANLXbXkW1NeyaIfAsuWXLdpycS9G_e0Lw1mpIXN6D1; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhNReiNgkPP3XWsl.NobBan5JpX5KMhUgL.FoM4Sh-ESozXS0.2dJLoIpYLxKnLBoMLB-qLxKBLB.2LB.2LxKML1KBLBoiW-8xq; XSRF-TOKEN=Kb6AqWUTVGqhVAv2HX28xwuz; _s_tentry=weibo.com; Apache=2662981918649.887.1735192707281; ULV=1735192707311:3:3:1:2662981918649.887.1735192707281:1734531090221; WBPSESS=VcS33kpB4y4rVzdQg8AvDfskifIc_2uxgDMSAtmzoWijfbgvWPjsULjF4Zj1i4v4iiZ4uOmXO2fIKKqbAbcKWoyQBVrteLw_L4b0TEltVze7aY35ZbOLOkiI5ZJ9-osiypKG6XJYw1hi33ltAhO0Cg=='

# 爬取微博搜索页面，提取帖子ID
def get_post_ids(search_url, max_posts=max_posts):
    headers = {
        "User-Agent": yourUser_Agent,
        "Cookie": yourcookie  # 替换为你的有效Cookie
    }

    try:
        # 发送GET请求获取页面内容
        response = requests.get(search_url, headers=headers)
        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}")
            return []

        # 解析HTML内容
        soup = BeautifulSoup(response.text, "lxml")
        post_ids = []

        # 查找所有帖子链接
        for link in soup.select("a[href^='/']"):  # 查找 href 以 '/' 开头的链接
            href = link.get("href")
            match = re.search(r'/(\d+)/([A-Za-z0-9]+)', href)
            if match:
                _, post_id = match.groups()
                if post_id not in post_ids:  # 去重处理
                    post_ids.append(post_id)
            if match == None :
                pass
            else:
                print(match)
            # 控制最大帖子数量
            if len(post_ids) >= max_posts:
                break

        return post_ids

    except Exception as e:
        print(f"发生异常：{e}")
        return []

# 主函数：读取CSV文件，提取帖子ID并分类存储
def process_and_store_links(file_path, output_dir, max_posts=max_posts, request_interval=10):
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path)

        # 检查文件是否包含必要的列
        if 'Search_url' not in df.columns or 'Title' not in df.columns or 'Rank' not in df.columns:
            print("CSV文件中必须包含 'Rank','Search_url' 和 'Title' 列，请检查文件格式。")
            return

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 遍历每个链接并提取帖子ID
        for index, row in df.iterrows():
            search_url = row['Search_url']
            title = row['Title']
            rank=row['Rank']
            print(f"\n正在处理 '{title}' 第 {rank} 个链接: {search_url}")

            # 提取帖子ID
            post_ids = get_post_ids(search_url, max_posts=max_posts)

            # 将帖子ID保存到CSV文件
            if post_ids:
                output_file = os.path.join(output_dir, f"{title}.csv")
                pd.DataFrame(post_ids, columns=["ID"]).to_csv(output_file, index=False)
                print(f"已将 {len(post_ids)} 个帖子ID保存到文件: {output_file}")
            else:
                print(f"'{title}' 未找到帖子ID，跳过保存。")

            # 控制请求间隔，避免被封禁
            time.sleep(5)  # 在 request_interval 的基础上加上一个随机时间差

    except Exception as e:
        print(f"处理文件时发生异常：{e}")

# 测试代码
if __name__ == "__main__":
    input_file = "weibo_hot_search_results.csv"  # 输入CSV文件路径
    output_directory = "weibo_posts_output"      # 输出目录

    # 执行主函数
    process_and_store_links(input_file, output_directory, max_posts=max_posts, request_interval=15)
