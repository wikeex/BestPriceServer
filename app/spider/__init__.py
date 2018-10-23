import requests
from queue import Queue
from pymongo import MongoClient
from threading import Timer
from datetime import datetime
from .smzdm import smzdm
from .models import Items, Keywords


class ImproperlyConfiguredError(Exception):
    """Exception for error on configurations."""
    pass


class Spider:
    def __init__(self, app=None):
        self.config_prefix = None
        self.mongo = None
        self.items_queue = Queue()
        if app is not None:
            self.app = app
            self.init_app(self.app)

    def init_app(self, app, config_prefix='SPIDER_DATABASE'):
        self.app = app
        self.config_prefix = config_prefix

        def key(suffix):
            return '%s_%s' % (config_prefix, suffix)
        database_login = dict()
        if key('URI') not in self.app.config:
            raise ImproperlyConfiguredError("You should provide a database name "
                                            "(the %s setting)." % key('URI'))
        else:
            database_login['host'] = self.app.config['%s_%s' % (self.config_prefix, 'URI')]

        # 读取设置文件中商品数据库配置并新建pymongo客户端
        suffixes = ['PORT', 'USERNAME', 'PASSWORD', 'AUTH_SOURCE', 'AUTH_MECHANISM']
        configs = ['port', 'username', 'password', 'authSource', 'authMechanism']
        map(
            lambda x, y: database_login.update(dict(y=self.app.config[key(x)])) if key(x) in self.app.config else ...,
            suffixes,
            configs
        )
        self.mongo = MongoClient(**database_login)

        crawling = Timer(1800, self._crawling_task)
        crawling.start()
        wechat = Timer(1800, self._wechat_task)
        wechat.start()

    def _crawling_task(self):
        """
        每隔30分钟爬取商品把商品信息保存到数据库, 并比较此次爬取的价格在历史记录中的水平，如果是历史最低就向items_queue消息队列中添加。
        :return:
        """
        # 使用Timer实现的循环定时器任务
        timer = Timer(1800, self._crawling_task)
        timer.start()

        # 关键词数据库读取所有关键词
        items = Items(*Keywords.fetchall(self.mongo), smzdmdata=self.mongo)

        # 在什么值得买网站爬取商品信息
        items_detail = smzdm(items.keywords)

        output_items = list()
        for item in items_detail:
            # 存入商品信息到数据库中
            item.setdefault('store_time', datetime.utcnow())
            self.mongo.items.update({'$push': item}, True)

            # 检查本次查询是否为历史最低，如果是则输出
            lowest_price = self.collection.find_one({'keyword': item['keyword'], 'price': {'$gt': item['price']}})
            if lowest_price:
                continue
            else:
                output_items.append(item)

        # 增加用户open_id到输出数据中
        to_wechat_task = Keywords.add_user(output_items, self.app.config['DATABASE_PATH'])

        self.items_queue.put(tuple(to_wechat_task))

    def _wechat_task(self):
        """
        每隔30分钟从items_queue队列中取商品信息，如果哪个关键词对应的值不为None就向用户发送业务消息。
        :return:
        """
        # 使用Timer实现的循环定时任务
        timer = Timer(1800, self._wechat_task)
        timer.start()

        to_send = self.items_queue.get()
        json_data = dict()
        json_data['template_id'] = self.app.config['MODEL_ID']

        access_token = self.app.get_access_token()
        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={0}'.format(access_token)
        if to_send:
            for item in to_send:
                for user in item['user']:
                    json_data['data'] = {'name': {'value': item['name'], 'color': '#173177'},
                                         'price': {'value': item['price'], 'color': '#173177"'}}
                    json_data['url'] = item['smzdm_link']
                    json_data['touser'] = user
                    respones = requests.post(url=url, json=json_data)
                    assert respones.json().get('errcode') == 0
