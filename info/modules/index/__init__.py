#coding:utf8
#创建蓝图对象
from flask import Blueprint

index_blu = Blueprint('index_blu',__name__)

from . import views