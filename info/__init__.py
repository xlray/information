#coding:utf8
from logging.handlers import RotatingFileHandler

import logging
import redis
from flask import Flask

from flask.ext.session import Session
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import CSRFProtect

from config import Config, Config_dict


db = SQLAlchemy()
redis_store = None
def create_app(config_name):
    app = Flask(__name__)
    config = Config_dict[config_name]
    #调用日志方法
    log_file(config.LEVEL)
    app.config.from_object(config)
    db.init_app(app)
    global redis_store
    redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT,decode_responses=True)
    Session(app)
    # 设置CSRF程序保护
    # CSRFProtect(app)
    #首页蓝图注册app
    from info.modules.index import index_blu
    app.register_blueprint(index_blu)
    #验证蓝图注册app
    from info.modules.passport.views import passport_blu
    app.register_blueprint(passport_blu)
    return app

#设置日志信息作用：用来记录程序的运行过程，比如调试信息，访问接口信息，异常信息。
def log_file(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level) # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)