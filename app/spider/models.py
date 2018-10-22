import smzdm
import datetime
import pymongo


class Message:
    def __init__(self):
        ...


class Database:
    def __init__(self):
        self.client = pymongo.MongoClient('booop.xyz', 27017, username='manager', password='mongo7898529',
                                     authSource='smzdmdata')
        self.smzdmdata = self.client.smzdmdata


class Keywords:
    """
    该类用来接收关键词并储存管理。储存在Database类中连接的MongoDB数据库中。user为发送消息的微信openID，每个user作为关键词的key，
    关键词以列表形式作为字典的值。
    """
    def __init__(self, user, smzdmdata):
        self.user = user
        self.collection = smzdmdata.keywords

    def add(self, *keywords):
        userkeywordslist = self.collection.find({'user': self.user})
        invalid = ''
        for keyword in keywords:
            if keyword in userkeywordslist or not keyword:
                invalid = invalid + keyword + ','
        self.collection.update({'user': self.user}, {'$pushAll': {'values': keywords}}, True)
        return ('关键词"{0}"已存在或无效, 其他关键词添加成功！'.format(invalid.rstrip(',')) if invalid else '全部关键词添加成功！')

    def delete(self, *keywords):
        userkeywordslist = self.collection.find({'user': self.user})
        invalid = ''
        for keyword in keywords:
            if keyword not in userkeywordslist or not keyword:
                invalid = invalid + keyword + ','
        self.collection.update({'user': self.user}, {'$pull': {'values': keyword}})
        return ('关键词"{0}"不已存在或无效, 其他关键词删除成功！'.format(invalid.rstrip(',')) if invalid else '全部关键词删除成功！')

    @staticmethod
    def fetchall(smzdmdata):
        data = smzdmdata.keywords.find()
        keywords = set()
        for user in data:
            if user.get('values'):
                keywords = keywords | set(user.get('values'))
        return list(keywords).remove(None) if None in list(keywords) else list(keywords)

    @staticmethod
    def user(keyword, smzdmdata):
        data = smzdmdata.keywords.find({'values': keyword})
        userlist = list()
        for user in data:
            print(user)
            userlist.append(user['user'])
        return userlist


class Items:
    """
    该类用来爬取、储存和管理商品信息。构造时将关键词传入，实例方法将根据这些关键词进行操作。
    """
    def __init__(self, *keywords, smzdmdata):
        self.keywords = keywords
        self.collection = smzdmdata.items

    def spider(self):
        pages = smzdm.download(keywords=self.keywords)
        items = smzdm.resolve(pages=pages)
        return items

    def store(self, items):
        for keyword in items:
            items[keyword].setdefault('store_time', datetime.datetime.utcnow())
            self.collection.update({'keyword': keyword}, {'$push': {'values': items[keyword]}}, True)

    def fetch(self):
        """
        返回self.keywords历史数据中价格最低和最近一次的商品数据。
        :return:
        """
        outputs = list()
        for keyword in self.keywords:
            itemslist = self.collection.find_one({'keyword': keyword})['values']
            for item in itemslist:
                if item['price'] < temp['price']:
                    temp = item
            outputs.append((temp, itemslist[-1]))

        return tuple(outputs)

    def task(self, period=0):
        """
        task任务爬取商品把商品信息保存到数据库并比较此次爬取的价格在历史记录中的水平，如果是历史最低就返回商品信息。
        :return:
        """
        items = self.spider()
        self.store(items)
        output_items = list()
        for keyword in items:
            if period:
                starttime = items[keyword]['store_time'] - datetime.timedelta(days=period)
                itemslist = self.collection.find({'keyword': keyword, 'values.store_time': {'$gt': starttime}})
            else:
                itemslist = self.collection.find({'keyword': keyword})
                deltatime = items[keyword]['store_time'] - self.collection.find_one({'keyword': keyword})['values'][0]['store_time']
                period = deltatime.days

            for item in list(itemslist)[:-1]:
                # item['price'] 为此次爬取的价格，只有此次爬取的价格低于历史价才会输出
                if item['price'] >= items[keyword]['price']:
                    break
            else:
                # 输出item在period天内价格最低
                output_items.append((items[keyword], period, keyword, '{0:.2f}元'.format(str(items[keyword]['price']))))
        return output_items

    def remove(self):
        for keyword in self.keywords:
            self.collection.remove({'keyword': keyword})

    @staticmethod
    def delete(*keywords, smzdmdata):
        for keyword in keywords:
            smzdmdata.items.remove({'keyword': keyword})

    @staticmethod
    def query(keyword):
        pages = smzdm.download([keyword])
        items = smzdm.resolve(pages=pages)
        return items
