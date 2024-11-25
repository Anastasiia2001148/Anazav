import logging

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from src.routes import users
from src.routes.routes import router as contacts_router
from src.routes.auth import router as auth_router, api_router
from src.database.db import get_db
from src.models.models import Base
from src.database.db import sessionmanager
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware
import redis.asyncio as redis
from src.conf.config import config
from fastapi_limiter import FastAPILimiter


app = FastAPI()

app.include_router(api_router, prefix="/api/auth")
app.include_router(auth_router, prefix="/auth")
app.include_router(contacts_router)
app.include_router(users.router, prefix="/api/users")

@app.on_event("startup")
async def startup():
    """
    Initializes Redis and FastAPI limiter during the startup of the application.

    This function is called when the FastAPI app starts. It establishes a
    connection to the Redis server, sets up FastAPILimiter, and makes
    sure that the limiter is ready to use for limiting the number of requests.
    :raises ConnectionError: If the Redis server is not accessible or fails to connect.
    :raises SQLAlchemyError: If an error occurs while initializing the database.
    """
    try:
        r = await redis.Redis(
            host=config.REDIS_DOMAIN,
            port=config.REDIS_PORT,
            db=0,
            password=config.REDIS_PASSWORD,
        )
        await FastAPILimiter.init(r)

        async with sessionmanager._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        logging.info("Startup completed successfully.")
    except Exception as e:
        logging.error(f"Error during startup: {e}")
        raise HTTPException(status_code=500, detail="Error during startup")

templates = Jinja2Templates(directory="src/templates")


origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    """
    Returns a simple message indicating the application's success.

   :return: A dictionary with a message confirming the app is running.
    :rtype: dict
   """
    return {"message": "Homework 14"}

@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
    Checks the health of the application by verifying the database connection.

    This endpoint executes a simple query (`SELECT 1`) to check the health of the database.
    If the database is properly configured, it returns a success message. Otherwise, it raises
    an HTTP exception.

    :param db: The database session that is used for the health check.
    :type db: AsyncSession
    :return: A health check message if the database is configured correctly.
    :rtype: dict
    :raises HTTPException: If the database is not properly configured or an error occurs during the check.
    """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")




