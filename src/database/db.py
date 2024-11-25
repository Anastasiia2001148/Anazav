import contextlib
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.conf.config import config


class DatabaseSessionManager:
    def __init__(self, url: str):
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_maker: async_sessionmaker = None

    def init_session_maker(self):
        if not self._session_maker:
            self._session_maker = async_sessionmaker(
                autoflush=False,
                autocommit=False,
                bind=self._engine
            )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Session maker is not initialized")
        session = self._session_maker()
        try:
            yield session
        except Exception as err:
            print(f"Session error: {err}")
            await session.rollback()
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(config.DB_URL)
sessionmanager.init_session_maker()

async def get_db():
    try:
        async with sessionmanager.session() as session:
            yield session
    except Exception as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")