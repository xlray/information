#coding:utf8
#装饰视图函数
from flask import current_app
from flask import render_template

from info import redis_store
from . import index_blu


@index_blu.route('/',methods=['GET','POST'])
def index():
    redis_store.set('name',"banzhang")
    name = redis_store.get('name')
    print(name)
    return render_template('news/index.html')

#每个网站都会设置/favicon.ico小图标
@index_blu.route('/favicon.ico')
def web_logo():
    return current_app.send_static_file('news/favicon.ico')