from fastapi import FastAPI

from server.config.factory import settings
from server.database.managers import create_db_and_tables, ping_redis_server
from server.routes.auth import router as auth_router
from server.routes.user import router as user_router
from server.schemas.base import HealthResponseSchema
from server.utils.enums import Tags

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    print("Starting up...")

    print("Creating relational database and tables...")
    create_db_and_tables()
    print("Relational database and tables created!")

    print("Ping Redis server...")
    ping_redis_server()
    print("Redis server pinged!")

    print("Startup complete!")


@app.get("/health", response_model=HealthResponseSchema, tags=[Tags.health_check])
async def health():
    return settings


app.include_router(auth_router)
app.include_router(user_router)
