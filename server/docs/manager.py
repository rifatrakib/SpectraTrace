from server.config.factory import settings
from server.utils.enums import Tags


def read_api_metadata():
    with open("server/docs/README.md") as reader:
        description = reader.read()

    return {
        "title": settings.APP_NAME,
        "description": description,
        "version": "0.1.0",
        "terms_of_service": "https://www.linkedin.com/in/md-abdur-rakib-1508/",
        "contact": {
            "name": f"Maintainer: {settings.APP_NAME}",
            "url": "https://www.linkedin.com/in/md-abdur-rakib-1508/",
            "email": "abdur.rakib.1508@gmail.com",
        },
    }


def read_tags_metadata():
    return [
        {
            "name": Tags.health_check.value,
            "description": "Verify *server operability* and *configuration variables*.",
            "externalDocs": {
                "description": "Server Health Check",
                "url": "https://www.linkedin.com/in/md-abdur-rakib-1508/",
            },
        },
        {
            "name": Tags.authentication.value,
            "description": "Endpoints for *user authentication*",
            "externalDocs": {
                "description": "User authentication documentation",
                "url": "https://www.linkedin.com/in/md-abdur-rakib-1508/",
            },
        },
        {
            "name": Tags.user.value,
            "description": "Endpoints for *user information*",
            "externalDocs": {
                "description": "Users information documentation",
                "url": "https://www.linkedin.com/in/md-abdur-rakib-1508/",
            },
        },
        {
            "name": Tags.audit.value,
            "description": "Endpoints for *audit log service*",
            "externalDocs": {
                "description": "Audit log service documentation",
                "url": "https://www.linkedin.com/in/md-abdur-rakib-1508/",
            },
        },
    ]
