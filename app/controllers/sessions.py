from flask.ext.restful import Resource
from flask import request
from webargs import fields
from webargs.flaskparser import use_args
from flask.ext.restful import abort
from app.common.errors import error_enum
from app.models.sessions import SessionModel, BlockSessionModel
from app.common.config import session_status, SESSION_STATUS
from app.common.util import Util
import datetime


class UserSessionController(Resource):

      session_args_post = {
        'workout_type_id': fields.Str(required=True),
        'start_datetime': fields.Str(required=True),
        'end_datetime': fields.Str(required=True),
        'session_feedback_id': fields.Int(required=False),
        'session_status': fields.Str(required=True),
      }

      # This should get all sessions of user if session_id is not given, otherwise get detail about specific session
      def get(self, user_id=None, session_id=None):
        args = request.args
        if not user_id:
            abort(http_status_code=404, error_code=error_enum.user_id_missing)

        if args.get('day'):
            start = Util.convert_string_to_datetime(args.get('day'))
            end = start + datetime.timedelta(days=1)
        else:
            start = args.get('start_date')
            end = args.get('end_date')

        result = SessionModel.get_user_sessions(user_id, start, end, session_id=session_id)
        return result
        return None, 200


      @use_args(session_args_post)
      def post(self, args, user_id):
        if not user_id:
                abort(http_status_code=400, error_code=error_enum.user_id_missing)
        if args['session_status'] not in SESSION_STATUS:
            abort(http_status_code=400, error_code = error_enum.invalid_session_status)
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

           success = SessionModel.update_session(user_id, session_id,args)
           if success is -1:
                abort(http_status_code=500, error_code=error_enum.database_error_updating)
           elif success is -2:
                abort(http_status_code=400, error_code=error_enum.fitness_session_overlap)
           return None, 200


class UserBlockedSessionController(Resource):

      session_args_post = {
        'start_time': fields.Str(required=True),
        'end_time': fields.Str(required=True),
        'day_of_week': fields.Str(required=True),
      }

      def get(self, user_id, session_id=None, day=None):
        if not user_id:
            abort(http_status_code=404, error_code=error_enum.user_id_missing)

        result = BlockSessionModel.get_block_session(user_id, day_of_week=day
                                                     , session_id=session_id)
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

class FreeSlotsController(Resource):

      def get(self, user_id):
          args = request.args

          if not user_id:
                abort(http_status_code=400, error_code=error_enum.user_id_missing)

          start = args.get('start')
          end = args.get('end')

          return SessionModel.get_free_slots(user_id, start, end)
