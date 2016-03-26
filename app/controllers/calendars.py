from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import use_args
from flask.ext.restful import abort
from app.common.errors import error_enum
from app.common.config import CAL_CONFIG as config
from app.common.config import MAIL_GUN as email_config
from app.common.temp_data import database, session
from flask import redirect, make_response
import requests
from app.models.calendars import CalendarModel
import json


class CalendarAuthController(Resource):

    @staticmethod
    def validate_email(self, email=None):
        result = requests.get(
                "https://api.mailgun.net/v3/address/validate",
                auth=("api", email_config['KEY']),
                params={"address": email}).json()

        is_valid = result['is_valid']
        return is_valid

    def get(self, user_id=None, email=None):
        if user_id is not None and email is not None:
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
                abort(http_status_code=400, error_code = error_enum.email_verification_failed)
        else:
            return "Error parsing parameters"

class UserCalendarController(Resource):

    def delete(self, email=None):
        if email is not None:
            CalendarModel.delete_email(email)
            return None, 204
        else:
            abort(http_status_code=400, error_code = error_enum.email_not_found)

    def get(self, user_id = None):
        if user_id is not None:
            return CalendarModel.get_all_emails(user_id), 200
        else:
            abort(http_status_code=400, error_code = error_enum.user_id_missing)

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
        print database
        print "added to databse -----------------------------------------------------------------------------------------"
        result = CalendarModel.add_calendar(calendar_details)
        if not result:
            abort(http_status_code=404, error_code=error_enum.calendar_exception)
        else:
            database.pop(username)
            print database
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

