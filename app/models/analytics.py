from datetime import datetime

from app.common.database import Db
from app.common.util import Util
HOURS = ["0:00", "1:00", "2:00", "3:00", "4:00", "5:00", "6:00", "7:00", "8:00", "9:00", "10:00", "11:00", "12:00",
         "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]

WEEK_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class Analytics(object):
    @staticmethod
    def get_present_day_analytics(user_id):
        query = """
                SELECT
                  SUM(distance) distance,
                  TRUNCATE(SUM(calories_burnt),2) calories,
                  HOUR(TIME(TRUNCATE(FROM_UNIXTIME(start_datetime/1000),0))) dayhour FROM t_user_activity
                WHERE user_id = '{}'
                AND DATE_FORMAT(FROM_UNIXTIME(start_datetime/1000), "%Y-%m-%d") = DATE_FORMAT(CURDATE(), "%Y-%m-%d")
                GROUP BY dayhour
                """
        result = {row['dayhour']: {'calories': row['calories'], 'distance': float(row['distance'])} for row in Db.execute_select_query(query.format(user_id))}
        calories = []
        distance = []
        for hour in HOURS:
            if int(hour.split(":")[0]) in result:
                calories.append(result[int(hour.split(":")[0])]['calories'])
                distance.append(result[int(hour.split(":")[0])]['distance'])
            else:
                calories.append(0.0)
                distance.append(0.0)

        return {
            'hours': HOURS,
            'calories': calories,
            'distance': distance
        }

    @staticmethod
    def get_present_week_analytics(user_id):
        # WEEKDAY() -> 0 for Monday, 6 for Sunday
        query = """
                SELECT
                  SUM(distance) distance,
                  TRUNCATE(SUM(calories_burnt),2) calories,
                  WEEKDAY(FROM_UNIXTIME(start_datetime/1000)) weekday
                FROM t_user_activity
                WHERE user_id = '%(user_id)s'
                AND start_datetime BETWEEN %(start_datetime)s AND  %(end_datetime)s
                GROUP BY weekday
                """
        params = {
            'user_id': user_id,
            'start_datetime': int(Util.get_future_date(-7).strftime('%s')) * 1000,
            'end_datetime': int(Util.get_current_datetime().strftime('%s')) * 1000
        }
        week_day_index = WEEK_DAYS.index(datetime.now().strftime("%A")[:3])
        week_days = WEEK_DAYS[week_day_index:] + WEEK_DAYS[:week_day_index]
        result = {row['weekday']: {'calories': row['calories'], 'distance': float(row['distance'])} for row in Db.execute_select_query(query % params)}
        calories = []
        distance = []
        for day in week_days:
            if WEEK_DAYS.index(day) in result:
                calories.append(result[WEEK_DAYS.index(day)]['calories'])
                distance.append(result[WEEK_DAYS.index(day)]['distance'])
            else:
                calories.append(0.0)
                distance.append(0.0)
        return {
            'weekdays': week_days,
            'calories': calories,
            'distance': distance
        }

    @staticmethod
    def get_last_30_days_analytics(user_id):
        dates = [date.strftime('%Y-%m-%d') for date in Util.daterange(Util.get_future_date(-30), Util.get_current_datetime())]
        query = """
                SELECT
                  SUM(distance) distance,
                  TRUNCATE(SUM(calories_burnt),2) calories,
                  DATE_FORMAT(FROM_UNIXTIME(start_datetime/1000), '%Y-%m-%d') as activity_date
                FROM t_user_activity
                WHERE user_id = '{}'
                GROUP BY activity_date
                HAVING activity_date BETWEEN '{}' and '{}'
                """
        start = Util.get_future_date(-30).strftime('%Y-%m-%d')
        end = Util.get_current_datetime().strftime('%Y-%m-%d')
        result = {row['activity_date']: {'calories': row['calories'], 'distance': float(row['distance'])} for row in Db.execute_select_query(query.format(user_id, start, end))}
        calories = []
        distance = []
        for date in dates:
            if date in result:
                calories.append(result[date]['calories'])
                distance.append(result[date]['distance'])
            else:
                calories.append(0.0)
                distance.append(0.0)
        return {
            'dates': dates,
            'calories': calories,
            'distance': distance
        }
