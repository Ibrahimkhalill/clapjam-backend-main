import datetime
from django.utils import timezone as tz


def current_timestamp() -> int:
    return int(tz.make_aware(
        datetime.datetime.now(), tz.get_default_timezone()).timestamp() * 1000) # milliseconds


def get_clean_dict(obj, target_key: str='_state') -> dict:
    _dict: dict = obj.__dict__.copy()
    if target_key in _dict: _dict.pop(target_key)
    return _dict    