from app.common.database import Db
from app.common.util import Util
from app.models.activity import Activity
import requests
from app.common.config import CAL_CONFIG, GMAIL_EVENTS_URLS
import iso8601


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
        delete_email_query = "DELETE from t_user_external_account WHERE email= \"%s\"" %email_add
        return Db.execute_update_query(delete_email_query)

    @staticmethod
    def get_all_emails(user_id, email_id=None):
        get_email_query = "SELECT id, user_id, email, created_datetime, modified_datetime from t_user_external_account where user_id =  \"%s\"" %user_id
        if email_id:
            get_email_query+=" AND email = \"%s\"" %email_id

        return Util.convert_datetime_to_str(Db.execute_select_query(get_email_query))

    @staticmethod
    def get_all_accounts_detail(user_id):
        query = """
                SELECT *
                FROM t_user_external_account WHERE user_id =  \"%s\"""" %user_id

        return Db.execute_select_query(query)

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


class CalendarEventsModel(object):

    @staticmethod
    def get_secret(user_id, email_id):

        query = """
                SELECT access_token, refresh_token
                FROM t_user_external_account
                WHERE user_id = '%(user_id)s'
                AND email = '%(email_id)s'
              """
        parameters = {
            'user_id': user_id,
            'email_id': email_id
        }

        return Db.execute_select_query(query, parameters)

    @staticmethod
    def store_new_secret(user_id, email_id, secret):

        query = """
                UPDATE t_user_external_account
                SET access_token = '%(secret)s',
                modified_datetime = '%(modified_datetime)s'
                WHERE user_id = '%(user_id)s'
                AND email = '%(email_id)s'
                """

        parameters = {
            'secret': secret,
            'user_id': user_id,
            'email_id': email_id,
            'modified_datetime': Util.get_current_time()
        }

        return Db.execute_select_query(query, parameters)

    @staticmethod
    def get_events_from_google(user_id, email_id, start_date, end_date):

        secret = CalendarEventsModel.get_secret(user_id, email_id)
        access_token = secret[0]['access_token']

        # TODO: Must be a RFC3339 timestamp with mandatory time zone offset,
        # e.g., 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z.
        start_time = Util.convert_string_to_datetime(start_date).isoformat() + 'Z'
        end_time = Util.convert_string_to_datetime(end_date).isoformat() + 'Z'

        headers = {'Authorization': 'Bearer {}'.format(access_token)}
        params = {'timeMin': start_time, 'timeMax': end_time, 'maxResults': 10, 'singleEvents': True,
                  'orderBy': 'startTime'}

        r = requests.get(GMAIL_EVENTS_URLS['EVENTS'], headers=headers, params=params)

        if r.status_code == 401:
            head = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = {
                'client_id': CAL_CONFIG['CLIENT_ID'],
                'client_secret': CAL_CONFIG['CLIENT_SECRET'],
                'refresh_token': secret[0]['refresh_token'],
                'grant_type': 'refresh_token'
            }

            new_token = requests.post(GMAIL_EVENTS_URLS['ACCESS_TOKEN'], headers=head, params=data)
            new_secret = new_token.json()['access_token']
            CalendarEventsModel.store_new_secret(user_id,email_id,new_secret)

            headers = {'Authorization': 'Bearer {}'.format(new_secret)}
            r = requests.get(GMAIL_EVENTS_URLS['EVENTS'], headers=headers, params=params)
            eventlist = r.json()['items']
            events = []
            for event in eventlist:
                session = {}
                session['start_datetime'] = str(iso8601.parse_date(event['start'].get('dateTime', event['start'].get('date'))))[:19]
                session['end_datetime'] = str(iso8601.parse_date(event['end'].get('dateTime', event['end'].get('date'))))[:19]
                session['summary'] = event['summary']
                session['email'] = email_id
                session['date'] = session['start_datetime'][:10]
                session['day'] = Util.get_weekday(iso8601.parse_date(event['start'].get('dateTime', event['start'].get('date'))))
                events.append(session)
            return events
        eventlist = r.json()['items']
        events = []
        for event in eventlist:
            session = {}
            session['start_datetime'] = str(iso8601.parse_date(event['start'].get('dateTime', event['start'].get('date'))))[:19]
            session['end_datetime'] = str(iso8601.parse_date(event['end'].get('dateTime', event['end'].get('date'))))[:19]
            session['summary'] = event['summary']
            session['email'] = email_id
            session['date'] = session['start_datetime'][:10]
            session['day'] = Util.get_weekday(iso8601.parse_date(event['start'].get('dateTime', event['start'].get('date'))))
            events.append(session)
        return events

    # @staticmethod
    # def get_weekday(date):
    #     days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    #     dayNumber = date.weekday()
    #     return days[dayNumber]