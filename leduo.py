#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import threading
from lxml import etree
import os

from tqdm import trange, tqdm
import time

# 乐多网站网址
url = 'http://leduomh.com/book/'

# 跳过连载中的
skip_writeing = 1

# 当前目录，用于存储下载下来的图片
folder = os.getcwd()

# error log
error_log = folder + "/error.log"

# 请求头
header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
}

# 定义代理ip
proxies = {
}


# 文件存储
def file_store(path, r):
    with open(path, 'wb') as f:
        f.write(r.content)


# 获取章节的图片
def getChapterImgs(book_name, path, url, chapter_name):
    chapter_path = os.path.join(path, chapter_name)
    if not os.path.exists(chapter_path):
        os.mkdir(chapter_path)
    try:
        response = requests.get(url,
                            headers=header,
                            proxies=proxies,
                            timeout=60
                            )
        tree = etree.HTML(response.text)
        imgs = tree.xpath(u"//img")
        description = book_name + " >> " + chapter_name
        with tqdm(total=len(imgs), desc=description) as pbar:
            for img in imgs:
                pbar.update(1)
                src = img.attrib.get('data-original')
                # 存储
                if src:
                    p = src.split('/')
                image_file_name = chapter_path + '/' + p[len(p) - 1]
                if not os.path.exists(image_file_name):
                    r = requests.get(src, headers=header, proxies=proxies, timeout=60)
                    file_store(image_file_name, r)
        time.sleep(1)
        
    except Exception as e:
        print(book_name + " " + chapter_name + " 获取异常")
        log_error(book_name + " " + chapter_name + " 获取异常")

def log_error(msg):
    with open(error_log, 'a+') as f:
        f.write( time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + " " + msg + '\n')

def cleanName(name):
    return name.replace('/', '-').replace(':', '-').replace("：", "-")


# 获取章节信息
def getChapter(url, num):
    try:
        response = requests.get(url, headers=header, proxies=proxies, timeout=60)
        tree = etree.HTML(response.text)

        # 名称
        book = tree.xpath("//div[@class='banner_detail_form']//div[@class='info']//h1")
        status = tree.xpath("//div[@class='banner_detail_form']//div[@class='info']/p[position()=3]/span/span")[0].text
        if (book):
            if skip_writeing == 1 and status == '连载中':
                return ;
            book_name = cleanName(book[0].text) + "-" + status
            book_path = folder + "/" + str(num) + "_" + book_name
            if not os.path.exists(book_path):
                os.mkdir(book_path)
            # 寻找章节
            chapters = tree.xpath("//ul[@id='detail-list-select']//li//a")
            # 限制最大20个线程池
            threads = [0] * len(chapters)
            # thread_len = 5
            # thread_pool = ThreadPoolExecutor(thread_len)

            # threads = [0] * thread_len
            with trange(len(chapters), desc=book_name) as pbar:
                for k, chapter in enumerate(chapters):
                    # tchapters.set_description(description + " %s")
                    href = chapter.attrib.get('href')
                    name = cleanName(chapter.text)
                    threads[k] = myThread(book_name, book_path, 'http://leduomh.com' + href, name, pbar)
                    threads[k].start()
                    # thread_pool.submit(getChapterImgs, boock_name, book_path, 'http://leduomh.com' + href, name)
                for k, thread in enumerate(threads):
                    thread.join()
    except Exception as e:
        print(url + " 访问异常")
        log_error(url + " 访问异常")


# 定义线程加速爬
class myThread(threading.Thread):
    def __init__(self, book, path, url, name, pbar):
        threading.Thread.__init__(self)
        self.book = book
        self.path = path
        self.url = url
        self.name = name
        self.pbar = pbar

    def run(self):
        # print("开始线程：" + self.name)
        getChapterImgs(self.book, self.path, self.url, self.name)
        # print("----退出线程：" + self.name)
        self.pbar.update(1)

def main():
    # 目前知道的只有4 到 662 之间的数字有漫画，后续可自行定义
    for num in range(4, 662):
        getChapter(url + str(num), num)
        time.sleep(2)
        

if __name__ == '__main__':
    main()
