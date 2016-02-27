from flask import Flask
from flask.ext.log import Logging

app = Flask(__name__)
app.config['FLASK_LOG_LEVEL'] = 'DEBUG'
flask_log = Logging(app)