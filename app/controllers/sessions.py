from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import use_args
from flask.ext.restful import abort
from app.common.errors import error_enum
from app.models.sessions import SessionModel, BlockSessionModel


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


      def delete(self, user_id, session_id):
          if not user_id:
                abort(http_status_code=400, error_code=error_enum.user_id_missing)

          if not session_id:
                abort(http_status_code=400, error_code = error_enum.session_not_found)

          result = SessionModel.delete_session(user_id, session_id)

          if result == 1:
              return None, 204
          else:
              abort(http_status_code=400, error_code = error_enum.calendar_exception)

      @use_args(session_args_post)
      def put(self, args, user_id, session_id):
           if not user_id:
                abort(http_status_code=400, error_code=error_enum.user_id_missing)

           if not session_id:
                abort(http_status_code=400, error_code = error_enum.session_not_found)

           success = SessionModel.update_session(args, user_id, session_id)
           if success is -1:
                abort(http_status_code=500, error_code=error_enum.database_error_updating)
           elif success is -2:
                abort(http_status_code=400, error_code=error_enum.fitness_session_overlap)
           return None, 201


class UserBlockedSessionController(Resource):

      session_args_post = {
        'start_time': fields.Str(required=True),
        'end_time': fields.Str(required=True),
        'day_of_week': fields.Int(required=True),
      }

      def get(self, args, user_id=None, session_id=None):
        if not user_id:
            abort(http_status_code=404, error_code=error_enum.user_id_missing)

        if not session_id:
            abort(http_status_code=400, error_code = error_enum.session_not_found)

        result = BlockSessionModel.get_block_session(user_id, args['day_of_week'], session_id)
        return result


      @use_args(session_args_post)
      def post(self, args, user_id):
        if not user_id:
                abort(http_status_code=400, error_code=error_enum.user_id_missing)
        success = BlockSessionModel.create_block_session(user_id, args)
        if success is -1:
            abort(http_status_code=500, error_code=error_enum.database_error_inserting)
        elif success is -2:
            abort(http_status_code=400, error_code=error_enum.fitness_session_overlap)
        return None, 201


      def delete(self, user_id, session_id):
          if not user_id:
                abort(http_status_code=400, error_code=error_enum.user_id_missing)

          if not session_id:
                abort(http_status_code=400, error_code = error_enum.session_not_found)

          result = BlockSessionModel.delete_block_session(user_id, session_id)

          if result == 1:
              return None, 204
          else:
              abort(http_status_code=400, error_code = error_enum.calendar_exception)

      @use_args(session_args_post)
      def put(self, args, user_id, session_id):
           if not user_id:
                abort(http_status_code=400, error_code=error_enum.user_id_missing)

           if not session_id:
                abort(http_status_code=400, error_code = error_enum.session_not_found)

           success = BlockSessionModel.update_block_session(user_id, session_id, args)
           if success is -1:
                abort(http_status_code=500, error_code=error_enum.database_error_updating)
           elif success is -2:
                abort(http_status_code=400, error_code=error_enum.fitness_session_overlap)
           return None, 201