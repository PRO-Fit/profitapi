# DB_CONFIG = {
#     'user': 'root',
#     'password': 'admin',
#     'host': 'localhost',
#     'database': 'profit',
#     'raise_on_warnings': True
# }

from collections import namedtuple

DB_CONFIG = {
    'user': 'root',
    'password': 'Profit123',
    'host': 'profitdb.cfmxakdibe3m.us-west-2.rds.amazonaws.com',
    'database': 'profit',
    'raise_on_warnings': True
}

CAL_CONFIG = {
    'CLIENT_ID': '761634219599-k2egp1a53gae9hv723tjr7ukauuinuo9.apps.googleusercontent.com',
    'CLIENT_SECRET': 'aOkLp_klNre103WCMt8P9nHu',  # Read from a file or environmental variable in a real app
    'SCOPE': 'https://www.googleapis.com/auth/calendar.readonly',
    'REDIRECT_URI': 'http://ec2-54-67-63-89.us-west-1.compute.amazonaws.com:8080/v1/calendars/google/oauth2callback'
}

# created mailgun acount to verify the email address whether it exists or not.
# https://mailgun.com, key should be included in request to veriy email address
MAIL_GUN = {
    'KEY': 'pubkey-f7b4a94467c20f067b253337b5d06023'
}

GMAIL_API = {
    'KEY': 'AIzaSyBmqCFXjVukY_h_DwguQr8_N1M8sVviDBw'
}

GMAIL_EVENTS_URLS = {
    'EVENTS': 'https://www.googleapis.com/calendar/v3/calendars/primary/events',
    'ACCESS_TOKEN': 'https://www.googleapis.com/oauth2/v4/token'
}

SESSION_STATUS = ['USER_CREATED', 'REC_ACCEPTED', 'REC_REJECTED', 'NOT_NOTIFIED', 'NOTIFIED']

session_status = namedtuple(
    'SESSION_STATUS',
    SESSION_STATUS
)(
    *SESSION_STATUS
)

