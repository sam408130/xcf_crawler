# -*- coding: utf-8 -*-

import re
import config
import utils

from scrapy.spiders import CrawlSpider
from scrapy import Request
from scrapy.selector import Selector
from sqlhelper import SqlHelper
import datetime

class ItemDetail(CrawlSpider):
    name = "item_list"
    base_url = "http://www.xiachufang.com"
    header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
            'Connection': 'keep-alive',
            'Host': 'www.xiachufang.com',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0',
    }
    def __init__(self, *a , **kw):
        super(ItemDetail, self).__init__(*a, **kw)

        self.dir_name = 'log/%s' % self.name
        self.sql = SqlHelper()
        self.init()
        utils.make_dir(self.dir_name)


    def init(self):
        command = (
            "CREATE TABLE IF NOT EXISTS {} ("
            "`id` INT(8) NOT NULL AUTO_INCREMENT,"
            "`name` CHAR(20) NOT NULL COMMENT '菜肴名称',"
            "`url` TEXT NOT NULL COMMENT '菜肴url',"
            "`img` TEXT NOT NULL COMMENT '封面图',"
            "`item_id` INT(8) NOT NULL COMMENT '菜肴id',"
            "`source` TEXT NOT NULL COMMENT '原料',"
            "`score` CHAR(5) NOT NULL COMMENT '平分',"
            "`create_time` DATETIME NOT NULL,"
            "PRIMARY KEY(id),"
            "UNIQUE KEY `item_id` (`item_id`)"
            ") ENGINE=InnoDB".format(config.item_list_table)
        )

        self.sql.create_table(command)

    def start_requests(self):
        command = "SELECT * from {}".format(config.category_urls_table)
        data = self.sql.query(command)

        for i, category in enumerate(data):
            url = self.base_url + category[2]
            utils.log(url)
            yield Request(
                url = url,
                headers = self.header,
                callback = self.parse_all,
                errback = self.error_parse,
            )


    def parse_all(self, response):
        utils.log(response.url)
        if response.status == 200:
            file_name = '%s/category.html' % (self.dir_name)
            self.save_page(file_name, response.body)
            recipes = response.xpath("//div[@class='normal-recipe-list']/ul/li").extract()
            self.parse_recipes(recipes)
            nextPage = response.xpath("//div[@class='pager']/a[@class='next']/@href").extract_first()
            if nextPage:
                yield Request(
                    url = self.base_url + nextPage,
                    headers = self.header,
                    callback = self.parse_all,
                    errback = self.error_parse,
                )

    def parse_recipes(self, recipes):
        for recipe in recipes:
            sel = Selector(text = recipe)
            name = sel.xpath("//p[@class='name']/text()").extract_first().strip()
            url = sel.xpath("//a[1]/@href").extract_first()
            img = sel.xpath("//div[@class='cover pure-u']/img/@data-src").extract_first()
            item_id = re.compile("/recipe/(.*?)/").findall(url)[0]
            source = sel.xpath("//p[@class='ing ellipsis']/text()").extract_first().strip()
            score = sel.xpath("//p[@class='stats']/span/text()").extract_first().strip()
            dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            msg = (None, name, url, img, item_id, source, score, dt)
            command = ("INSERT IGNORE INTO {} "
                        "(id, name, url, img, item_id, source, score, create_time)"
                        "VALUES(%s,%s,%s,%s,%s,%s,%s,%s)".format(config.item_list_table)
            )
            self.sql.insert_data(command, msg)

    def error_parse(self, faiture):
        request = faiture.request
        utils.log('error_parse url:%s meta:%s' % (request.url, request.meta))


    def save_page(self, file_name, data):
        with open(file_name, 'w') as f:
            f.write(data)
            f.close()
