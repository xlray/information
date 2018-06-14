#coding:utf8
#装饰视图函数
from flask import current_app
from flask import render_template
from flask import session

from info import constants
from info.models import User, News
from . import index_blu



@index_blu.route('/',methods=['GET','POST'])
def index():
    # redis_store.set('name',"banzhang")
    # name = redis_store.get('name')
    # print(name)
    #查询用户编号
    user_id = session.get('user_id')
    #查询用户对象
    user = None
    if user_id:
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    #查询数据库，按照点击量,前十名的新闻
    try:
        click_news = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS).all()

    except Exception as e:
        current_app.logger.error(e)

    #将对象列表转换为字典
    click_news_list = []
    for news in click_news:
        click_news_list.append(news.to_dict())

    #对象是无法返回到模板页面，必须先转换成字典
    data = {
        "user_info":user.to_dict() if user else None,
        "click_news_list":click_news_list
    }
    #返回数据对象到模板页面
    return render_template('news/index.html',data = data)



#每个网站都会设置/favicon.ico小图标
@index_blu.route('/favicon.ico')
def web_logo():
    return current_app.send_static_file('news/favicon.ico')