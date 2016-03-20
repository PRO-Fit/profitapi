from collections import namedtuple

_error_tokens = [
    'user_id_missing',
    'user_id_not_found',
    'user_id_duplicate',
    'calendar_exception',
    'email_add_already_present',
]

error_enum = namedtuple('Errors', _error_tokens)(*_error_tokens)
