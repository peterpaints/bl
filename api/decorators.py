from functools import wraps

from flask import abort, request

from models.models import User


def check_access_token(func):
    """Ensure a function can only be executed if there is a token."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token:
            user_id = User.decode_token(access_token)
            if isinstance(user_id, str):
                abort(404, user_id)
            request.user_id = user_id
        return func(*args, **kwargs)
    return wrapper
