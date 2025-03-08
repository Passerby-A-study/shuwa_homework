import json
import re
import requests
import urllib.parse
from bs4 import BeautifulSoup

class Sina:

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'
    cookies_str = 'sinaAds; post=massage; NowDate=Tue Feb 04 2025 12:06:01 GMT+0800 (中国标准时间); UOR=cn.bing.com,finance.sina.com.cn,; SINAGLOBAL=14.145.9.70_1719888374.783891; SCF=ArVImN-rAa93jAX7-lP8kOsuGIeGDyRt3JbNyr-b3KkqOCQu8_S-lFzYkg8hKEmE_iBzt0skY9gr79oCe1vG_tQ.; Apache=183.238.76.97_1738641246.788801; ULV=1738641263853:2:1:1:183.238.76.97_1738641246.788801:1719888374919'
    encoded_cookies = urllib.parse.quote(cookies_str, safe=';/= ')#请求头有中文
    headers = {
        'User-Agent': user_agent
    }
    sina_news_url = 'https://feed.sina.com.cn/api/roll/get'
    sina_news=[]
    file_path = 'homework_2.json'

    def spider(self):
        for page in range(1,6):
            print(f"正在爬起第{page}页")
            data = {
                'pageid': '121',
                'lid': '1356',
                'num': '20',
                'versionNumber': '1.2.4',
                'page': page,
                'encode': 'utf-8',
                'callback': 'feedCardJsonpCallback'
            }
            response = requests.get(url=self.sina_news_url, params=data, headers=self.headers, cookies=dict(Cookie=self.encoded_cookies))
            jsonp_str = response.text
            match = re.search(r'feedCardJsonpCallback\((.*)\);}catch\(e\){};', jsonp_str)
            if match:
                json_str = match.group(1)
                data = json.loads(json_str)
            news_data = data['result']['data']
            for news in news_data:
                url = news['url']
                response_url = requests.get(url=url, headers=self.headers, cookies=dict(Cookie=self.encoded_cookies))
                response_url.encoding = 'utf-8'
                html_content = response_url.text
                soup = BeautifulSoup(html_content, 'html.parser')
                date=soup.find('span',class_='date').text.strip()
                title=soup.find('h1',class_='main-title').text.strip()
                article=[]
                element_img=soup.find_all('div',class_='img_wrapper')
                img_urls = []
                for img_div in element_img:
                    img_tag = img_div.find('img')
                    if img_tag and 'src' in img_tag.attrs:
                        img_url = img_tag['src']
                        img_urls.append(img_url)
                article.extend(img_urls)
                element_literate=soup.find_all('p',{'cms-style':'font-L'})
                for p in element_literate:
                    article.append(p.text.strip())
                self.sina_news.append({"title":title,"body":article,"date":date})


    def write_file(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.sina_news, f, ensure_ascii=False, indent=4)


if __name__ == '__main__' :
    sina=Sina()
    sina.spider()
    print("爬取完成")
    sina.write_file()
    print(f"数据已成功写入 {sina.file_path}")

