#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
import json
import pymongo
import time


def gerSongByName(name,page):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['Song']
    sl=db['songListFull']
    url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp'
    for x in range(page):
        params = {
            'ct': '24',
            'qqmusic_ver': '1298',
            'new_json': '1',
            'remoteplace': 'txt.yqq.song',
            'searchid': '54207254756173652',
            't': '0',
            'aggr': '1',
            'cr': '1',
            'catZhida': '1',
            'lossless': '0',
            'flag_qc': '0',
            'p': str(x+1),
            'n': '10',
            'w': name['Name'],
            'g_tk_new_20200303': '5381',
            'g_tk': '5381',
            'loginUin': '0',
            'hostUin': '0',
            'format': 'json',
            'inCharset': 'utf8',
            'outCharset': 'utf-8',
            'notice': '0',
            'platform': 'yqq.json',
            'needNewCode': '0'
        }
        res = requests.get(url, params=params)
        json = res.json()
        if('data' in json):
            list = json['data']['song']['list']
            for song in list:
                print('歌曲ID:'+str(song['id']))
                songTemp={
                    'id':song['id'],
                    'name':song['name'],
                    'singer':name['Name'],
                    'album':song['album']['name'],
                    'link':'https://y.qq.com/n/yqq/song/'+song['mid']+'.html'
                }
                result=sl.update_one(songTemp,{'$set':songTemp},upsert=True)
                print(result)

client = pymongo.MongoClient(host='localhost', port=27017)
db = client['Song']
sl = db['singerList']
for x in sl.find().limit(5000):
    print(x)
    gerSongByName(x,2)
