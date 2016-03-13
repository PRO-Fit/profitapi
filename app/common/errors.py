from collections import namedtuple

_error_tokens = [
    'user_id_missing',
    'user_id_not_found',
    'user_id_duplicate'
]

error_enum = namedtuple('Errors', _error_tokens)(*_error_tokens)
