import requests
from bs4 import BeautifulSoup
import csv



class Xinhua:
    xinhua_url = 'https://www.news.cn/tech/'
    headers = {
        'user - agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0'
    }
    dates = []
    titles = []
    articles_list = []
    visited_urls = set()
    file_path='homework_3.csv'

    def spider(self):
        response = requests.get(self.xinhua_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a')
        for a_tag in a_tags:
            href = a_tag.get('href')
            if href and href.startswith('/tech/') and len(href.split('/')) == 5 and href.endswith('/c.html') and href not in self.visited_urls:
                full_url = 'https://www.news.cn' + href
                self.visited_urls.add(href)
                url_response = requests.get(url=full_url, headers=self.headers)
                url_soup = BeautifulSoup(url_response.text, 'html.parser')
                title = url_soup.find('span', class_='title')
                if title:
                    title = title.text.strip()
                date = url_soup.find('div', class_='info')
                if date:
                    date = date.text.strip()[:len('2024 - 12 - 27 19:15:39')]
                articles = url_soup.find_all('p')
                article_texts = []
                for article in articles:
                    article_texts.append(article.text.strip())
                self.dates.append(date)
                self.titles.append(title)
                self.articles_list.append(article_texts)

    def write_file(self):
        with open(self.file_path, 'w', newline='', encoding='utf - 8') as csvfile:
            fieldnames = ['Title', 'Body', 'Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for i in range(len(self.dates)):
                article_text = ' '.join(self.articles_list[i])
                writer.writerow({'Title': self.titles[i], 'Body': article_text, 'Time': self.dates[i]})


if __name__=='__main__':
    xinhua=Xinhua()
    xinhua.spider()
    print("爬取完成")
    xinhua.write_file()
    print(f"数据已成功写入 {xinhua.file_path}")