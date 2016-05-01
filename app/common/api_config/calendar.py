from app.controllers.calendars import CalendarAuthController, CalendarAuthRedirectController, UserCalendarController,\
                                      CalendarEventsController
from app.controllers.sessions import UserSessionController, UserBlockedSessionController, FreeSlotsController, NotificationController

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
            '/v1/users/<user_id>/sessions',
            '/v1/users/<user_id>/sessions/<session_id>',
        ]
    },
    {
        'endpoint': UserBlockedSessionController,
        'routes': [
            '/v1/users/<user_id>/blocksessions',
            '/v1/users/<user_id>/blocksessions/days/<day>',
            '/v1/users/<user_id>/blocksessions/<session_id>',
        ]
    },
    {
        'endpoint': CalendarEventsController,
        'routes': [
            '/v1/users/<user_id>/calendars/events/<email_id>'
        ]
    },
    {
        'endpoint': FreeSlotsController,
        'routes': [
            '/v1/users/<user_id>/calendars/freeslots'
        ]
    },
    {
        'endpoint': NotificationController,
        'routes': [
            '/v1/users/<user_id>/notifications/sessions',
            '/v1/users/<user_id>/notifications/sessions/<session_id>',
        ]
    }
]
