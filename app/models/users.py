from app.common.database import Db
from app.common.util import Util
from app.models.activity import Activity


class User(object):
    @staticmethod
    def insert_user(user_details):
        add_user_query = ("""INSERT INTO t_user (first_name, last_name, points, weight, height, dob, gender, email,
                          contact_number, injuries, user_id, created_datetime, modified_datetime) VALUES (
                          %(first_name)s, %(last_name)s, %(points)s, %(weight)s, %(height)s, %(dob)s, %(gender)s,
                          %(email)s, %(contact_number)s, %(injuries)s, %(user_id)s, %(created_datetime)s,
                          %(modified_datetime)s)""")
        user_details['created_datetime'] = Util.get_current_time()
        user_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_insert_query(add_user_query, user_details)

    @staticmethod
    def insert_user_activity_pref(user_id, preference):
        query = """INSERT INTO t_user_activity_preference (workout_type_id, preference_priority, user_id) VALUES (
                  %s, %s, %s)"""
        activity_types = Activity.get_activity_type()
        for activity in preference:
            activity_query = query % (activity_types.get(activity), int(preference.get(activity)), user_id)
            Db.execute_insert_query(activity_query)
        return

    @staticmethod
    def get_user(user_id):
        get_user_query = """SELECT first_name, last_name, points, weight, height, dob, gender, email, contact_number,
                          injuries FROM t_user WHERE user_id = \"%s\"""" % user_id
        return Db.execute_select_query(get_user_query)
