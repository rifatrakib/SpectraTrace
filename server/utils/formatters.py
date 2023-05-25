from datetime import datetime, timezone

from pydash import camel_case


def format_datetime_into_isoformat(ts: datetime) -> str:
    return ts.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


def format_dict_key_to_camel_case(key: str) -> str:
    return camel_case(key)
