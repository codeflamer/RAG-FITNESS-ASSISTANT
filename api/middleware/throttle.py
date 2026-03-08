from slowapi import Limiter
from starlette.requests import Request


def get_user_key(request:Request):
    user_id = request.headers.get("X-User-ID")
    if user_id:
        return user_id
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

limiter = Limiter(key_func=get_user_key, default_limits=["2/minute"])