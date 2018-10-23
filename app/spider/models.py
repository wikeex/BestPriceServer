import time
import sqlite3
from .smzdm import download, resolve


class Keywords:
    """
    该类用来接收关键词并储存管理。储存在sqlite3数据库中。
    """
    def __init__(self, open_id, database):
        self.open_id = open_id
        self.database = database

        # 如果数据库中没有user表则新建user表
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        try:
            cur.execute('SELECT * FROM user')
        except sqlite3.OperationalError as e:
            cur.execute('''
                    CREATE TABLE user (
                    open_id TEXT NOT NULL ,
                    keyword TEXT UNIQUE NOT NULL ,
                    insert_time FLOAT NOT NULL 
                    );
                    ''')
            conn.commit()
            conn.close()

    def add(self, *keywords):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()

        add_failed = list()
        for keyword in keywords:
            try:
                cur.execute(
                    'INSERT INTO user (open_id, keyword, insert_time) VALUES (?, ?, ?)',
                    (self.user, keyword, time.time())
                )
            except sqlite3.OperationalError as e:
                # 捕获到异常说明keyword已存在数据库中，continue跳过
                add_failed.append(keyword)
                continue
        conn.commit()
        conn.close()
        return 'success' if add_failed is None else tuple(add_failed)

    def delete(self, *keywords):
        conn = sqlite3.connect(self.database)
        cur = conn.cursor()
        for keyword in keywords:
            cur.execute('DELETE FROM user WHERE open_id = ? AND keyword = ?', (self.open_id, keyword))
        conn.commit()
        conn.close()
        return 'success'

    @staticmethod
    def fetchall(database):
        conn = sqlite3.connect(database)
        cur = conn.cursor()
        cur.execute('SELECT keyword FROM user')
        keywords = set(cur.fetchall()[0])
        conn.commit()
        conn.close()

        return list(keywords).remove(None) if None in list(keywords) else list(keywords)

    @staticmethod
    def add_user(items_q, database):
        conn = sqlite3.connect(database)
        cur = conn.cursor()

        # 包含目标用户open_id的产品信息列表，用来给微信模块向用户推送业务消息
        to_send_items = list()
        for item in items_q:
            if item is not None:
                keyword = item.get('keyword')
                cur.execute('SELECT open_id FROM user WHERE keyword = ?', (keyword,))
                users = cur.fetchall()[0]
                item['user'] = tuple(users)
                to_send_items.append(item)
            else:
                continue
        conn.commit()
        conn.close()

        return tuple(to_send_items)


class Items:
    """
    该类用来爬取、储存和管理商品信息。构造时将关键词传入，实例方法将根据这些关键词进行操作。
    """
    def __init__(self, *keywords, smzdmdata):
        self.keywords = tuple(keywords)
        self.collection = smzdmdata.items

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

    def remove(self):
        for keyword in self.keywords:
            self.collection.remove({'keyword': keyword})

    @staticmethod
    def delete(*keywords, smzdmdata):
        for keyword in keywords:
            smzdmdata.items.remove({'keyword': keyword})

    @staticmethod
    def query(keyword):
        pages = download([keyword])
        items = resolve(pages=pages)
        return items
