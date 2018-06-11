import logging
from flask import current_app

from flask import session
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from info import create_app, db

app = create_app('develop')

manager = Manager(app)
Migrate(app,db)
manager.add_command('db',MigrateCommand)


@app.route('/',methods=['GET','POST'])
def index():
    # session['name'] = 'zhangsan'

    logging.debug("调试信息AAAA")
    logging.info("详细信息AAAA")
    logging.error("错误信息AAAAA")
    current_app.logger.debug("调试信息BBBB")
    current_app.logger.error("错误信息BBBB")
    return "hello world!"
if __name__ == '__main__':
    manager.run()