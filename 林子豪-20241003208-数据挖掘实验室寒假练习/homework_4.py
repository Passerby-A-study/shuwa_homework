import json
import re
import requests
from datetime import datetime


class Weibo:
    weibo_url = 'https://weibo.com/ajax/feed/unreadfriendstimeline'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0',
        'cookie': 'SCF=ArVImN-rAa93jAX7-lP8kOsuGIeGDyRt3JbNyr-b3Kkql-yQ0LHDcV_RR9uH8pe-dJoW_-jqio1nh3CKNlRchzc.; SINAGLOBAL=2811722820605.9.1734250707227; UOR=,,origin.eqing.tech; ULV=1735192707311:3:3:1:2662981918649.887.1735192707281:1734531090221; XSRF-TOKEN=8TvfIB-tzVFmd0Xlsmsnw1-d; SUB=_2A25KppM0DeRhGeFH71cT9izIzDWIHXVp3ar8rDV8PUNbmtANLU_7kW9NeyaIfAtDMsbjyGjLoN9mLUtgsqEI4oPw; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhNReiNgkPP3XWsl.NobBan5JpX5KzhUgL.FoM4Sh-ESozXS0.2dJLoIpYLxKnLBoMLB-qLxKBLB.2LB.2LxKML1KBLBoiW-8xq; ALF=02_1741320292; WBPSESS=VcS33kpB4y4rVzdQg8AvDfskifIc_2uxgDMSAtmzoWijfbgvWPjsULjF4Zj1i4v44PGBrkUXBoKrWFEjb3E-1u-hnuyhDcOEEsuDWwxml68VsbeuYMeeLNgdqyrub-kjGb5vwsavlWd2Pyr3bgguqg=='
    }
    data = {
        'list_id': '100017945262479',
        'refresh': '4',
        'since_id': '0',
        'count': '15'
    }
    post_set = []
    file_path='homework_4.json'

    def spider(self):
        response = requests.get(url=self.weibo_url, params=self.data, headers=self.headers).json()
        posts = response['statuses']
        for post in posts:
            name = post['user']['screen_name']
            date_str = post['created_at']
            # 将字符串转换为 datetime 对象
            date_obj = datetime.strptime(date_str, '%a %b %d %H:%M:%S %z %Y')
            # 将 datetime 对象转换为指定格式的字符串
            date = date_obj.strftime('%Y-%m-%d %H:%M:%S')
            article = post['text_raw']
            article = re.sub(r'\u200B', '', article)
            reposts_count = post['reposts_count']
            comments_count = post['comments_count']
            attitudes_count = post['attitudes_count']
            self.post_set.append({'screen_name': name, 'text_raw': article, 'comments_count': comments_count,
                             'reposts_count': reposts_count, 'created_at': date, 'attitudes_count': attitudes_count})

    def write_file(self):
        with open(self.file_path,'w',encoding='utf - 8 - sig') as f:
            json.dump(self.post_set,f,ensure_ascii=False, indent=4)



if __name__ =='__main__':
    weibo=Weibo()
    weibo.spider()
    print("爬取成功")
    weibo.write_file()
    print(f"数据已成功写入 {weibo.file_path}")