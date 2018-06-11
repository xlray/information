import logging
import redis


class Config(object):
    SECRET_KEY = "DAJSKFJAOXKSAOKOSA"
    #数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql@127.0.0.1:3306/information31'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #redis配置
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    #session配置
    SESSION_TYPE = 'redis'
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(REDIS_HOST,REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 3600*24*2 #设置session有效时间
    #默认日志等级
    LEVEL = logging.DEBUG
#开发模式

class DeveloperConfig(Config):
    DEBUG = True
    LEVEL = logging.INFO

#生产环境

class ProductConfig(Config):
    DEBUG = False

#测试环境

class TestConfig(Config):
    pass

Config_dict = {
    "develop":DeveloperConfig,
    "product":ProductConfig,
    "test":TestConfig
}
