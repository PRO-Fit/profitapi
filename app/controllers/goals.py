from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import use_args
from flask.ext.restful import abort

from app.common.errors import error_enum
from app.models.goals import Goal


class GoalController(Resource):
    user_goal_args = {
        'name': fields.Str(required=True),
        'target_burn_calories': fields.Int(missing=0),
        'target_distance': fields.Int(missing=0),
        'start_datetime': fields.Str(required=True),
        'end_datetime': fields.Str(required=True),
    }

    def get(self, user_id, goal_id=None):
        if not user_id:
            abort(http_status_code=400, error_code=error_enum.user_id_missing)
        result = Goal.get_user_active_goals(user_id, goal_id)
        if result:
            for record in result:
                record['start_datetime'] = str(record['start_datetime'])
                record['end_datetime'] = str(record['end_datetime'])
        return result

    @use_args(user_goal_args)
    def post(self, args, user_id):
        if not user_id:
            abort(http_status_code=400, error_code=error_enum.user_id_missing)
        success = Goal.insert_user_goal(user_id, args)
        if success is -1:
            abort(http_status_code=500, error_code=error_enum.database_error_inserting)
        elif success is -2:
            abort(http_status_code=400, error_code=error_enum.goal_overlap)
        return None, 201

    def delete(self, user_id, goal_id):
        if not goal_id:
            abort(http_status_code=400, error_code=error_enum.goal_id_missing)
        success = Goal.delete_user_goal(goal_id)
        if success is -1:
            abort(http_status_code=500, error_code=error_enum.database_error_deleting)
        return None, 204

    @use_args(user_goal_args)
    def put(self, args, user_id, goal_id):
        if not user_id:
            abort(http_status_code=400, error_code=error_enum.user_id_missing)
        if not goal_id:
            abort(http_status_code=400, error_code=error_enum.goal_id_missing)
        success = Goal.update_user_goal(user_id, goal_id, args)
        if success is -1:
            abort(http_status_code=500, error_code=error_enum.database_error_updating)
        elif success is -2:
            abort(http_status_code=400, error_code=error_enum.goal_overlap)
        return None, 204
