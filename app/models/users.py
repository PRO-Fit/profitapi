from app.common.database import Db
from app.common.util import Util


class User():
    @staticmethod
    def insert_user(user_details):
        add_user_query = ("INSERT INTO t_user (first_name, last_name, points, weight, height, dob, gender, email, "
                          "contact_number, injuries, created_datetime, modified_datetime) VALUES (%(first_name)s, "
                          "%(last_name)s, %(points)s, %(weight)s, %(height)s, %(dob)s, %(gender)s, %(email)s, "
                          "%(contact_number)s, %(injuries)s, %(created_datetime)s, %(modified_datetime)s)")
        user_details['created_datetime'] = Util.get_current_time()
        user_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_insert_query(add_user_query, user_details)

    @staticmethod
    def get_user(user_id):
        print user_id
        get_user_query = ("SELECT first_name, last_name, points, weight, height, dob, gender, email, contact_number, "
                          "injuries FROM t_user WHERE id = %s")
        return Db.execute_select_query(get_user_query, user_id)
