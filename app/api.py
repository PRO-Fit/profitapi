from app import app
from flask.ext.restful import Api

from common.api_config.user import user_api_config
from common.api_config.calendar import calendar_api_config

api = Api(app)

for config in user_api_config + calendar_api_config:
    api.add_resource(config.get('endpoint'), *config.get('routes'))
