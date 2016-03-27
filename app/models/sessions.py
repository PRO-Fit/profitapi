from app.common.database import Db
from app.common.util import Util


class SessionModel(object):

    @staticmethod
    def insert_user_session(user_id, session_details):
        if SessionModel._has_session_period_overlap(user_id, session_details['start_datetime'], session_details['end_datetime']):
            return -2
        query = """INSERT INTO t_user_session (
                    user_id,
                    workout_type_id,
                    start_datetime,
                    end_datetime,
                    session_feedback_id,
                    is_accepted,
                    ) VALUES (
                    %(user_id)s,
                    %(workout_type_id)s,
                    %(start_datetime)s,
                    %(end_datetime)s,
                    %(session_feedback_id)s,
                    %(is_accepted)s,
                    )"""
        session_details['user_id'] = user_id
        session_details['created_datetime'] = Util.get_current_time()
        session_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_insert_query(query, session_details)

    @staticmethod
    def _has_session_period_overlap(user_id, start_datetime, end_datetime):
        user_active_goals = SessionModel.get_user_sessions(user_id)
        new_start = Util.convert_string_to_datetime(start_datetime)
        new_end = Util.convert_string_to_datetime(end_datetime)
        for goal in user_active_goals:
            start = goal.get('start_datetime')
            end = goal.get('end_datetime')
            if start <= new_start < end or start <= new_end <= end or new_start <= start < new_end:
                return True
        return False

    @staticmethod
    def get_user_sessions(user_id):
        return list