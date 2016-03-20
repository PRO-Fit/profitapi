from app import app
from flask.ext.restful import Api

import controllers.users
import controllers.goals

api = Api(app)
api.add_resource(controllers.users.UserController, '/v1/users', '/v1/users/<user_id>')
api.add_resource(controllers.goals.GoalController, '/v1/users/<user_id>/goals/<goal_id>', '/v1/users/<user_id>/goals')
