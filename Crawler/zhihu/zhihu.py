# coding:utf-8
import requests
from lxml import html
import os

# 编码问题，可以加下面三行
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55'
                  '.0.2883.95 Safari/537.36',
    'Cookie': ''

}



# url = 'https://www.zhihu.com/collection/69135664'
# response = requests.get(url, headers=headers).content
# print response


def get_link_ist(collection_num):
    page = input('你想要多少页？(注意身体哦～):')
    result = []
    collection_title = None
    for i in range(1, page+1):
        link = 'https://www.zhihu.com/collection/{}?page={}'.format(collection_num, i)
        response = requests.get(link, headers=headers).content
        sel = html.fromstring(response)
        # 创建文件夹
        if collection_title is None:
            # 收藏夹名字
            collection_title = sel.xpath('//h2[@class="zm-item-title zm-editable-content"]/text()')[0].strip()
            if collection_title == '':
                collection_title = '我的收藏'
            if not os.path.exists(collection_title):
                os.mkdir(collection_title)
        each = sel.xpath('//div[@class="zm-item"]//div[@class="zm-item-answer "]/link')
        for e in each:
            link = 'https://www.zhihu.com' + e.xpath('@href')[0]
            result.append(link)
    return [collection_title, result]


def get_pic(collection, answer_link):
    response = requests.get(answer_link, headers=headers).content
    sel = html.fromstring(response)
    title = sel.xpath('//h1[@class="QuestionHeader-title"]/text()')[0].strip()
    try:
        # 匿名用户
        author = sel.xpath('//a[@class="UserLink-link"]/text()')[0].strip()
    except:
        author = u'匿名用户'
    # 新建路径
    path = collection + '/' + title + ' - ' + author
    try:
        if not os.path.exists(path):
            os.mkdir(path)
        n = 1
        for i in sel.xpath('//div[@class="RichContent-inner"]//img/@src'):
            # 去除whitedot链接
            if 'whitedot' not in i:
                # print i
                pic = requests.get(i).content
                fname = path + '/' + str(n) + '.jpg'
                with open(fname, 'wb') as p:
                    p.write(pic)
                n += 1
        print u'{} 已完成'.format(title)
    except :
        pass


if __name__ == '__main__':
    collection_num = input('输入收藏夹号码：')
    r = get_link_ist(collection_num)
    collection = r[0]
    collection_list = r[1]
    for k in collection_list:
        get_pic(collection, k)