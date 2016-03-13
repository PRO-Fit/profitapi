from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import use_args
from flask.ext.restful import abort

from app.models.users import User
from app.common.errors import error_enum


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

    def get(self, id=None):
        if not id:
            abort(http_status_code=404, error_code=error_enum.user_id_missing)
        result = User.get_user(id)
        if result:
            for record in result:
                record['dob'] = str(record['dob'])
        else:
            abort(http_status_code=400, error_code=error_enum.user_id_not_found)
        return result

    @use_args(user_args_post)
    def post(self, args):
        return {'user_id': User.insert_user(args)}
