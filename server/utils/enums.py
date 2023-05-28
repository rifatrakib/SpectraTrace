from enum import Enum


class Tags(str, Enum):
    health_check = "Health Check"
    authentication = "Authentication"
    user = "User"
    audit = "Audit"
