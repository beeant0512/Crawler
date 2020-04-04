#!/usr/bin/python
# -*- coding: UTF-8 -*-

import requests
import threading
from lxml import etree
import os

# 乐多网站网址
url = 'http://leduomh.com/book/'

# 当前目录，用于存储下载下来的图片
folder = os.getcwd()

# 请求头
header = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'User-Agent': 'Mozilla/5.0 (compatible; ABrowse 0.4; Syllable)'
}


# 文件存储
def file_store(path, r):
    with open(path, 'wb') as f:
        f.write(r.content)


# 获取章节的图片
def getChapterImgs(path, url, chapterName):
    chapter_path = os.path.join(path, chapterName)
    if not os.path.exists(chapter_path):
        os.mkdir(chapter_path)
    response = requests.get(url,
                            headers=header,
                            timeout=60
                            )
    tree = etree.HTML(response.text)
    imgs = tree.xpath(u"//img")

    for img in imgs:
        src = img.attrib.get('data-original')
        # 存储
        if src:
            p = src.split('/')
            image_file_name = chapter_path + '/' + p[len(p) - 1]
            if not os.path.exists(image_file_name):
                r = requests.get(src, headers=header)
                file_store(image_file_name, r)


# 获取章节信息
def getChapter(url):
    response = requests.get(url, headers=header, timeout=60)
    tree = etree.HTML(response.text)

    # 名称
    book_name = tree.xpath("//div[@class='banner_detail_form']//div[@class='info']//h1")
    book_path = folder + "/" + book_name[0].text.replace('/', '-')
    if not os.path.exists(book_path):
        os.mkdir(book_path)
    # 寻找章节
    chapters = tree.xpath("//ul[@id='detail-list-select']//li//a")
    threads = [0] * len(chapters)
    for k, chapter in enumerate(chapters):
        href = chapter.attrib.get('href')
        name = chapter.text
        threads[k] = myThread(book_path, 'http://leduomh.com' + href, name)
        threads[k].start()

    for k, thread in enumerate(threads):
        thread.join()

# 定义线程加速爬
class myThread(threading.Thread):
    def __init__(self, path, url, name):
        threading.Thread.__init__(self)
        self.path = path
        self.url = url
        self.name = name

    def run(self):
        print("开始线程：" + self.name)
        getChapterImgs(self.path, self.url, self.name)
        print("退出线程：" + self.name)


def main():
     # 目前知道的只有4 到 662 之间的数字有漫画，后续可自行定义
    for num in range(4,662): 
        getChapter(url + str(num))


if __name__ == '__main__':
    main()
