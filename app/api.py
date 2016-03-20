from app import app
from flask.ext.restful import Api
import controllers.users
import controllers.calendars

api = Api(app)
api.add_resource(controllers.users.UserController, '/v1/users', '/v1/users/<user_id>')












api.add_resource(controllers.calendars.CalendarController, '/v1/calendars/google/oauth2/<user_id>/<email>')
api.add_resource(controllers.calendars.CalendarRedirectController, '/v1/calendars/google/oauth2callback')