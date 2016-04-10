from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import use_args
from flask.ext.restful import abort
from app.common.errors import error_enum
from app.common.config import CAL_CONFIG as config, GMAIL_EVENTS_URL
from app.common.temp_data import database, session
from flask import redirect, make_response
import requests
from app.models.calendars import CalendarModel, CalendarEventsModel
import re
import datetime
import json


class CalendarAuthController(Resource):

    @staticmethod
    def validate_email(email=None):
        REG_EX = "^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9\._-]+\.[a-zA-Z]*$"
        return re.match(REG_EX, str(email))

    def get(self, user_id=None, email=None):
        if user_id is not None and email is not None:
            print email
            print self.validate_email(email)
            if self.validate_email(email):
                records = CalendarModel.check_email(email)
                if records>0 :
                    abort(http_status_code=400, error_code = error_enum.email_add_already_present)
                else:
                    session[email] = user_id
                    database[user_id] = {}
                    auth_uri = ('https://accounts.google.com/o/oauth2/v2/auth?response_type=code'
                                '&client_id={}&redirect_uri={}&scope={}&login_hint={}&access_type=offline')\
                                .format(config['CLIENT_ID'], config['REDIRECT_URI'], config['SCOPE'], email)
                    return redirect(auth_uri)
            else:
                abort(http_status_code=400, error_code=error_enum.invalid_email_syntax)
        else:
            return "Error parsing parameters"


class UserCalendarController(Resource):

    def delete(self, user_id= None, email=None):
        if email is not None:
            CalendarModel.delete_email(email)
            return None, 204
        else:
            abort(http_status_code=400, error_code=error_enum.email_not_found)

    def get(self, user_id = None):
        if user_id is not None:
            return CalendarModel.get_all_emails(user_id), 200
        else:
            abort(http_status_code=400, error_code=error_enum.user_id_missing)


class CalendarEventsController(Resource):

    def get(self, args, user_id, email_id=None):
        if user_id is None:
            abort(http_status_code=400, error_code=error_enum.user_id_missing)

        if email_id is None:
            abort(http_status_code=400, error_code=error_enum.email_not_found)

        secret = CalendarEventsModel.get_secret(user_id, email_id)
        access_token = secret[0]['access_token']

        # TODO: Must be a RFC3339 timestamp with mandatory time zone offset,
        # e.g., 2011-06-03T10:00:00-07:00, 2011-06-03T10:00:00Z.
        start_time = args.get('start_time')
        end_time = args.get('end_time')

        now = datetime.datetime.utcnow().isoformat() + 'Z'
        headers = {'Authorization': 'Bearer {}'.format(access_token)}
        params = {'timeMin': start_time, 'timeMax': end_time, 'maxResults': 10, 'singleEvents': True,
                  'orderBy': 'startTime'}
        r = requests.get(GMAIL_EVENTS_URL['KEY'], headers=headers, params=params)
        eventlist = r.json()['items']
        events = {}
        for event in eventlist:
            start = event['start'].get('dateTime', event['start'].get('date'))
            events[start] = event['summary']
        print r.text
        return json.dumps(events)


class CalendarAuthRedirectController(Resource):
    calendar_args = {
        'code': fields.Str(required=True)
    }

    @use_args(calendar_args)
    def get(self, args):

        auth_code = args.get('code')

        data = {'code': auth_code,
                'client_id': config['CLIENT_ID'],
                'client_secret': config['CLIENT_SECRET'],
                'redirect_uri': config['REDIRECT_URI'],
                'grant_type': 'authorization_code'}

        cred = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
        credjson = cred.json()

        # call the calendar service and get the email address
        headers = {'Authorization': 'Bearer {}'.format(credjson['access_token'])}
        req_uri = 'https://www.googleapis.com/calendar/v3/calendars/primary'
        r = requests.get(req_uri, headers=headers)
        emailadd = r.json()['id']

        username = session[emailadd]

        database[username][emailadd] = credjson
        # inserting into database

        calendar_details = {'user_id':username, 'email':emailadd, 'access_token':credjson['access_token'],
                            'refresh_token':credjson.get('refresh_token', None), 'account':'gmail'}

        result = CalendarModel.add_calendar(calendar_details)
        if not result:
            abort(http_status_code=404, error_code=error_enum.calendar_exception)
        else:
            database.pop(username)
            htmlcontent = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">\
                <html>\
                <head>\
                <script>\
                function closeBrowser(){\
                window.open(\'\', \'_self\', \'\');\
                window.close();\
                }\
                </script>\
                </head>\
                <body onload="closeBrowser();">\
                Calendar added successfully !!\
                </body>\
                </html>'

            response = make_response(htmlcontent)
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return response

