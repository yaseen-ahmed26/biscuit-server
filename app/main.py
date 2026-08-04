# ------- IMPORTS -------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_swagger_ui_theme import setup_swagger_ui_theme

from contextlib import asynccontextmanager

from app.database import Base, engine
from app.routes import users, codes, saves, auth
from app.constants import ORIGINS

# ------- CONSTANTS -------
ROUTERS = [
    {
        "router": users.router,
        "prefix": "/api/users",
        "tags": ["users"],
    },
    {
        "router": codes.router,
        "prefix": "/api/codes",
        "tags": ["codes"],
    },
    {
        "router": auth.router,
        "prefix": "/api/auth",
        "tags": ["auth"],
    },
    {
        "router": saves.router,
        "prefix": "/api/saves",
        "tags": ["saves"],
    },
]

# ------- SETUP -------
@asynccontextmanager
async def lifespan(_app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(lifespan = lifespan, docs_url = None)

for router in ROUTERS:
    app.include_router(**router)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ORIGINS,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]
)

# Dark Mode
setup_swagger_ui_theme(
    app, 
    docs_path = "/docs", 
    title = "Swagger Docs"
)

# ------- HOME -------
@app.get("/", include_in_schema = False)
async def home():
    return {"message": "Biscuit Backend is running"}