from typing import Any, Dict, Union

from fastapi import Depends, Header, HTTPException
from sqlmodel import Session

from server.database.audit.auth import check_user_access_key
from server.database.managers import cache_data, is_in_cache, read_from_cache
from server.security.dependencies.sessions import get_database_session
from server.utils.messages import raise_401_unauthorized


def verify_api_key(
    api_key: Union[str, None] = Header(
        default=None,
        title="API Key",
        description="API Key",
        example="1234567890",
    ),
) -> str:
    if not api_key:
        raise raise_401_unauthorized(message="API Key is required.")
    return api_key


async def verify_user_access(
    api_key: str = Depends(verify_api_key),
    session: Session = Depends(get_database_session),
) -> Dict[str, Any]:
    try:
        if not is_in_cache(key=api_key):
            user = await check_user_access_key(session, api_key)
            cache_data(key=api_key, data=user.json())
            return user.dict()

        user = read_from_cache(key=api_key)
        return user
    except HTTPException as e:
        raise e
