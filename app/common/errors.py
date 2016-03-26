from collections import namedtuple
from error_tokens.calendar import tokens as calendar_errors
from error_tokens.user import tokens as user_errors
from error_tokens.database import tokens as database_errors

error_enum = namedtuple(
    'Errors',
    calendar_errors + user_errors + database_errors
)(
    *calendar_errors + user_errors + database_errors
)
