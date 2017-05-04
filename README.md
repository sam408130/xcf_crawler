# xcf_crawler
爬取下厨房首页全部分类下的所有菜品

### 项目依赖库
* scrapy
* mysql-connector
* BeautifulSoup
* lxml

### 抓取流程
1. 首先爬去下厨房首页全部分类下的所有分类链接
2. 逐个爬取分类下的所有菜品

### 下载运行

```
$ git clone https://github.com/sam408130/xcf_crawler.git
```

进入目录
```
cd cook
```

修改数据库配置(打开本地数据库mysql.server start)

```
$ vim config.py
------------
database_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
}
```

编辑 main.py 先抓取 所有分类url

```
$ vim main.py
---------
cmdline.execute('scrapy crawl category_urls'.split())
# cmdline.execute('scrapy crawl item_list'.split())
```

待 urls 抓取完成后再抓取菜品信息

```
$ vim main.py
---------
# cmdline.execute('scrapy crawl category_urls'.split())
cmdline.execute('scrapy crawl item_list'.split())
```
运行爬虫抓取菜品信息

```
$ python main.py
```

