# ------- IMPORTS -------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_swagger_ui_theme import setup_swagger_ui_theme

from contextlib import asynccontextmanager

from app.routes import codes
from database import Base, engine
from routes import users

# ------- SETUP -------
@asynccontextmanager
async def lifespan(_app: FastAPI):
    # On Startup.
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()

app = FastAPI(lifespan = lifespan, docs_url = None)

app.include_router(
    users.router, 
    prefix = "/api/users",
    tags = ["users"]
)

app.include_router(
    codes.router, 
    prefix = "/api/codes",
    tags = ["codes"]
)

origns = [
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origns,
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