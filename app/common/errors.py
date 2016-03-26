from collections import namedtuple

_error_tokens = [
    'user_id_missing',
    'user_id_not_found',
    'user_id_duplicate',
    'calendar_exception',
    'email_add_already_present',
    'email_not_found',
    'goal_id_missing',
    'database_error_inserting',
    'database_error_updating',
    'database_error_deleting',
    'goal_overlap'
]

error_enum = namedtuple('Errors', _error_tokens)(*_error_tokens)
