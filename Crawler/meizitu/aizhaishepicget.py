# coding=utf-8
import random
import re
import threading
import time

import chardet
import requests
from bs4 import BeautifulSoup
import os


def del_file(path):
    if not os.path.exists(path):
        return
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
    os.rmdir(path)


def get_html(url):  # 获得页面html代码
    headers = {
        'authority': 'aizhaishe.org',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'referer': 'https://aizhaishe.org/luyifa/2017/0316/3134_8.html',
        # 'accept-encoding': 'gzip, deflate, br',
        # 'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cookie': 'UM_distinctid=168e1ab56b1b6-09c39bca702aee-13396850-1aeaa0-168e1ab56b27d1; ASPSESSIONIDQCCTAQQD=HEOJOBFBHBIOIAOMKEIILAAA; CNZZDATA1273986503=524050400-1549971382-%7C1549991745',
    }

    t = 3
    while t > 0:
        try:
            req = requests.get(url, headers=headers)
            if req.status_code == 200:
                t = 0
                break
            else:
                print('response not 200: ' + str(req.status_code))
                t = t - 1
        except Exception, e:
            print('response exception: ' + str(e.message))
            t = t - 1
        time.sleep(10)
    html = req.content
    # print chardet.detect(html)
    return html


def get_title(soup):  # find the article title
    title = soup.find('h1', class_="article-title")
    return title.text


def get_image_url_list(soup):
    article = soup.find('article', class_='article-content')
    return [a['src'] for a in article.findAll('img')]


def get_next_page(soup):
    li = soup.find('li', class_='next-page')
    if li is not None:
        return li.a['href']
    else:
        return None


def save_img(img_url, url, name):
    headers = {
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
    }

    if img_url == "":
        return
    t = 3
    while t > 0:
        try:
            req = requests.get(img_url, headers=headers)
            if req.status_code == 200:
                t = 0
                print("get " + img_url + " OK!")
                break
            else:
                print('response not 200: ' + str(req.status_code))
                t = t - 1
        except Exception, e:
            print('response exception: ' + str(e.message))
            t = t - 1
        time.sleep(10)
    file_name = img_url.split('/')[-1].split('-')[1]
    with open(name + '/' + file_name, 'wb') as f:
        f.write(req.content)


def save_images(image_list, url, name):
    for img_url in image_list:
        save_img(img_url, url, name)


def main():
    # url = raw_input("input main page id: ")
    start_url = "https://aizhaishe.org/xiurenwang/2018/0901/5733.html"
    # main_url = ""
    for i in range(10):
        print(start_url)
        start_url = run_set(start_url)




def find_next_set(soup):
    a_set = soup.findAll('a', target='_blank')
    want_url_set = []
    for a in a_set:
        if not 'title' in a.attrs:
            title = a.text
        else:
            title = a['title']
        if title.find(u'撸一管')>=0 or title.find(u'大尺度')>=0:
            want_url_set.append(a['href'])
    len = want_url_set.__len__()
    random.seed(time)
    rand = random.random()
    i = int(rand * len)
    return "https://aizhaishe.org" + want_url_set[i]




def run_set(url):
    # url = "https://aizhaishe.org/luyifa/2017/0312/3119.html"
    main_page_prefix = "/".join(url.split("/")[:-1]) + "/"
    site_prefix = "/".join(url.split("/")[:3])
    print main_page_prefix, site_prefix
    html = get_html(url)
    soup = BeautifulSoup(html.decode('GB2312', errors='ignore'), 'html.parser')
    title = "aizhaishe" + os.sep + "aizhaishe_" + get_title(soup)
    print title
    if os.path.exists(title):
        print(title + "has exists!")
        return find_next_set(soup)
    del_file(title)
    os.mkdir(title)
    threading.Thread(target=save_images, args=(get_image_url_list(soup), url, title)).start()
    next_page = get_next_page(soup)
    soup_next = soup
    while next_page is not None:
        html_next = get_html(main_page_prefix + next_page)
        soup_next = BeautifulSoup(html_next.decode('GB2312', errors='ignore'), 'html.parser')
        # save_images(get_image_url_list(soup_next), main_page_prefix + next_page, title)
        threading.Thread(target=save_images, args=(get_image_url_list(soup_next), main_page_prefix + next_page, title)).start()
        next_page = get_next_page(soup_next)
    for t in threading.enumerate():
        if t != threading.currentThread() and t.name.find('Thread-') == 0:
            print t
            t.join()
    print "DONE: " + title
    return find_next_set(soup_next)



if __name__ == "__main__":
    main()
