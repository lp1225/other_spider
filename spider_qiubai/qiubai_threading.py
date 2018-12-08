from lxml import etree
from bs4 import BeautifulSoup
from queue import Queue
import requests
import time
import threading


class SpiderQiuBai:

    def __init__(self):
        self.base_url = 'http://www.qiushibaike.com/8hr/page/{}'
        self.headers = {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 "
                                      "(KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
                    }
        self.url_queue = Queue()
        self.response_queue = Queue()
        self.data_queue = Queue()
        self.count = 0

    def get_url_list(self):
        """
        拼接所有页数的地址
        """
        for i in range(1, 14):
            self.url_queue.put(self.base_url.format(i))

    def send_request(self):
        """
        对页面发起请求
        """
        while True:  # 使用线程守护,否则子线程不结束
            url = self.url_queue.get()
            time.sleep(1)
            print(url)
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                self.response_queue.put(response)
            else:
                self.url_queue.put(url)

            self.url_queue.task_done()

    def analysis_list(self):
        """
        提取数据
        """
        while True:
            data = self.response_queue.get().text
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
            self.data_queue.put(content_list)
            self.response_queue.task_done()

    def save_file(self):
        while True:
            content_list = self.data_queue.get()
            print(content_list)
            self.data_queue.task_done()

    def run(self):
        thread_list = []
        # url_list
        t_url = threading.Thread(target=self.get_url_list)
        thread_list.append(t_url)

        # 三个线程发送请求
        for i in range(3):
            t_request = threading.Thread(target=self.send_request)
            thread_list.append(t_request)

        # 提取数据
        t_analysis = threading.Thread(target=self.analysis_list)
        thread_list.append(t_analysis)

        # 保存
        t_save = threading.Thread(target=self.save_file)
        thread_list.append(t_save)

        for t in thread_list:
            t.setDaemon(True)  # 把子线程设置为守护线程，当前这个线程不重要，主线程结束，子线程结束
            t.start()

        for q in [self.url_queue, self.response_queue, self.data_queue]:
            q.join()  # 让主线程阻塞，等待队列的计数为0，

        print("主线程结束")


if __name__ == '__main__':
    t1 = time.time()
    qiubai = SpiderQiuBai()
    qiubai.run()
    print('total time:', time.time()-t1)
