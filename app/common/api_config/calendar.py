from app.controllers.calendars import CalendarAuthController, CalendarAuthRedirectController, UserCalendarController
from app.controllers.sessions import UserSessionController

calendar_api_config = [
    {
        'endpoint': CalendarAuthController,
        'routes': [
            '/v1/calendars/google/oauth2/<user_id>/<email>'
        ]
    },
    {
        'endpoint': CalendarAuthRedirectController,
        'routes': [
            '/v1/calendars/google/oauth2callback'
        ]
    },
    {
        'endpoint': UserCalendarController,
        'routes': [
            '/v1/users/<user_id>/calendars/google/<email>',
            '/v1/users/<user_id>/calendars/google'
        ]
    },
    {
        'endpoint': UserSessionController,
        'routes': [
            '/v1/users/<user_id>/session/',
            '/v1/users/<user_id>/session/<session_id>',
        ]
    },
]
