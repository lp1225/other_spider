import requests
from lxml import etree
from bs4 import BeautifulSoup
from queue import Queue
from multiprocessing.dummy import Pool
import time


class SpiderQiuBai:

    def __init__(self):
        self.base_url = 'http://www.qiushibaike.com/8hr/page/{}'
        self.headers = {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
                    }
        self.url_queue = Queue()
        self.pool = Pool()
        self.response_count = 0
        self.request_count = 0
        #  判断 是否解开递归的条件
        self.isrunning = True

    def get_url_list(self):
        """
        入队列
        """
        for i in range(1, 14):
            self.url_queue.put(self.base_url.format(i))
            self.request_count += 1

    def send_request(self, url):
        # time.sleep(1)
        print(url)
        response = requests.get(url, headers=self.headers)
        self.response_count += 1
        data = response.content.decode('utf-8')
        return data

    def analysis_data(self, data):
        """
        提取数据
        """
        html = etree.HTML(data)
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

    def _execute_request_response_item(self):
        """
        一个线程执行的任务
        """
        url = self.url_queue.get()
        data = self.send_request(url)
        self.analysis_data(data)

    def _callback(self, item):
        if self.isrunning:
            self.pool.apply_async(self._execute_request_response_item, callback=self._callback)

    def run(self):
        self.get_url_list()
        # 开启异步任务
        for i in range(2):
            self.pool.apply_async(self._execute_request_response_item, callback=self._callback)
        while True:
            time.sleep(0.00001)
            #  判断条件 当 响应的个数 大于等于 请求的个数 13
            if self.response_count >= self.request_count:
                # 解开递归
                self.isrunning = False
                break

        self.pool.close()


if __name__ == '__main__':
    t1 = time.time()
    qiubai = SpiderQiuBai()
    qiubai.run()
    print('total time:', time.time()-t1)
