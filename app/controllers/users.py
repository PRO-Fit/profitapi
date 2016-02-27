from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import use_args
from flask.ext.restful import abort

from app.models.users import User


class UserController(Resource):
    user_args_post = {
        'first_name': fields.Str(required=True),
        'last_name': fields.Str(required=True),
        'points': fields.Int(missing=0),
        'weight': fields.Int(required=True),
        'height': fields.Int(required=True),
        'dob': fields.Str(required=True),
        'gender': fields.Str(required=True),
        'email': fields.Str(required=True),
        'contact_number': fields.Int(required=True),
        'injuries': fields.Str(missing='')
    }
    user_args_get = {
        'user_id': fields.Int(required=True)
    }

    @use_args(user_args_get)
    def get(self, args):
        result = User.get_user(args['user_id'])
        if result:
            for record in result:
                record['dob'] = str(record['dob'])
        else:
            abort(http_status_code=400)
        return result

    @use_args(user_args_post)
    def post(self, args):
        return {'user_id': User.insert_user(args)}
