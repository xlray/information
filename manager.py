#coding:utf8
from flask import Flask

app = Flask(__name__)
# 从配置对象中加载配置
#app.config.from_pyfile('config.ini')
# 加载指定环境变量名称所对应的相关配置
# app.config.from_envvar('FLASKCONFIG')

@app.route('/')
def index():
    return "hello world!"

if __name__ == '__main__':
    app.run(debug=True)