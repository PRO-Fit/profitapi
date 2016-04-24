from datetime import datetime
import datetime as dtime

from app.common.database import Db
from app.common.util import Util
from app.common.config import session_status
from app.models.calendars import CalendarModel, CalendarEventsModel
import time
from app.models.activity import Activity

activity_type = Activity.get_activity_type()



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
                    session_status,
                    created_datetime,
                    modified_datetime
                    ) VALUES (
                    %(user_id)s,
                    %(workout_type_id)s,
                    %(start_datetime)s,
                    %(end_datetime)s,
                    %(session_feedback_id)s,
                    %(session_status)s,
                    %(created_datetime)s,
                    %(modified_datetime)s
                    )"""
        session_details['user_id'] = user_id
        session_details['created_datetime'] = Util.get_current_time()
        session_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_insert_query(query, session_details)

    @staticmethod
    def _has_session_period_overlap(user_id, start_datetime, end_datetime, session_id = None):
        user_sessions = SessionModel.get_user_sessions(user_id, start=Util.get_current_datetime())
        new_start = Util.convert_string_to_datetime(start_datetime)
        new_end = Util.convert_string_to_datetime(end_datetime)
        for session in user_sessions:
            if session_id:
                if int(session_id) == session.get('id'):
                    continue
            start = Util.convert_string_to_datetime(session.get('start_datetime'))
            end = Util.convert_string_to_datetime(session.get('end_datetime'))
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
                      session_status
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
            parameters['start'] = str(start)

        if end:
            end_clause = """ AND end_datetime <= '%(end)s'"""
            query += end_clause
            parameters['end'] = str(end)

        return Util.convert_datetime_to_str(Db.execute_select_query(query, parameters))

    @staticmethod
    def delete_session(user_id, session_id):

        query = """DELETE
                   FROM t_user_session
                   WHERE
                   user_id = '%(user_id)s'
                   AND id = '%(session_id)s'"""

        parameters = {
            'user_id': user_id,
            'session_id': session_id
        }

        return Db.execute_update_query(query, parameters)

    @staticmethod
    def update_session(user_id, session_id, session_details):

        if SessionModel._has_session_period_overlap(user_id, session_details['start_datetime'],
                                                    session_details['end_datetime'], session_id):
            return -2

        query = """UPDATE t_user_session
                   SET
                   user_id = '%(user_id)s',
                   workout_type_id = '%(workout_type_id)s',
                   start_datetime = '%(start_datetime)s',
                   end_datetime = '%(end_datetime)s',
                   session_feedback_id = '%(session_feedback_id)s',
                   session_status = '%(session_status)s',
                   modified_datetime = '%(modified_datetime)s'
                   WHERE id = '%(session_id)s'
                   """

        session_details['user_id'] = user_id
        session_details['session_id'] = session_id
        session_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_update_query(query, session_details)

    @staticmethod
    def get_user_sessions_in_duration(start_time, end_time, user_id=None):
        if type(start_time) is datetime:
            start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        if type(end_time) is datetime:
            end_time = end_time.strftime("%Y-%m-%d %H:%M:%S")
        query = """SELECT id, user_id, workout_type_id, start_datetime, end_datetime, session_status
                    FROM t_user_session WHERE start_datetime BETWEEN'%(start_time)s' AND '%(end_time)s'
                    AND session_status IN ('%(session_status)s') %(user_id_query)s
                    UNION
                    SELECT id, user_id, workout_type_id, start_datetime, end_datetime, session_status
                    FROM t_user_session WHERE end_datetime BETWEEN'%(start_time)s' AND '%(end_time)s'
                    AND session_status IN ('%(session_status)s') %(user_id_query)s
                    ORDER BY start_datetime ASC"""
        user_id_query = ""
        if user_id:
            user_id_query = " AND user_id = '%s'" % user_id
        sessions = [session_status.USER_CREATED, session_status.REC_ACCEPTED, session_status.NOT_NOTIFIED]
        params = {
            'start_time': start_time,
            'end_time': end_time,
            'session_status': "','".join(sessions),
            'user_id_query': user_id_query
        }
        return Db.execute_select_query(query % params)

    @staticmethod
    def get_free_slots(user_id, start_date, end_date=None):
        if user_id is None:
            raise Exception('user_id can not be null')
        if start_date is None:
            raise Exception('start_date not provided')
        if end_date is None:
            start = Util.convert_string_to_datetime(start_date)
            end_date = str(start + dtime.timedelta(days=1))

        # get all accounts
        accounts = CalendarModel.get_all_accounts_detail(user_id)

        # stores all event from all google accounts for start_date to end_date
        events_from_google = []

        # get all events from all google accounts
        for account in accounts:
            list_of_events = CalendarEventsModel.get_events_from_google(user_id, account['email'], str(start_date),
                                                                        str(end_date))
            events_from_google = events_from_google + list_of_events

        # get list of dates between start and end
        start_date = Util.convert_string_to_datetime(str(start_date))
        end_date = Util.convert_string_to_datetime(str(end_date))

        dates = Util.daterange(start_date, end_date)
        list_of_dateobject = []
        for day in dates:
            new_day = DateObject(day)
            new_day.day = Util.get_weekday(day)
            print new_day.day
            list_of_dateobject.append(new_day)

        # get all block_session for user
        block_sessions = BlockSessionModel.get_block_session(user_id)

        # club all block sessions day wise
        block_sessions_for_day = {
        }

        for block_session in block_sessions:

            time_slot = TimeSlot(Util.convert_string_to_time(block_session['start_time']),
                                 Util.convert_string_to_time(block_session['end_time']))

            if block_sessions_for_day.get(block_session['day_of_week']) is None:
                block_sessions_for_day[block_session['day_of_week']] = []
                temp_list = block_sessions_for_day[block_session['day_of_week']]

            else:
                temp_list = block_sessions_for_day.get(block_session['day_of_week'])
            temp_list.append(time_slot)

        # populate blocked sessions in list_of_dateObject
        for date_object in list_of_dateobject:
            date_object.block_sessions = block_sessions_for_day.get(date_object.day)

        # populate events from google in list_of_dateObject
        for date_object in list_of_dateobject:
            date = date_object.date
            for session in events_from_google:
                if session['date'] == str(date)[:10]:

                    time_slot = TimeSlot(Util.convert_string_to_time(session['start_datetime'][11:]),
                                 Util.convert_string_to_time(session['end_datetime'][11:]))
                    date_object.google_events.append(time_slot)

        # calculate free slots for each object in list_of_dateObject
        for date_object in list_of_dateobject:
            all_sessions = date_object.block_sessions + date_object.google_events

            # sort all_sessions to get free slots
            all_sessions.sort(key=lambda r: r.start)
            for x, y in zip(all_sessions, all_sessions[1:]):
                if x.end < y.start:
                    start = x.end
                    end = y.start
                    date_object.free_slots.append({"start": time.strftime('%H:%M:%S', start),
                                                   "end": time.strftime('%H:%M:%S', end)})

            # if first reserved slot is not starting with mid-night then add delta in free slots
            if all_sessions[0].start > Util.convert_string_to_time("00:00:00"):
                date_object.free_slots.append({"start": "00:00:00", "end": time.strftime('%H:%M:%S', all_sessions[0].start)})

            # if last reserved slot is not ending at mid-night then add delta in free slots
            if all_sessions[-1].end < Util.convert_string_to_time("23:59:59"):
                date_object.free_slots.append({"start": time.strftime('%H:%M:%S', all_sessions[-1].end), "end": "23:59:59"})

        # return result from list_of_dateObject
        result = {}
        for date_object in list_of_dateobject:
            result[str(date_object.date)] = date_object.free_slots

        return result


class BlockSessionModel(object):

    @staticmethod
    def create_block_session(user_id, session_details):
        result_row = 0
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
                    %(modified_datetime)s
                    )
                    """
                session_details['user_id'] = user_id
                session_details['day_of_week'] = day
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
                    user_id = '%(user_id)s'
                    """

        parameters = {
            'user_id': user_id,
        }

        if day_of_week:
            parameters['day_of_week'] = day_of_week
            query += " AND day_of_week = '%(day_of_week)s'"
        if session_id:
            parameters['id'] = session_id
            query += " AND id = '%(id)s'"

        return Util.convert_time_to_str(Db.execute_select_query(query, parameters))

    @staticmethod
    def update_block_session(user_id, session_id, session_details):
        if BlockSessionModel._has_session_period_overlap(user_id, session_details['start_time'],
                                session_details['end_time'], session_details['day_of_week'], session_id):
            return -2
        query = """
             UPDATE t_user_blocked_session
               SET
               start_time = '%(start_time)s',
               end_time = '%(end_time)s',
               day_of_week = '%(day_of_week)s',
               modified_datetime = '%(modified_datetime)s'
               WHERE user_id = '%(user_id)s' AND id = '%(session_id)s'
               """

        session_details['session_id'] = session_id
        session_details['user_id'] = user_id
        session_details['modified_datetime'] = Util.get_current_time()
        return Db.execute_update_query(query, session_details)

    @staticmethod
    def delete_block_session(user_id, session_id):
        query = """
                DELETE
                FROM t_user_blocked_session
                WHERE user_id = '%(user_id)s'
                AND id = '%(session_id)s'
                """
        parameters = {
            'user_id': user_id,
            'session_id': session_id
        }

        return Db.execute_update_query(query, parameters)

    @staticmethod
    def _has_session_period_overlap(user_id, start_time, end_time, day_of_week, session_id=None):
        sessions = BlockSessionModel.get_block_session(user_id, day_of_week)
        new_start = Util.convert_string_to_time(start_time)
        new_end = Util.convert_string_to_time(end_time)
        for session in sessions:
            if session_id:
                if int(session_id) == session.get('id'):
                    continue
            start = Util.convert_string_to_time(session.get('start_time'))
            end = Util.convert_string_to_time(session.get('end_time'))
            if start <= new_start < end or start <= new_end <= end or new_start <= start < new_end:
                return True
        return False


class DateObject(object):
    """common date object to store google events, block sessions and free slots"""

    def __init__(self, date):
        self.date = date
        self.day = None
        self.google_events = []
        self.block_sessions = None
        self.free_slots = []

    def __str__(self):
        return "" + self.date + " ~ " + self.day + " ~ " + self.block_sessions + " ~ " +\
                self.google_events + " ~ " + self.free_slots


class TimeSlot(object):
    """object to store start and end time of slot """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return "" + self.start + " ~ " + self.end
