from app.common.database import Db
from app.common.util import Util


class SessionModel(object):

    @staticmethod
    def insert_user_session(user_id, session_details):
        if SessionModel._has_session_period_overlap(user_id, session_details['start_datetime'],
                                                    session_details['end_datetime']):
            return -2
        query = """INSERT INTO t_user_session (
                    user_id,
                    workout_type_id,
                    start_datetime,
                    end_datetime,
                    session_feedback_id,
                    is_accepted,
                    created_datetime,
                    modified_datetime
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
        user_sessions = SessionModel.get_user_sessions(user_id, start=Util.get_current_datetime())
        new_start = Util.convert_string_to_datetime(start_datetime)
        new_end = Util.convert_string_to_datetime(end_datetime)
        for session in user_sessions:
            start = session.get('start_datetime')
            end = session.get('end_datetime')
            if start <= new_start < end or start <= new_end <= end or new_start <= start < new_end:
                return True
        return False

    @staticmethod
    def get_user_sessions(user_id, start=None, end=None, session_id=None):

        query = """SELECT
                      id,
                      user_id,
                      workout_type_id,
                      start_datetime,
                      end_datetime,
                      session_feedback_id,
                      is_accepted
                    FROM t_user_session
                    WHERE
                      user_id = '%(user_id)s'
                      """

        parameters = {
            'user_id': user_id,
        }

        if session_id:
            session_id_clause = """ AND id = %(session_id)s"""
            query += session_id_clause
            parameters['session_id'] = session_id

        if start:
            start_clause = """ AND start_datetime >= '%(start)s'"""
            query += start_clause
            parameters['start'] = start

        if end:
            end_clause = """ AND end_datetime >= '%(end)s'"""
            query += end_clause
            parameters['end'] = end

        print query % parameters
        return Db.execute_select_query(query, parameters)

    @staticmethod
    def delete_session(user_id, session_id):

        query = """DELETE
                   FROM t_user_session
                   WHERE
                   user_id = '%(user_id)s'
                   AND id = '%(session_id)'
                      """

        parameters = {
            'user_id': user_id,
            'session_id': session_id
        }

        return Db.execute_update_query(query, parameters)

    @staticmethod
    def update_session(user_id, session_id, session_details):

        if SessionModel._has_session_period_overlap(user_id, session_details['start_datetime'],
                                                    session_details['end_datetime']):
            return -2

        query = """UPDATE t_user_session
                   SET
                   user_id = '%(user_id)s',
                   workout_type_id = '%(workout_type_id)',
                   start_datetime = '%(start_datetime)',
                   end_datetime = '%(end_datetime)',
                   session_feedback_id = '%(session_feedback_id)'
                   is_accepted = '%(is_accepted)'
                   modified_datetime = '%(modified_datetime)'
                   WHERE id = '%(session_id)'
                   """

        session_details['session_id'] = session_id
        session_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_update_query(query, session_details)


class BlockSessionModel(object):

    @staticmethod
    def create_block_session(user_id, session_details):
        result_row = 0;
        days = []
        if session_details['day_of_week'] == 'All':
            days.extend(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']);
        else:
            days.append(session_details['day_of_week'])

        for day in days:
            if BlockSessionModel._has_session_period_overlap(user_id, session_details['start_time'],
                                    session_details['end_time'], day):
                if len(days) == 1:
                    return -2
                continue
            else:
                query = """INSERT INTO t_user_blocked_session (
                    user_id,
                    start_time,
                    end_time,
                    day_of_week,
                    created_datetime,
                    modified_datetime
                    ) VALUES (
                    %(user_id)s,
                    %(start_time)s,
                    %(end_time)s,
                    %(day_of_week)s,
                    %(created_datetime)s,
                    %(modified_datetime)s,
                    )"""
                session_details['user_id'] = user_id
                session_details['created_datetime'] = Util.get_current_time()
                session_details['modified_datetime'] = Util.get_current_time()
                result_row = Db.execute_insert_query(query, session_details)
                if result_row == -1:
                    return -1
        return result_row

    @staticmethod
    def get_block_session(user_id, day_of_week=None, session_id=None):

        query = """ SELECT
                    id,
                    user_id,
                    start_time,
                    end_time,
                    day_of_week
                    FROM t_user_blocked_session
                    WHERE
                    user_id = '%(user_id)'"""

        parameters = {
            'user_id': user_id,
        }

        if day_of_week:
            parameters['day_of_week'] = day_of_week
            query += " AND day_of_week = '%(day_of_week)'"
        if session_id:
            parameters['id'] = session_id
            query += " AND id = '%(session_id)'"

        return Db.execute_select_query(query, parameters)

    @staticmethod
    def update_block_session(user_id, session_id, session_details):
         if BlockSessionModel._has_session_period_overlap(user_id, session_details['start_time'],
                                    session_details['end_time'], session_details['day_of_week']):
            return -2
         query = """
                 UPDATE t_user_blocked_session
                   SET
                   start_time = '%(start_time)s',
                   end_time = '%(end_time)',
                   day_of_week = '%(day_of_week)',
                   modified_datetime = '%(modified_datetime)'
                   WHERE user_id = '%(user_id)'AND id = '%(session_id)'"""

         session_details['session_id'] = session_id
         session_details['user_id'] = user_id
         session_details['modified_datetime'] = Util.get_current_time()

         return Db.execute_update_query(query, session_details)

    @staticmethod
    def delete_block_session(user_id, session_id):
        query = """
                DELETE
                FROM t_user_blocked_session
                WHERE user_id = '%s(user_id)'
                AND session_id = '%s(session_id)'
                """
        parameters = {
            'user_id':user_id,
            'session_id':session_id
        }

        return Db.execute_update_query(query, parameters)

    @staticmethod
    def _has_session_period_overlap(user_id, start_time, end_time, day_of_week):
        sessions = BlockSessionModel.get_block_session(user_id, day_of_week)
        new_start = Util.convert_string_to_datetime(start_time)
        new_end = Util.convert_string_to_datetime(end_time)
        for session in sessions:
            start = session.get('start_time')
            end = session.get('end_time')
            if start <= new_start < end or start <= new_end <= end or new_start <= start < new_end:
                return True
        return False

