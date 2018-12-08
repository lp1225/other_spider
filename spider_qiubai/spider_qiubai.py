import requests
from lxml import etree
from bs4 import BeautifulSoup
import time


class SpiderQiuBai:

    def __init__(self):
        self.base_url = 'http://www.qiushibaike.com/8hr/page/{}'
        self.headers = {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
                    }

    def get_url_list(self):
        """
        拼接所有页数的地址
        """
        return [self.base_url.format(i) for i in range(1, 14)]

    def send_request(self, url):
        response = requests.get(url, headers=self.headers)
        data = response.text
        return data

    def get_content_list(self, html_str):
        """
        提取数据
        """
        html = etree.HTML(html_str)
        li_list = html.xpath("//*[@id='content']/div/div[2]/div/ul")
        for res in li_list:
            result = etree.tostring(res).decode('utf-8')

        content_list = []
        soup = BeautifulSoup(result)
        li_list = soup.find_all('li')
        for li in li_list:
            item = {}
            div = li.find('div', class_='recmd-right')
            if div:
                user_name = div.a['title']
                content = div.a.get_text()
                item['article_title'] = user_name
                item['content'] = content
                content_list.append(item)

        return content_list

    def run(self):
        url_list = self.get_url_list()
        for url in url_list:
            html_str = self.send_request(url)
            content_list = self.get_content_list(html_str)
            print(content_list)


if __name__ == '__main__':
    t1 = time.time()
    qiubai = SpiderQiuBai()
    qiubai.run()
    print('total time:', time.time()-t1)
