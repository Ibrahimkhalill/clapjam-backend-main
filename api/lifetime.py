import jwt
from datetime import datetime, timezone
import math

def get_token_lifetime_remaining(token: str) -> int:
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get('exp')
        if not exp:
            return 0
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        remaining_seconds = (exp_datetime - now).total_seconds()
        remaining_days = remaining_seconds * 1000
        return max(0, math.floor(remaining_days))
    except Exception:
        return 0


def get_token_remaining_days_with_request(request) -> dict:
    access_token = request.data.get('access_token')
    refresh_token = request.data.get('refresh_token')

    if not access_token:
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(' ')[1]

    return {
        'access_token_lifetime_remaining': get_token_lifetime_remaining(access_token) if access_token else 0,
        'refresh_token_lifetime_remaining': get_token_lifetime_remaining(refresh_token) if refresh_token else 0,
    }