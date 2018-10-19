import requests
import lxml.html
import re


def download(keywords):
    """
    在没有cookies的情况下直接访问搜索链接会返回403错误,为了解决这个问题需要了解服务器如何构造cookies。
    根据服务器构造cookies的规则，直接访问搜索链接的响应头中Location字段有重定向url，访问这个重定向url会返回一个js脚本，这个脚本中
    有构造cookies的方法，构造好cookies再重新访问搜索链接可以得到返回页面。
    """
    if not keywords:
        return None

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Host": "search.smzdm.com",
        "Referer": "http://search.smzdm.com/?c=faxian&s=ducky",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    sess = requests.session()

    urls = {keyword: 'https://search.smzdm.com/?c=faxian&s=' + '+'.join(keyword.split(' ')) for keyword in keywords}
    print(urls)
    response = sess.get(urls[keywords[0]], headers=headers)
    redirect_url = response.history[0].headers.get('location')
    print(redirect_url)
    url_regex = re.compile(r'(?<=ss_ab=)(.+?)(?=&)')
    ss_ab_re = url_regex.search(redirect_url)
    ss_ab = ss_ab_re.group()
    cookie_dict = requests.utils.dict_from_cookiejar(sess.cookies)
    cookie_dict['ss_ab'] = ss_ab
    cookie_dict['path'] = '/'
    cookie_dict['domain'] = 'smzdm.com'
    print(cookie_dict)
    cookie = requests.utils.cookiejar_from_dict(cookie_dict)
    sess.cookies = cookie

    return {keyword: sess.get(urls[keyword], headers=headers).text for keyword in urls}


def resolve(pages):
    """
    该函数解析download()下载的什么值得买搜索页面，将页面上商品信息解析成字典格式并返回。
    :param pages: 由download()下载页面HTML文件
    :return: 商品信息字典
    """
    if pages is None:
        return None

    items = dict()
    for keyword in pages:
        compare_price = 10000000
        if pages[keyword]:
            tree = lxml.html.fromstring(pages[keyword])
            lis = tree.xpath('.//li[@class="feed-row-wide "]')

            for li in lis:
                spans = li.xpath('.//span/text()')
                if '好价频道' not in spans \
                    and '国内优惠' not in spans\
                        and '极速发' not in spans:
                        print(spans)
                        print('没有好价频道和国内优惠')
                        continue
                item_info = dict()
                item_info['image'] = li.xpath('.//img/@src')[0]
                item_info['name'] = li.xpath('.//h5/a/text()')[0].strip()
                item_info['price'] = li.xpath('.//h5/a[last()]/div/text()')[0]
                item_info['description'] = li.xpath('.//div[@class="feed-block-descripe"]/text()')[0].strip()
                item_info['smzdm_link'] = li.xpath('.//h5/a/@href')[0]

                price_regex = re.compile(r'^[￥¥$]?[0-9]+\.?[0-9]+')
                price_re = price_regex.search(item_info['price'])
                try:
                    item_info['price'] = float(price_re.group())
                except:
                    price_regex2 = re.compile(r'[0-9]+')

                    try:
                        price_re2 = price_regex2.search(price_re.group())
                        if '$' in price_re.group():
                            item_info['price'] = float(price_re2.group())*6.3
                        else:
                            item_info['price'] = float(price_re2.group())
                    except:
                        continue
                if compare_price > item_info['price']:
                    compare_price = item_info['price']

                    items[keyword] = item_info

    return items


if __name__ == '__main__':
    items = resolve(download(['ducky 3108', 'em10 mark ii']))
    for key in items:
        print(items[key])
