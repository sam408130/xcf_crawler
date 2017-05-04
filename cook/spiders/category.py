# -*- coding: utf-8 -*-

import re
import config
import utils


from scrapy.spider import Spider
from scrapy import Request
from scrapy.selector import Selector
from sqlhelper import SqlHelper
import datetime


class Category(Spider):
    name = "category_urls"

    start_url = 'http://www.xiachufang.com/category/'

    def __init__(self, *a , **kw):
        super(Category, self).__init__(*a, **kw)

        self.dir_name = 'log/%s' % self.name
        self.sql = SqlHelper()
        self.init()
        utils.make_dir(self.dir_name)


    def init(self):
        command = (
            "CREATE TABLE IF NOT EXISTS {} ("
            "`id` INT(8) NOT NULL AUTO_INCREMENT,"
            "`name` CHAR(20) NOT NULL COMMENT '分类名称',"
            "`url` TEXT NOT NULL COMMENT '分类url',"
            "`category` CHAR(20) NOT NULL COMMENT '父级分类',"
            "`category_id` INT(8) NOT NULL COMMENT '分类id',"
            "`create_time` DATETIME NOT NULL,"
            "PRIMARY KEY(id),"
            "UNIQUE KEY `category_id` (`category_id`)"
            ") ENGINE=InnoDB".format(config.category_urls_table)
        )

        self.sql.create_table(command)

    def start_requests(self):
        yield Request(
            url = self.start_url,
            headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, sdch',
                    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
                    'Connection': 'keep-alive',
                    'Host': 'www.xiachufang.com',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:51.0) Gecko/20100101 Firefox/51.0',
            },
            callback = self.parse_all,
            errback = self.error_parse,
        )


    def parse_all(self, response):
        if response.status == 200:
            file_name = '%s/category.html' % (self.dir_name)
            self.save_page(file_name, response.body)
            categorys = response.xpath("//div[@class='cates-list-all clearfix hidden']").extract()
            for category in categorys:
                sel_category = Selector(text = category)
                category_father = sel_category.xpath("//h4/text()").extract_first().strip()
                items = sel_category.xpath("//ul/li/a").extract()
                for item in items:
                    sel = Selector(text = item)
                    url = sel.xpath("//@href").extract_first()
                    name = sel.xpath("//text()").extract_first()
                    _id = re.compile('/category/(.*?)/').findall(url)[0]
                    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    msg = (None , name, url, category_father, _id, dt)
                    command = ("INSERT IGNORE INTO {} "
                                "(id, name, url, category, category_id, create_time)"
                                "VALUES(%s,%s,%s,%s,%s,%s)".format(config.category_urls_table)
                    )
                    self.sql.insert_data(command, msg)




    def error_parse(self, faiture):
        request = faiture.request
        utils.log('error_parse url:%s meta:%s' % (request.url, request.meta))


    def save_page(self, file_name, data):
        with open(file_name, 'w') as f:
            f.write(data)
            f.close()
