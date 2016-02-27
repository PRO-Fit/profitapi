from app import app
from flask.ext.restful import Api

import controllers.users

api = Api(app)
api.add_resource(controllers.users.UserController, '/v1/users')
