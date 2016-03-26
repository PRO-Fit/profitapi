from app.controllers.users import UserController, UserPreferenceController
from app.controllers.goals import GoalController

user_api_config = [
    {
        'endpoint': UserController,
        'routes': [
            '/v1/users',
            '/v1/users/<user_id>'
            ]
    },
    {
        'endpoint': GoalController,
        'routes': [
            '/v1/users/<user_id>/goals',
            '/v1/users/<user_id>/goals/<goal_id>'
            ]
    },
    {
        'endpoint': UserPreferenceController,
        'routes': [
            '/v1/users/<user_id>/preferences'
            ]
    }
]
