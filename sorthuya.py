# -*- coding: utf-8 -*-
import pymongo

myclient = pymongo.MongoClient('localhost', 27017)  # 创建mongodb连接
mydb = myclient['huya']  # 创建mongodb数据库huya
mycol = mydb['huyaanchor']  # 创建数据库huya中collection

def sorthuya(int):#降序排序
    mydoc = mycol.find().sort("watch_num", -1)

j = 1#序列号
k = 0#总数
for x in mycol:
    k += x["watch_num"]
    print(x)
    print(j)
    j += 1
print("总数：", k)
 # for i in mycol.find({'watch_num':{'$type':2}}):
 #     print(j)
 #     j+=1
 #     print(i)