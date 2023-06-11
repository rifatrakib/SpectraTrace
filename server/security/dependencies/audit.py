from typing import Any, Dict, Union

from fastapi import Depends, Header, HTTPException, Query
from sqlmodel import Session

from server.database.audit.auth import check_user_access_key
from server.database.cache.ops import cache_data, is_in_cache, read_from_cache
from server.schemas.inc.audit import AuditRetrievalRequestSchema
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
        is_valid, _ = is_in_cache(key=api_key)
        if not is_valid:
            user = await check_user_access_key(session, api_key)
            cache_data(key=api_key, data=user.json())
            return user.dict()

        user, _ = read_from_cache(key=api_key)
        return user
    except HTTPException as e:
        raise e


def log_retrieval_query_parameters(
    category: str = Query(title="Category", description="Category", example="http_events"),
    app: str = Query(title="Application", description="Application", example="spectratrace_api"),
    env: Union[str, None] = Query(default=None, title="Environment", description="Environment"),
    method: Union[str, None] = Query(default=None, title="Method", description="Method"),
    status: Union[str, None] = Query(default=None, title="Status", description="Status"),
    origin: Union[str, None] = Query(default=None, title="Origin", description="Origin"),
    start: Union[str, None] = Query(default="1d", title="Start", description="Start time"),
    stop: Union[str, None] = Query(default="now()", title="Stop", description="Stop time"),
) -> AuditRetrievalRequestSchema:
    return AuditRetrievalRequestSchema(
        category=category,
        app=app,
        env=env,
        method=method,
        status=status,
        origin=origin,
        start=start,
        stop=stop,
    )
