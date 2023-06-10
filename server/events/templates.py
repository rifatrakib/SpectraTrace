from functools import lru_cache

from pydantic import parse_file_as

from server.schemas.inc.audit import AuditRequestSchema


@lru_cache()
def get_event_template(filename: str) -> AuditRequestSchema:
    return parse_file_as(
        type_=AuditRequestSchema,
        path=f"server/templates/events/{filename}.json",
    )
