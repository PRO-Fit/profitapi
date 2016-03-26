from app.controllers.calendars import CalendarAuthController, CalendarAuthRedirectController, CalendarController

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
        'endpoint': CalendarController,
        'routes': [
            '/v1/calendars/google/<email>'
        ]
    }
]
