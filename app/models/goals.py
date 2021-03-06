from datetime import datetime

from app.common.database import Db
from app.common.util import Util


class Goal(object):

    @staticmethod
    def get_user_active_goals(user_id, goal_id=None):
        query = """SELECT
                      id,
                      user_id,
                      `name`,
                      target_burn_calories,
                      target_distance,
                      start_datetime,
                      end_datetime
                    FROM t_goal
                    WHERE
                      user_id = '%(user_id)s'
                      AND end_datetime >= '%(today)s'
                      """
        goal_id_clause = """ AND id = %(goal_id)s"""
        parameters = {
            'user_id': user_id,
            'today': Util.get_current_time()
        }
        if goal_id:
            query += goal_id_clause
            parameters['goal_id'] = goal_id
        return Db.execute_select_query(query, parameters)

    @staticmethod
    def insert_user_goal(user_id, user_goal_details):
        if Goal._has_goal_period_overlap(user_id, user_goal_details['start_datetime'], user_goal_details['end_datetime']):
            return -2
        query = """INSERT INTO t_goal (
                    user_id,
                    `name`,
                    target_burn_calories,
                    target_distance,
                    start_datetime,
                    end_datetime,
                    created_datetime,
                    modified_datetime
                    ) VALUES (
                    %(user_id)s,
                    %(name)s,
                    %(target_burn_calories)s,
                    %(target_distance)s,
                    %(start_datetime)s,
                    %(end_datetime)s,
                    %(created_datetime)s,
                    %(modified_datetime)s
                    )"""
        user_goal_details['user_id'] = user_id
        user_goal_details['created_datetime'] = Util.get_current_time()
        user_goal_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_insert_query(query, user_goal_details)

    @staticmethod
    def update_user_goal(user_id, goal_id, user_goal_details):
        if Goal._has_goal_period_overlap(user_id, user_goal_details['start_datetime'],
                                         user_goal_details['end_datetime'], goal_id=goal_id):
            return -2
        query = """UPDATE t_goal SET
                    `name` = '%(name)s',
                    target_burn_calories = %(target_burn_calories)s,
                    target_distance = %(target_distance)s,
                    start_datetime = '%(start_datetime)s',
                    end_datetime = '%(end_datetime)s',
                    modified_datetime =  '%(modified_datetime)s'
                   WHERE id = %(goal_id)s"""

        user_goal_details['modified_datetime'] = Util.get_current_time()
        user_goal_details['goal_id'] = int(goal_id)
        return Db.execute_update_query(query, user_goal_details)

    @staticmethod
    def delete_user_goal(goal_id):
        query = "DELETE FROM t_goal WHERE id = %s" % goal_id
        return Db.execute_update_query(query)

    @staticmethod
    def _has_goal_period_overlap(user_id, start_datetime, end_datetime, goal_id=None):
        user_active_goals = Goal.get_user_active_goals(user_id)
        new_start = Util.convert_string_to_datetime(start_datetime)
        new_end = Util.convert_string_to_datetime(end_datetime)
        for goal in user_active_goals:
                if goal_id and int(goal.get('id')) == int(goal_id):
                    continue
                start = goal.get('start_datetime')
                end = goal.get('end_datetime')
                if start <= new_start < end or start <= new_end <= end or new_start <= start < new_end:
                    return True
        return False

    @staticmethod
    def get_user_goals(start_date, end_date, user_id=None):
        if type(start_date) is datetime:
            start_date = start_date.strftime("%Y-%m-%d")
        if type(end_date) is datetime:
            end_date = end_date.strftime("%Y-%m-%d")
        query = """SELECT id, user_id, target_burn_calories, target_distance, start_datetime, end_datetime
                    FROM t_goal WHERE start_datetime BETWEEN '%(start_date)s' AND '%(end_date)s' %(user_id_query)s
                    UNION
                    SELECT id, user_id, target_burn_calories, target_distance, start_datetime, end_datetime
                    FROM t_goal WHERE end_datetime BETWEEN '%(start_date)s' AND '%(end_date)s' %(user_id_query)s
                    UNION
                    SELECT id, user_id, target_burn_calories, target_distance, start_datetime, end_datetime
                    FROM t_goal WHERE start_datetime < '%(start_date)s' AND end_datetime > '%(end_date)s'
                    ORDER BY start_datetime ASC"""
        user_id_query = ""
        if user_id:
            user_id_query = " AND user_id = '%s'" % user_id
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'user_id_query': user_id_query
        }
        return Db.execute_select_query(query % params)
