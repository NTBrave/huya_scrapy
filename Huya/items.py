# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HuyaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    channel = scrapy.Field() #主播所在频道
    anchor_name = scrapy.Field()#主播名称
    anchor_url = scrapy.Field()#直播房间链接
    anchor_roomname = scrapy.Field()#主播房间名称
    watch_num = scrapy.Field()#观看人数
    fan_num = scrapy.Field()#订阅人数
    crawl_time = scrapy.Field()#爬取时间

