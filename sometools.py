import werobot
import requests
from app.models import Keywords, Items, Database
from threading import Timer
from config import Config

robot = werobot.WeRoBot(token=Config.TOKEN, app_id=Config.APP_ID, app_secret=Config.APP_SECRET)


@robot.text
def hello(message):
    userkeywords = Keywords(user=message.source, smzdmdata=dbclient.smzdmdata)

    if '~~' in message.content:
        return userkeywords.add(message.content.strip('~'))
    elif '立即查询' in message.content:
        item = Items.query(message.content.strip('立即查询 '))
        return str(item)
    else:
        return '在关键词前面或者后面添加“~~”以监控关键词，发送“立即查询”立即查询已添加的关键词'


@robot.handler
def template(return_code):
    if type(return_code) == werobot.messages.events.TemplateSendJobFinishEvent:
        print(return_code.status)
    return None


def timing_task():
    timer = Timer(1800, timing_task)
    timer.start()

    modelID = Config.MODEL_ID
    json_data = dict()
    json_data['template_id'] = modelID
    access_token = robot.client.get_access_token()
    url = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={0}'.format(access_token)

    all_items = Items(*Keywords.fetchall(dbclient.smzdmdata), smzdmdata=dbclient.smzdmdata)
    lowest = all_items.task()
    if lowest:
        for item in lowest:
            users = Keywords.user(item[2], dbclient.smzdmdata)
            print(users)
            for user in users:
                json_data['data'] = {'name': {'value': item[0]['name'], 'color': '#173177'},
                                     'period': {'value': item[1], 'color': '#173177"'},
                                     'price': {'value': item[3], 'color': '#173177"'}}
                json_data['url'] = item[0]['smzdm_link']
                json_data['touser'] = user
                respones = requests.post(url=url, json=json_data)
                print(respones.json())


if __name__ == '__main__':
    robot.config['HOST'] = '127.0.0.1'
    robot.config['PORT'] = 5000
    dbclient = Database()
    timer = Timer(1800, timing_task)
    timer.start()
    robot.run()

