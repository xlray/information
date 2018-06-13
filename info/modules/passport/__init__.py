#coding:utf8
from flask import Blueprint
#创建验证蓝图对象
passport_blu = Blueprint('passport_blu',__name__,url_prefix='/passport')
from . import views