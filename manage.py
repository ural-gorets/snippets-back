from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from run import app, db, Config

app.config.from_object(Config)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
'''
first run:
python manage.py db init

To perform migration run:
python manage.py db migrate

Then adjust "upgrade" function and run
python manage.py db upgrade 

'''