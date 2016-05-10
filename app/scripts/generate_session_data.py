from app.common.database import Db
from app.common.util import Util
from app.models.sessions import SessionModel
import time
from datetime import datetime
import random

user_id = "jainik_vora@live.in"
activities = [1, 2]
session_name = ['Lose Weight', 'Burn Fat!', 'Get Fit']
start_time = ['07:00:00', '06:30:00', '19:00:00', '17:39:00']
end_time = ['07:35:00', '07:15:00', '19:40:00', '18:00:00']
status = 'USER_CREATED'

date_range = Util.daterange(Util.convert_string_to_datetime("2016-04-30"), Util.convert_string_to_datetime("2016-05-30"))


query_single_insert = """INSERT INTO t_user_session (
                    user_id,
                    name,
                    workout_type_id,
                    start_datetime,
                    end_datetime,
                    session_status,
                    created_datetime,
                    modified_datetime
                    ) VALUES (
                    '%(user_id)s',
                    '%(name)s',
                    %(workout_type_id)s,
                    '%(start_datetime)s',
                    '%(end_datetime)s',
                    '%(session_status)s',
                    '%(created_datetime)s',
                    '%(modified_datetime)s'
                    )"""

user_sessions = []
for date in date_range:
    this_session_name = session_name[random.randint(0, 2)]
    random_num = random.randint(0, 3)
    session_start_date = date.strftime("%Y-%m-%d") + " " + start_time[random_num]
    session_end_date = date.strftime("%Y-%m-%d") + " " + end_time[random_num]
    workout_type = activities[random.getrandbits(1)]

    data = {
        'user_id': user_id,
        'name': this_session_name,
        'workout_type_id': workout_type,
        'start_datetime': session_start_date,
        'end_datetime': session_end_date,
        'session_status': status,
        'created_datetime': Util.get_current_time(),
        'modified_datetime': Util.get_current_time()
    }
    Db.execute_insert_query(query_single_insert % data)