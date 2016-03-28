from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import use_args
from flask.ext.restful import abort
from app.common.errors import error_enum
from app.models.sessions import SessionModel


class UserSessionController(Resource):

      session_args_post = {
        'user_id': fields.Str(required=True),
        'workout_type_id': fields.Str(required=True),
        'start_datetime': fields.Str(required=True),
        'end_datetime': fields.Int(missing=0),
        'session_feedback_id': fields.Int(required=False),
        'is_accepted': fields.Int(required=True),
      }

      # This should get all sessions of user if session_id is not given, otherwise get detail about specific session
      def get(self, user_id=None, session_id=None):
        if not user_id:
            abort(http_status_code=404, error_code=error_enum.user_id_missing)
        result = SessionModel.get_user_sessions(user_id)
        if result:
            for record in result:
                record['dob'] = str(record['dob'])
        else:
            abort(http_status_code=400, error_code=error_enum.user_id_not_found)
        return result

      @use_args(session_args_post)
      def post(self, args, user_id):
        if not user_id:
                abort(http_status_code=400, error_code=error_enum.user_id_missing)
        success = SessionModel.insert_user_session(user_id, args)
        if success is -1:
            abort(http_status_code=500, error_code=error_enum.database_error_inserting)
        elif success is -2:
            abort(http_status_code=400, error_code=error_enum.fitness_session_overlap)
        return None, 201



      # def delete(self, session_id, user_id):
      #
      #
      # def put(self, session_id, user_id):