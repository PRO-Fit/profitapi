from app.common.database import Db
from app.common.util import Util
from app.models.sessions import SessionModel
import time
import random

user_id = "jainik_vora@live.in"
activities = [1, 2]
calories_burnt = [0.33, 0.42]
distance = [0.0057, 0.0078]

interval = 5000


def insert_user_activities(user_activities):
    query = """INSERT INTO
                t_user_activity (user_id, workout_type_id, distance, start_datetime, end_datetime, calories_burnt)
                VALUES""" + ",".join(user_activities)
    Db.execute_insert_query(query)

query = """INSERT INTO t_user_activity
                            (user_id,
                            workout_type_id,
                            distance,
                            start_datetime,
                            end_datetime,
                            calories_burnt)
                         VALUES
                            ('%(user_id)s',
                            %(workout_type_id)s,
                            %(distance)s,
                            %(start_datetime)s,
                            %(end_datetime)s,
                            %(calories_burnt)s)"""

sessions = [{'start': session['start_datetime'], 'end': session['end_datetime']} for session in SessionModel.get_user_sessions(user_id, '2016-04-15 00:00:00', '2016-05-11 00:00:00')]

print sessions

calculated_activites = []
for session in sessions:
    start_time = Util.convert_string_to_datetime(session['start'])
    end_time = Util.convert_string_to_datetime(session['end'])

    start_timestamp = long(time.mktime(start_time.timetuple()) * 1000.0)
    end_timestamp = long(time.mktime(end_time.timetuple()) * 1000.0)

    while start_timestamp < end_timestamp:
        activity = random.getrandbits(1)
        session_end = start_timestamp + 5000
        calculated_activites.append(
            "('{0}',{1},{2},{3}, {4}, {5})".format(user_id, activities[activity], distance[activity], start_timestamp, session_end, calories_burnt[activity])
        )
        start_timestamp = session_end

insert_user_activities(calculated_activites)