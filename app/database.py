# ------- IMPORTS -------
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# ------- SETUP -------
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./biscuit.db"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(
    autocommit = False,
    autoflush = False,
    bind = engine,
    expire_on_commit = False,
    class_ = AsyncSession
)

# ------- CLASSES -------
class Base(DeclarativeBase):
    pass

# ------- FUNCTIONS -------
async def get_database():
    async with AsyncSessionLocal() as database:
        yield database