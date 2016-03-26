from app.common.database import Db
from app.common.util import Util
from app.models.activity import Activity


class CalendarModel(object):
    @staticmethod
    def add_calendar(calendar_details):
        get_account_details_query ="""SELECT id FROM t_external_account WHERE t_external_account.name = \"%s\"""" % calendar_details['account']
        external_id = Db.execute_select_query(get_account_details_query)
        calendar_details['external_account_id'] = external_id[0]['id']
        add_calendar_query = ("""INSERT INTO t_user_external_account (user_id, external_account_id, access_token, refresh_token, email,
                               created_datetime, modified_datetime) VALUES (
                              %(user_id)s, %(external_account_id)s, %(access_token)s, %(refresh_token)s, %(email)s, %(created_datetime)s,
                              %(modified_datetime)s)""")
        calendar_details['created_datetime'] = Util.get_current_time()
        calendar_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_insert_query(add_calendar_query, calendar_details)

    @staticmethod
    def check_email(email_add):
        get_account_details_query ="""SELECT email FROM t_user_external_account WHERE email = \"%s\"""" % email_add
        ids = Db.execute_select_query(get_account_details_query)
        return len(ids)

    @staticmethod
    def delete_email(email_add):
        delete_email_query = "DELETE from profit.t_user_external_account WHERE email= \"%s\"" %email_add
        return Db.execute_update_query(delete_email_query)

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
