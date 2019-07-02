# -*- coding: utf-8 -*-
import scrapy,re,json,time
from scrapy.http import Request
from Huya.items import HuyaItem

class HuyaspiderSpider(scrapy.Spider):
    name = 'huyaspider'
    allowed_domains = ['www.huya.com']#设置爬虫允许抓取的
    start_urls = ['http://www.huya.com/g']#设置第一个爬取的url
    allow_pagenum = 5;   #设置爬取频道的数量
    total_pagenum = 0;   #计算档前已爬取频道的数量
    url_dict={}       #设置存放url的dict

    def parse(self, response):#获取虎牙下所有频道的url 、频道id  、频道名称
        parse_content = response.xpath('/html/body/div[2]/div/div/div[2]/ul/li')  # 抓取当前频道
        for i in parse_content:#
            channel_title = i.xpath('a/h3/text()').extract()  # 抓取频道名称
            channel_title = channel_title[0]

            channel_url = i.xpath('a/@href').extract_first()  # 抓取当前频道url
            channel_id = i.xpath('a/@report').re(r'game_id\D*(.*)\D\}')  # 抓取当前频道对应的id，用正则去掉不需要部分
            channel_data = {"url": channel_url, "channel_id": channel_id[0]}  # 将频道url和频道id组成一一对应的dict

            if self.total_pagenum <= self.allow_pagenum:  # 用于控制爬出抓取数量，当total_pagenum小于allow_pagenum 继续爬
                self.total_pagenum += 1
                yield Request(url=channel_url, meta={'channel_data': channel_data, 'channel': channel_title},
                              callback=self.channel_get)
                # 使用request，meta携带数据为频道url，频道id，回调函数为channel_get

    def channel_get(self, response):
        #def parse的回调函数，根据频道id构造主播数据连接并执行请求
        page_num = int(response.xpath(
            '/html/body/div[2]/div/div/div["js-list-page"]/div[1]/@data-pages').extract_first())
        # 抓取当前频道一共有多少页，并转为int格式
        channel_id = response.meta['channel_data'][
            'channel_id']  # 将传入meta的dict（channel_data）中的channel_id值赋给channel_id，该id用于构造url从而实现翻页
        channel = response.meta['channel']  # 将传入的meta的dict中的channel值赋给channel
        for i in range(1, page_num + 1):  # 根据page_num数量构造"下一页"并继续抓取
            url = 'http://www.huya.com/cache.php?m=LiveList&do=getLiveListByPage&gameId={gameid}&tagAll=0&page={page}'.format(
                gameid=channel_id, page=i)  # 获取下一页的json数据
            yield Request(url=url, meta={'page': i, 'channel': channel},
                          callback=self.channel_parse)  # meta携带数据为频道当前页码，频道名称，回调函数为channel_parse

    def channel_parse(self, response):
        #channel_get 的回调函数，根据返回的json数据抓取相应内容，并抓出主播的房间链接，对房间链接执行请求
        response_json = json.loads(response.text)  # 利用json.loads将json数据转为字典
        channel = response.meta['channel']
        for i in response_json['data']['datas']:
            items = HuyaItem()  # 实例化item.HuyaItem
            items['channel'] = channel  # 获取频道名称
            items['watch_num'] = int(i['totalCount'])  # 获取观看数量 设置为整数方便排序
            items['anchor_roomname'] = i['roomName']  # 获取房间名称
            items['anchor_url'] = 'http://www.huya.com/' + i['privateHost']
            items['anchor_name'] = i['nick']  # 获主播名称
            yield Request(url=items['anchor_url'], meta={'items': items},
                          callback=self.room_parse)#重跳转问题修复, dont_filter=True
            # 进入主播房间url获取主播订阅数量，meta携带数据为刚抓取的items，回调函数为room_parse

    def room_parse(self, response):#channel_parse的回调函数，抓取主播的订阅数量
        items = response.meta['items']
        is301 = response.xpath('//p[@class="error-tip"]/a/@href').extract_first()
        if is301 is None:
            yield Request(url=items['anchor_url'], meta={'items': items},
                          callback=self.room_parse2)  # 重跳转问题修复
        else:
            items['anchor_url'] = is301
            yield Request(url=items['anchor_url'], meta={'items': items},
                          callback=self.room_parse2)  #重跳转问题修复

    def room_parse2(self, response):
        items = response.meta['items']
        items['fan_num'] = int(response.xpath('//div[@class="subscribe-count"]/text()').extract_first()) # 获取主播订阅数量
        items['crawl_time'] = time.strftime('%Y-%m-%d %X', time.localtime())  # 记录爬取时间
        yield items  # 输出items