#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
import json
import pymongo
import time

# 准备全局变量
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36 Qiyu/2.1.1.1",
    "Referer": "https://y.qq.com/portal/player.html"
}
def get_singer_list():
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['Song']
    sl = db['singerList']
    page = int(input('请查询的歌手页数:'))
    for x in range(page):
        url = "https://u.y.qq.com/cgi-bin/musicu.fcg?callback=getUCGI25738961582047115&g_tk=5381&jsonpCallback=getUCGI25738961582047115&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&data=%7B%22comm%22%3A%7B%22ct%22%3A24%2C%22cv%22%3A10000%7D%2C%22singerList%22%3A%7B%22module%22%3A%22Music.SingerListServer%22%2C%22method%22%3A%22get_singer_list%22%2C%22param%22%3A%7B%22area%22%3A-100%2C%22sex%22%3A-100%2C%22genre%22%3A-100%2C%22index%22%3A-100%2C%22sin%22%3A"+str(x*80)+"%2C%22cur_page%22%3A"+str(x+1)+"%7D%7D%7D"
        headers['Referer'] = "https://y.qq.com/portal/singer_list.html"
        ie = requests.session()
        rep = ie.get(url, headers=headers)
        html = rep.content.decode('utf-8')[25:-1]
        singer_list = json.loads(html)['singerList']['data']['singerlist']
        for singer in singer_list:
            singerTemp = {
                'Id': singer['singer_mid'],
                'Name': singer['singer_name'],
                'picLink': 'http://y.gtimg.cn/music/photo_new/T001R150x150M000'+singer['singer_mid']+'.webp'
            }
            result = sl.insert_one(singerTemp)
            print(result)
            print(result.inserted_id)

get_singer_list()
