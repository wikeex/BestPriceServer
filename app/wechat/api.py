from flask import request, current_app
from ..wechat import wechat
import hashlib


@wechat.route('/auth', methods=['GET', 'POST'])
def auth():
    auth_args = list()

    auth_args.append(request.args.get('timestamp')) if request.args.get('timestamp') is not None else ...
    auth_args.append(request.args.get('nonce')) if request.args.get('nonce') is not None else ...
    signature = request.args.get('signature') if request.args.get('signature') is not None else ...
    echostr = request.args.get('echostr')

    if current_app.config.get('WECHAT_TOKEN') is not None:
        auth_args.append(current_app.config.get('WECHAT_TOKEN'))
    else:
        raise RuntimeError('WECHAT_TOKEN not set')

    temp_string = ''.join(sorted(auth_args))
    sign_calc = hashlib.sha1(temp_string.encode('utf-8')).hexdigest()

    if sign_calc == signature:
        return echostr
    else:
        return 'no response'
