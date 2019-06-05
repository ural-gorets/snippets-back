from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://test_task:qwertyu@localhost:5432/db"    # EDIT THIS!!!!
    # basedir = os.path.dirname(__file__)  #migr
    # SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repo') #migr
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'some-secret-string'
    FLASK_ENV = 'development'


app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r'/*': {'origins': '*'}})    # http://localhost:8080

api = Api(app)
db = SQLAlchemy(app)

import models
import resources as res

api.add_resource(res.Wall, '/')
api.add_resource(res.Snippet, '/snippet/<snippet_ref>')
api.add_resource(res.Upload, '/upload')
api.add_resource(res.Test, '/test')

@app.before_first_request
def create_tables():
    db.create_all()
