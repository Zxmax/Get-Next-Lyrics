#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
import json
import pymongo
import time
import html


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'referer': 'https://y.qq.com/n/yqq/song.html'
}


def getLyric(songHtml):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['Song']
    sl = db['songLyricFull']
    url_2 = 'https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_yqq.fcg'
    params = {
        'nobase64': '1',
        'musicid': songHtml['id'],  # 用上面获取到的id
        '-': 'jsonp1',
        'g_tk': '5381',
        'loginUin': '0',
        'hostUin': '0',
        'format': 'json',
        'inCharset': 'utf8',
        'outCharset': 'utf-8',
        'notice': '0',
        'platform': 'yqq.json',
        'needNewCode': '0',
    }
    res_music = requests.get(url_2, headers=headers, params=params)
    # 发起请求
    js = res_music.json()
    if('lyric' in js):
        lyric = js['lyric']
        lyric_html = html.unescape(lyric)  # 用了转义字符html.unescape方法
        LyricTemp = {
                'id': songHtml['id'],
                'name': songHtml['name'],
                'singer': songHtml['singer'],
                'album': songHtml['album'],
                'lyric': lyric_html
            }
        result=sl.update_one(LyricTemp,{'$set':LyricTemp},upsert=True)
        print(result)


client = pymongo.MongoClient(host='localhost', port=27017)
db = client['Song']
sl = db['songListFull']
for x in sl.find():
    print(x)
    getLyric(x)
