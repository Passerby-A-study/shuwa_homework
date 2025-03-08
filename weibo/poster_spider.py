import os
import csv
import requests
import time
import random
import logging

# 设置日志输出配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置全局变量，包括cookie和请求头
yourUser_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
yourcookie = 'SCF=ArVImN-rAa93jAX7-lP8kOsuGIeGDyRt3JbNyr-b3Kkql-yQ0LHDcV_RR9uH8pe-dJoW_-jqio1nh3CKNlRchzc.; SINAGLOBAL=2811722820605.9.1734250707227; UOR=,,origin.eqing.tech; ALF=1737784441; SUB=_2A25KaJ8pDeRhGeFH71cT9izIzDWIHXVpB57hrDV8PUJbkNANLXbXkW1NeyaIfAsuWXLdpycS9G_e0Lw1mpIXN6D1; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhNReiNgkPP3XWsl.NobBan5JpX5KMhUgL.FoM4Sh-ESozXS0.2dJLoIpYLxKnLBoMLB-qLxKBLB.2LB.2LxKML1KBLBoiW-8xq; XSRF-TOKEN=Kb6AqWUTVGqhVAv2HX28xwuz; _s_tentry=weibo.com; Apache=2662981918649.887.1735192707281; ULV=1735192707311:3:3:1:2662981918649.887.1735192707281:1734531090221; WBPSESS=VcS33kpB4y4rVzdQg8AvDfskifIc_2uxgDMSAtmzoWijfbgvWPjsULjF4Zj1i4v4iiZ4uOmXO2fIKKqbAbcKWoyQBVrteLw_L4b0TEltVze7aY35ZbOLOkiI5ZJ9-osiypKG6XJYw1hi33ltAhO0Cg=='
headers = {
    'cookie': yourcookie,
    'User-Agent': yourUser_Agent
}

# 创建输出文件夹，如果不存在的话
output_info_folder = 'weibo_combined_output_info'
if not os.path.exists(output_info_folder):
    os.makedirs(output_info_folder)


# 获取验证类型含义的函数
def get_verified_type_meaning(verified_type):
    verified_types = {
        -1: "普通用户", 0: "名人（黄V）", 1: "政府（蓝V）", 2: "企业（蓝V）", 3: "媒体（蓝V）",
        4: "校园（蓝V）", 5: "网站（蓝V）", 6: "应用（蓝V）", 7: "团体（机构）（蓝V）", 8: "待审企业",
        200: "初级达人", 220: "中高级达人", 400: "已故V用户"
    }
    return verified_types.get(verified_type, "未知类型")


# 获取发布者详细信息的函数
def get_poster_info(uid):
    poster_url = 'https://weibo.com/ajax/profile/info'
    poster_data = {'uid': uid}
    response_poster = requests.get(url=poster_url, params=poster_data, headers=headers)
    print(response_poster)

    if response_poster.status_code == 200:
        response_poster_json = response_poster.json()
        return {
            '发布者粉丝数': response_poster_json['data']["user"]["followers_count"],
            '发布者微博数量': response_poster_json['data']["user"]["statuses_count"],
            '发布者认证状态': response_poster_json['data']['user']["verified"],
            '发布者认证类型': get_verified_type_meaning(response_poster_json['data']['user']["verified_type"]),
            '发布者URL': response_poster_json['data']['user']['profile_url']
        }
    else:
        logger.error(f"获取用户信息失败，UID: {uid}")
        return None


# 获取微博信息的函数
def get_weibo_info(ID):
    try:
        post_url = 'https://weibo.com/ajax/statuses/show'
        data = {'id': ID, 'locale': 'zh-CN', 'isGetLongText': 'true'}
        response = requests.get(url=post_url, params=data, headers=headers)
        print(response.json())
        if response.status_code != 200:
            logger.error(f"获取微博信息失败，ID: {ID}")
            return None

        response_json = response.json()

        # 获取微博的相关数据
        poster_name = response_json['user']['screen_name']
        post_zhuanfa_num = response_json["reposts_count"]
        post_commend_num = response_json["comments_count"]
        post_dianzan_num = response_json["attitudes_count"]

        # 提取发布者UID，去掉 /u/ 前缀
        poster_uid = response_json['user']['profile_url'].lstrip('/u/')

        # 获取发布者的详细信息
        poster_info = get_poster_info(poster_uid)

        if poster_info:
            return {
                '发布者昵称': poster_name,
                '转发数': post_zhuanfa_num,
                '评论数': post_commend_num,
                '点赞数': post_dianzan_num,
                **poster_info  # 添加发布者的基本信息
            }

    except Exception as e:
        logger.error(f"获取微博信息时出现异常: {str(e)}")
        return None


# 计算标准化值的函数
def standardize(values):
    min_val = min(values)
    max_val = max(values)
    return [(value - min_val) / (max_val - min_val) for value in values]


# 计算博主影响力数据
def calculate_influence(data):
    followers = [item['发布者粉丝数'] for item in data]
    likes = [item['点赞数'] for item in data]
    comments = [item['评论数'] for item in data]
    forwards = [item['转发数'] for item in data]

    # 计算标准化数据
    standardized_likes = standardize(likes)
    standardized_comments = standardize(comments)
    standardized_forwards = standardize(forwards)

    # 计算关注度得分
    attention_scores = [
        0.2 * like + 0.3 * comment + 0.3 * forward
        for like, comment, forward in zip(standardized_likes, standardized_comments, standardized_forwards)
    ]

    # 计算平均粉丝数
    avg_follower = sum(followers) / len(followers) if followers else 0

    # 计算平均关注度
    avg_attention = sum(attention_scores) / len(attention_scores) if attention_scores else 0

    # 计算V博主数量
    v_count = sum(1 for item in data if item['发布者认证状态'] == 1)

    # 计算平均历史博客量
    avg_hisvol = sum(item['发布者微博数量'] for item in data) / len(data) if data else 0

    # 总点赞数、评论数、转发数、博客总量
    total_likes = sum(likes)
    total_comments = sum(comments)
    total_forwards = sum(forwards)
    total_posts = len(data)

    return {
        'AvgFollower': avg_follower,
        'AvgAttention': avg_attention,
        'V_count': v_count,
        'AvgHisVol': avg_hisvol,
        'TotalLikes': total_likes,
        'TotalComments': total_comments,
        'TotalForwards': total_forwards,
        'TotalPosts': total_posts
    }


# 爬取评论并写入CSV文件
def crawl_comments(input_csv_file, output_info_folder):
    # 读取输入的CSV文件
    with open(input_csv_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        data = []

        # 读取并收集数据
        for row in reader:
            ID = row['ID']
            weibo_info = get_weibo_info(ID)
            if weibo_info:
                data.append(weibo_info)

            # 添加随机时间间隔，防止被封
            time.sleep(random.uniform(2, 5))  # 随机延时 2 到 5 秒

        # 计算博主影响力数据
        influence_data = calculate_influence(data)

        # 设置输出文件路径
        info_output_file_path = os.path.join(output_info_folder, f"info_{os.path.basename(input_csv_file)}")

        with open(info_output_file_path, mode='w', encoding='utf-8-sig', newline='') as f_info:
            fieldnames = [
                'AvgFollower', 'AvgAttention', 'V_count', 'AvgHisVol',
                'TotalLikes', 'TotalComments', 'TotalForwards', 'TotalPosts'
            ]
            csv_info_writer = csv.DictWriter(f_info, fieldnames=fieldnames)
            csv_info_writer.writeheader()
            csv_info_writer.writerow(influence_data)


# 读取weibo_posts_output文件夹中的每个CSV文件，并调用爬取评论的函数
input_folder = 'weibo_posts_output'
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.endswith('.csv'):
            input_csv_path = os.path.join(root, file)
            logger.info(f"开始爬取文件 {file}")
            crawl_comments(input_csv_path, output_info_folder)
            logger.info(f"完成爬取文件 {file}")
