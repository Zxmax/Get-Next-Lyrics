#!/usr/bin/python
# -*- coding:utf-8 -*-
from pymongo import MongoClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import datetime
import json
from fuzzywuzzy import fuzz

# 一次同步的数据量，批量同步
syncCountPer = 100000
# Es 数据库地址
es_url = 'localhost:9200'
# mongodb 数据库地址
mongo_url = 'localhost:27017'
# mongod 需要同步的数据库名
DB = 'song'
# mongod 需要同步的表名
COLLECTION = 'songLyricFull'
es = Elasticsearch(es_url, port=9200)
conn = MongoClient(mongo_url, 27017)


def connect_db():
    count = 0
    db = conn['Song']
    sl = db['songLyricFull']
    syncDataLst = []
    mongoRecordRes = sl.find()
    for record in mongoRecordRes:
        count += 1
        # 因为mongodb和Es中，对于数据类型的支持是有些差异的，所以在数据同步时，需要对某些数据类型和数据做一些加工
        # 删掉 url 这个字段
        record.pop('url', '')
        # Es中不支持 float('inf') 这个数据， 也就是浮点数的最大值
        #if record['rank'] == float('inf'):
        #record['rank'] = 999999999999

        syncDataLst.append({
            "_index": DB,               # mongod数据库 == Es的index
            "_type": COLLECTION,        # mongod表名 == Es的type
            "_id": str(record.pop('_id')),
            "_source": record,
        })

        if len(syncDataLst) == syncCountPer:
            # 批量同步到Es中，就是发送http请求一样，数据量越大request_timeout越要拉长
            bulk(es, syncDataLst, request_timeout=180)
            # 清空数据列表
            syncDataLst[:] = []
            print(f"Had sync {count} records at {datetime.datetime.now()}")
            # 同步剩余部分
    if syncDataLst:
        bulk(es, syncDataLst, request_timeout=180)
        print(f"Had sync {count} records rest at {datetime.datetime.now()}")


def search(lyric):
    dsl = {
        'query': {
            "match_phrase": {'lyric': lyric}
        }
    }
    dsl2={
        'query': {"match": {'lyric': lyric}
        }
    }

    result = es.search(index=DB, doc_type=COLLECTION, body=dsl)

    if (len(result['hits']['hits']) == 0):
        result = es.search(index=DB, doc_type=COLLECTION, body=dsl2)
    if (len(result['hits']['hits']) > 0):
        lyricF = result['hits']['hits'][0]['_source']['lyric']
        lyricF = lyricF.split('[')
        for i in range(len(lyricF)):
            lyricC = lyricF[i]
            if(']' in lyricC and not lyricC.endswith(']')):
                lyricF[i] = lyricC[lyricC.index(']')+1:]
        lyricF = [i for i in lyricF if i != '\n']
        lyricF_r = []
        for j in range(len(lyricF)):
            ratio = fuzz.ratio(lyric, lyricF[j])
            lyricF_r.append(ratio)
        if(lyricF_r.index(max(lyricF_r)) == len(lyricF_r)-1):
            lyricF_r[lyricF_r.index(max(lyricF_r))
                     ] = lyricF_r[lyricF_r.index(min(lyricF_r))]
        res = lyricF[lyricF_r.index(max(lyricF_r))]
        res.replace(' ', '')
        if(res.startswith(lyric) and len(res)-1 > len(lyric)):
            res = res.replace(lyric, '',1)
            return res
        else:
            res = lyricF[lyricF_r.index(max(lyricF_r))+1]
        if(lyricF[lyricF_r.index(max(lyricF_r))] != lyric+'\n'):
            res = lyricF[lyricF_r.index(max(lyricF_r))]+res
        if('&apos;' in res):
            res = res.replace('&apos;', "\'")
        print(res)
        return res
    return "无匹配"
    

#connect_db()
search('更怕你永远停留在这里')

