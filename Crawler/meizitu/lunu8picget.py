# coding=utf-8
import time

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


def get_page_name(url):  # 获得图集最大页数和名称
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    a_list = soup.findAll('a')
    pic_list = [url]
    for a in a_list:
        if a.attrs.has_key('href') and a['href'].find(url + "?page") == 0:
            pic_list.append(a['href'])

    title = soup.find('h1', class_="title")

    return pic_list, title.text


def get_html(url):  # 获得页面html代码
    headers = {
        'authority': 'www.lunu8.com',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        # 'referer': 'https://www.tuao8.com/post/195.html',
        # 'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cookie': 'ftwwwtuao8com=1; __cfduid=de58af645163b94b68232ad7c4c40297f1549722290; __51cke__=; UM_distinctid=168d2a591edf5-035c26a18e9974-13396850-1aeaa0-168d2a591ee8cf; pgv_pvi=6860773376; pgv_si=s5303814144; timezone=8; HstCfa4220059=1549722636372; HstCmu4220059=1549722636372; HstCnv4220059=1; __dtsu=1EE70445CBE35E5CA35A89BF02F0B967; ftwwwtuao8com=1; HstCns4220059=6; HstCla4220059=1549736952252; HstPn4220059=228; HstPt4220059=228; CNZZDATA1271838784=2144449714-1549720720-https%253A%252F%252Fwww.baidu.com%252F%7C1549734162; __tins__19458827=%7B%22sid%22%3A%201549735581605%2C%20%22vd%22%3A%2074%2C%20%22expires%22%3A%201549738752293%7D; __51laig__=464'
    }

    t = 3
    while t > 0:
        try:
            req = requests.get(url, headers=headers)
            if req.status_code == 200:
                t = 0
            else:
                print('response not 200: ' + str(req.status_code))
                t = t - 1
        except Exception, e:
            print('response exception: ' + str(e.message))
            t = t - 1
        time.sleep(1)
    html = req.text
    return html


def get_img_url(url):
    html = get_html(url)
    soup = BeautifulSoup(html, 'lxml')
    img_url = soup.findAll('img')
    for img in img_url:
        if img['src'].find("upload")>=0:
            return img['src']
    return ""


def save_img(img_url, url, name):
    headers = {
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
        'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'referer': url,
        'authority': 'www.lunu8.com',
        'cookie': '__cfduid=de58af645163b94b68232ad7c4c40297f1549722290; __51cke__=; UM_distinctid=168d2a591edf5-035c26a18e9974-13396850-1aeaa0-168d2a591ee8cf; pgv_pvi=6860773376; pgv_si=s5303814144; timezone=8; HstCfa4220059=1549722636372; HstCmu4220059=1549722636372; HstCnv4220059=1; __dtsu=1EE70445CBE35E5CA35A89BF02F0B967; CNZZDATA1271838784=2144449714-1549720720-https%253A%252F%252Fwww.baidu.com%252F%7C1549731520; ftwwwtuao8com=1; HstCns4220059=6; HstCla4220059=1549736860629; HstPn4220059=227; HstPt4220059=227; __tins__19458827=%7B%22sid%22%3A%201549735581605%2C%20%22vd%22%3A%2072%2C%20%22expires%22%3A%201549738660641%7D; __51laig__=462',
    }

    if img_url == "":
        return
    t = 3
    while t > 0:
        try:
            req = requests.get(img_url, headers=headers)
            if req.status_code == 200:
                t = 0
            else:
                print('response not 200: '+str(req.status_code))
                t = t-1
        except Exception, e:
            print('response exception: ' + str(e.message))
            t = t-1
        time.sleep(10)
    file_name = img_url.split('/')[-1]
    with open(name + '/' + file_name, 'wb') as f:
        f.write(req.content)


def main():
    num = input("input num: ")
    old_url = "https://www.lunu8.com/web/"+str(num)+".html"
    pages, name = get_page_name(old_url)
    dir_name = name + "_" + str(num)
    del_file(dir_name)
    os.mkdir(dir_name)
    for url in pages:
        img_url = get_img_url(url)
        # print(img_url)
        save_img(img_url, url, dir_name)
        print(u'保存 ' + url + u' 图片 ' + img_url + u' to ' + dir_name)
        time.sleep(0.1)


main()
