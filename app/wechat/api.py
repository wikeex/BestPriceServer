from flask import request
from ..wechat import wechat
from config import Config
import hashlib


@wechat.route('/auth')
def auth():
    auth_args = list()

    auth_args.append(request.args.get('timestamp'))
    auth_args.append(request.args.get('nonce'))
    signature = request.args.get('signature')
    echostr = request.args.get('echostr')

    token = Config.WECHAT_TOKEN
    auth_args.append(request.args.get(token))

    temp_string = ''.join(sorted(auth_args))
    sign_calc = hashlib.sha1(temp_string).hexdigest()

    if sign_calc == signature:
        return echostr
