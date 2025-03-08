import requests
import json
from bs4 import BeautifulSoup

class Bookreview:
    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'
    cookies='bid=UYUqRguXba8; ll="118281"; _ga=GA1.2.1344245837.1732415084; _ga_Y4GN1R87RG=GS1.1.1732415084.1.0.1732416288.0.0.0; _vwo_uuid_v2=D50DB0494F61897CC762EE31B3957AAB9|88cbe26c66ea0adfa4c373555848498d; __utmz=30149280.1733019450.3.2.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; _pk_id.100001.3ac3=5e2142cddda05ab4.1738296727.; _pk_ses.100001.3ac3=1; ap_v=0,6.0; __utma=30149280.1017075583.1732415074.1733019450.1738296727.4; __utmc=30149280; __utma=81379588.1344245837.1732415084.1738296727.1738296727.1; __utmc=81379588; __utmz=81379588.1738296727.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmb=30149280.10.10.1738296727; __utmb=81379588.10.10.1738296727'
    headers={
        'User-Agent':user_agent,
        'Cookies':cookies
    }
    douban_book_url="https://book.douban.com/latest"
    page=None
    latest_book=[]
    file_path = 'homework_1.json'

    def spider(self):
        for page in range(1,6):
            print(f"正在爬取第{page}页")
            data = {
                'subcat': '全部',
                'p': page
            }
            response=requests.get(url=self.douban_book_url,params=data,headers=self.headers)
            json_data=BeautifulSoup(response.text,'html.parser')
            books=json_data.find_all('li', class_='media clearfix')
            books.extend(json_data.find_all('li',class_='media clearfix last'))
            for book in books:
                information=book.find('div',class_='media__body')
                name=information.find('a',class_='fleft').text.strip()
                author=information.find('p',class_="subject-abstract color-gray").text.strip()
                mark=information.find('span',class_="font-small color-red fleft").text.strip()
                if mark=="":
                    mark="No mark"
                try:
                    price =information.find('span',class_="buy-info").text.strip()
                except:
                    price ="No price"
                self.latest_book.append({"name":name,"author":author,"mark":mark,"price":price})


    def write_file(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            # ensure_ascii=False 确保中文能正确写入，indent=4 让 JSON 文件格式更美观
            json.dump(self.latest_book, f, ensure_ascii=False, indent=4)

if __name__=='__main__':
    book=Bookreview()
    book.spider()
    print("爬取完成")
    book.write_file()
    print(f"数据已成功写入 {book.file_path}")

