from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.database.db import get_db
from src.models.models import User
from src.utils.security import oauth2_scheme
from jose import JWTError, jwt
from src.conf.config import config


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """
    Retrieves the current user from the database based on the provided JWT token.

   This function decodes the provided JWT token, extracts the email of the user (subject) from the payload,
   and queries the database to find a user with that email. If the token is invalid or the user cannot be found,
   an HTTP 401 Unauthorized error is raised.

    :param db: The database session used to query for the user.
    :type db: AsyncSession
    :param token: The JWT token containing the user's credentials.
    :type token: str
    :return: The user object if the credentials are valid and the user is found.
    :rtype: User
    :raises HTTPException: If the credentials are invalid, or if the user cannot be found in the database.
    :raises JWTError: If decoding the JWT token fails.
   """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY_JWT, algorithms=[config.ALGORITHM])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    query = select(User).filter(User.email == user_email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    return user
