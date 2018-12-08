from lxml import etree
from bs4 import BeautifulSoup
import requests
import time
from multiprocessing import Process
from multiprocessing import JoinableQueue as Queue


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
        while True:
            url = self.url_queue.get()
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
        process_list = []
        # url_list
        p_url = Process(target=self.get_url_list)
        process_list.append(p_url)

        # 三个进程发送请求
        for i in range(3):
            p_request = Process(target=self.send_request)
            process_list.append(p_request)

        # 提取数据
        p_analysis = Process(target=self.analysis_list)
        process_list.append(p_analysis)

        # 保存
        t_save = Process(target=self.save_file)
        process_list.append(t_save)
        for p in process_list:
            p.daemon = True
            time.sleep(0.2)
            p.start()

        for q in [self.url_queue, self.response_queue, self.data_queue]:
            print(q)
            q.join()

        print("主进程程结束")


if __name__ == '__main__':
    t1 = time.time()
    qiubai = SpiderQiuBai()
    qiubai.run()
    print('total time:', time.time()-t1)

