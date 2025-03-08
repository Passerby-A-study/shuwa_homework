import os
import csv
import requests
import time
import random
import logging

# 设置日志输出配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 定义全局变量，包括cookie和请求头
yourUser_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
yourcookie = 'SCF=ArVImN-rAa93jAX7-lP8kOsuGIeGDyRt3JbNyr-b3Kkql-yQ0LHDcV_RR9uH8pe-dJoW_-jqio1nh3CKNlRchzc.; SINAGLOBAL=2811722820605.9.1734250707227; UOR=,,origin.eqing.tech; ALF=1737784441; SUB=_2A25KaJ8pDeRhGeFH71cT9izIzDWIHXVpB57hrDV8PUJbkNANLXbXkW1NeyaIfAsuWXLdpycS9G_e0Lw1mpIXN6D1; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhNReiNgkPP3XWsl.NobBan5JpX5KMhUgL.FoM4Sh-ESozXS0.2dJLoIpYLxKnLBoMLB-qLxKBLB.2LB.2LxKML1KBLBoiW-8xq; XSRF-TOKEN=Kb6AqWUTVGqhVAv2HX28xwuz; _s_tentry=weibo.com; Apache=2662981918649.887.1735192707281; ULV=1735192707311:3:3:1:2662981918649.887.1735192707281:1734531090221; WBPSESS=VcS33kpB4y4rVzdQg8AvDfskifIc_2uxgDMSAtmzoWijfbgvWPjsULjF4Zj1i4v4iiZ4uOmXO2fIKKqbAbcKWoyQBVrteLw_L4b0TEltVze7aY35ZbOLOkiI5ZJ9-osiypKG6XJYw1hi33ltAhO0Cg=='
headers = {
    'cookie': yourcookie,
    'User-Agent': yourUser_Agent
}


# 创建一个函数用于爬取评论并写入CSV文件
def crawl_comments(input_csv_file, output_folder):
    with open(input_csv_file, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        # 提取输入CSV文件的文件名
        output_file_name = os.path.basename(input_csv_file)
        output_file_path = os.path.join(output_folder, output_file_name)  # 设置输出文件路径

        # 打开文件用于写入数据，设置合适的编码和换行符
        with open(output_file_path, mode='w', encoding='utf-8-sig', newline='') as f:
            csv_writer = csv.DictWriter(f, fieldnames=['昵称', '地区', '性别', '粉丝数', '用户发布微博数量', '评论'])
            csv_writer.writeheader()

            # 获取评论数据的函数
            def get_comments(ID, max_id=None, current_page=None):
                try:
                    # 获取帖子ID的请求
                    weibo_get_commendmid_url = f'https://weibo.com/ajax/statuses/show?id={ID}&locale=zh-CN'
                    response = requests.get(url=weibo_get_commendmid_url, headers=headers)
                    json_commendmid_data = response.json().get('idstr')

                    # 如果没有获取到idstr，输出错误信息并返回
                    if not json_commendmid_data:
                        logger.error(f"无法获取微博ID {ID} 的评论ID，请检查数据")
                        return None

                    # 请求评论的URL
                    weibo_url = 'https://weibo.com/ajax/statuses/buildComments'
                    if max_id is None:
                        # 页面的初始请求，第一页
                        data = {
                            'is_reload': '1',
                            'id': json_commendmid_data,
                            'is_show_bulletin': '2',
                            'is_mix': '0',
                            'count': '10',
                            'uid': '1653603955',
                            'fetch_level': '0',
                            'locale': 'zh-CN'
                        }
                    else:
                        # 后续页的请求
                        data = {
                            'low': '0',
                            'is_reload': '1',
                            'id': json_commendmid_data,
                            'is_show_bulletin': '2',
                            'is_mix': '0',
                            'max_id': max_id,
                            'count': '20',
                            'uid': '1653603955',
                            'fetch_level': '0',
                            'locale': 'zh-CN'
                        }

                    # 加入随机时间间隔
                    time.sleep(random.uniform(2, 5))  # 在2到5秒之间随机暂停

                    response = requests.get(url=weibo_url, params=data, headers=headers)
                    json_data = response.json()
                    data_list = json_data.get('data')

                    if data_list is None:
                        logger.warning(f"当前页 {current_page} 返回数据结构异常，缺少'data'键，跳过此页")
                        return max_id

                    max_id = json_data.get('max_id')
                    for index in data_list:
                        sex = index['user']['gender']
                        if sex == 'f':
                            gender = '女'
                        elif sex == 'm':
                            gender = '男'
                        else:
                            gender = '保密'

                        dict_data = {
                            '昵称': index['user']['screen_name'],
                            '地区': index['user']['location'],
                            '性别': gender,
                            '粉丝数': index['user']['followers_count'],
                            '用户发布微博数量': index['user']['statuses_count'],
                            '评论': index['text']
                        }
                        logger.info(f"正在写入评论数据：{dict_data}")
                        csv_writer.writerow(dict_data)

                    return max_id

                except Exception as e:
                    logger.error(f"爬取微博ID {ID} 第 {current_page} 页评论时出现异常: {str(e)}")
                    return max_id

            # 遍历CSV文件中的所有ID并爬取评论
            for row in reader:
                ID = row['ID']  # 假设CSV中有一个名为ID的列存储需要爬取的微博ID

                max_id = None
                for page in range(1, 10):  # 假设最多爬取10页
                    logger.info(f'爬取微博ID {ID} 第 {page} 页评论')
                    max_id = get_comments(ID, max_id=max_id, current_page=page)
                    if not max_id:
                        break
                    logger.info(f'成功爬取微博ID {ID} 第 {page} 页评论')


# 创建输出文件夹，如果不存在的话
output_folder = 'weibo_comments_output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 读取weibo_posts_output文件夹中的每个CSV文件，并调用爬取评论的函数
input_folder = 'weibo_posts_output'
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.endswith('.csv'):
            input_csv_path = os.path.join(root, file)
            crawl_comments(input_csv_path, output_folder)
