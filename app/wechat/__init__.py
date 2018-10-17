from flask import Blueprint


wechat = Blueprint('wechat', __name__)

from . import api
