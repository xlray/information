import logging
from flask import current_app

from flask import session
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from info import create_app, db,models

app = create_app('develop')

manager = Manager(app)
Migrate(app,db)
manager.add_command('db',MigrateCommand)

if __name__ == '__main__':
    manager.run()