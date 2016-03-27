from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import use_args
from flask.ext.restful import abort

from app.models.users import User
from app.common.errors import error_enum
from app.common.util import Util

user_activity_preference_args = {
    'run': fields.Int(missing=1),
    'jog': fields.Int(missing=1),
    'walk': fields.Int(missing=1),
    'bike': fields.Int(missing=1),
    'gym': fields.Int(missing=1),
    'sport': fields.Int(missing=1),
    'hike': fields.Int(missing=1),
    'aerobic': fields.Int(missing=1),
    'dance': fields.Int(missing=1),
    'yoga': fields.Int(missing=1),
    'swim': fields.Int(missing=1)
}
user_args_put = {
    'first_name': fields.Str(required=True),
    'last_name': fields.Str(required=True),
    'points': fields.Int(missing=0),
    'weight': fields.Int(required=True),
    'height': fields.Int(required=True),
    'dob': fields.Str(required=True),
    'gender': fields.Str(required=True),
    'email': fields.Str(required=True),
    'contact_number': fields.Int(required=True),
    'injuries': fields.Str(missing=''),
}
user_args_post = user_args_put.copy()
user_args_post.update({
    'user_id': fields.Str(required=True),
    'activity_preferences': fields.Nested(user_activity_preference_args, required=True)
})


class UserController(Resource):
    def get(self, user_id=None):
        if not user_id:
            abort(http_status_code=404, error_code=error_enum.user_id_missing)
        result = User.get_user(user_id)
        if result:
            for record in result:
                record['dob'] = str(record['dob'])
        else:
            abort(http_status_code=400, error_code=error_enum.user_id_not_found)
        return result

    @use_args(user_args_post)
    def post(self, args):
        activity_pref = args.pop('activity_preferences')
        user_details = args
        user_id = User.insert_user(user_details)
        if user_id is -1:
            abort(http_status_code=400, error_code=error_enum.user_id_duplicate)
        User.insert_user_activity_pref(user_id, activity_pref)
        return {'user_id': user_id}

    @use_args(user_args_put)
    def put(self, args, user_id):
        if User.update_user(args, user_id) is -1:
            abort(http_status_code=500, error_code=error_enum.database_error_updating)
        return None, 204


class UserPreferenceController(Resource):
    def get(self, user_id):
        if not user_id:
            abort(http_status_code=404, error_code=error_enum.user_id_missing)
        result = User.get_user_activity_pref(user_id)
        if not result:
            abort(http_status_code=400, error_code=error_enum.user_id_not_found)
        return result

    @use_args(user_activity_preference_args)
    def put(self, args, user_id):
        if not user_id:
            abort(http_status_code=404, error_code=error_enum.user_id_missing)
        if User.set_user_activity_pref(user_id, args) is -1:
            abort(http_status_code=500, error_code=error_enum.database_error_updating)
        return None, 204


class UserConnectionsController(Resource):
    user_args_connections = {
        'connections': fields.List(fields.Str())
    }

    def get(self, user_id):
        return {'connections': User.get_user_connections(user_id)}

    @use_args(user_args_connections)
    def post(self, args, user_id):
        contacts = []
        for contact in args['connections']:
            if Util.is_valid_contact_number(contact):
                contacts.append(Util.clean_contact_number(contact))
        User.set_user_connections(user_id, contacts)
        return None, 202
