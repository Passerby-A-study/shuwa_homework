import requests
from bs4 import BeautifulSoup
import csv
import time
import random

num_results = 6  # 热搜前几名，一般来说有53还是53名


# 获取微博热搜榜
def get_weibo_hot_search(num_results=num_results):
    url = "https://s.weibo.com/top/summary"  # 微博热搜榜URL
    yourUser_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
    yourcookie = 'SCF=ArVImN-rAa93jAX7-lP8kOsuGIeGDyRt3JbNyr-b3Kkql-yQ0LHDcV_RR9uH8pe-dJoW_-jqio1nh3CKNlRchzc.; SINAGLOBAL=2811722820605.9.1734250707227; UOR=,,origin.eqing.tech; ALF=1737784441; SUB=_2A25KaJ8pDeRhGeFH71cT9izIzDWIHXVpB57hrDV8PUJbkNANLXbXkW1NeyaIfAsuWXLdpycS9G_e0Lw1mpIXN6D1; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhNReiNgkPP3XWsl.NobBan5JpX5KMhUgL.FoM4Sh-ESozXS0.2dJLoIpYLxKnLBoMLB-qLxKBLB.2LB.2LxKML1KBLBoiW-8xq; XSRF-TOKEN=Kb6AqWUTVGqhVAv2HX28xwuz; _s_tentry=weibo.com; Apache=2662981918649.887.1735192707281; ULV=1735192707311:3:3:1:2662981918649.887.1735192707281:1734531090221; WBPSESS=VcS33kpB4y4rVzdQg8AvDfskifIc_2uxgDMSAtmzoWijfbgvWPjsULjF4Zj1i4v4iiZ4uOmXO2fIKKqbAbcKWoyQBVrteLw_L4b0TEltVze7aY35ZbOLOkiI5ZJ9-osiypKG6XJYw1hi33ltAhO0Cg=='
    headers = {
        'cookie': yourcookie,
        'User-Agent': yourUser_Agent
    }
    response = requests.get(url, headers=headers)

    # 随机延迟，防止请求过于频繁
    time.sleep(random.uniform(2, 5))  # 延时 2-5 秒

    if response.status_code != 200:
        print("请求失败，状态码：", response.status_code)
        return []

    # 解析网页内容
    soup = BeautifulSoup(response.text, "html.parser")
    hot_search_list = []
    for idx, item in enumerate(soup.select(".td-02 > a"), start=1):
        if idx > num_results:
            break
        Title = item.text.strip()
        Search_url = "https://s.weibo.com" + item["href"]
        hot_search_list.append({"Rank": idx, "Title": Title, "Search_url": Search_url})

        # 每次获取一个热搜之后，稍微延时
        time.sleep(random.uniform(2, 5))  # 延时 1-3 秒

    return hot_search_list


# 保存数据到CSV文件
def save_to_csv(filename, data):
    with open(filename, "w", newline='', encoding="utf-8-sig") as csvfile:
        fieldnames = ["Rank", "Title", "Search_url"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # 写入表头
        writer.writeheader()

        # 写入数据
        for row in data:
            writer.writerow({
                "Rank": row["Rank"],
                "Title": row["Title"],
                "Search_url": row["Search_url"]
            })


if __name__ == "__main__":
    output_file = "weibo_hot_search_results.csv"

    # 获取微博热搜榜
    print(f"获取微博热搜榜中前 {num_results} 个...")
    hot_search = get_weibo_hot_search(num_results)

    if hot_search:
        print("\n微博热搜榜：")
        for item in hot_search:
            print(f"{item['Rank']}. {item['Title']} - {item['Search_url']}")

        # 保存到CSV文件
        print("\n保存数据到CSV文件中...")
        save_to_csv(output_file, hot_search)
        print(f"数据已保存到 {output_file} 文件！")
    else:
        print("未获取到微博热搜榜数据。")
