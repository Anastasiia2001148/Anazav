from asyncio.log import logger

from fastapi import APIRouter, status

from src.database.db import get_db
from src.repository import repository
from fastapi_limiter.depends import RateLimiter
from src.schemas.user import UserCreate, Token, RequestEmail
from src.models.models import User
from src.utils.auth import verify_password
from src.utils.check import create_access_token, create_refresh_token, auth_service
from src.repository.repository import get_user_by_email
from fastapi.security import OAuth2PasswordRequestForm
from src.utils.auth import pwd_context
from src.utils.email import send_email

from fastapi import HTTPException, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse


router = APIRouter()
api_router = APIRouter()

@router.post("/register", response_model=Token, tags=["auth"])
async def register(user_data: UserCreate, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Registers a new user and sends a confirmation email.

    This endpoint allows users to register with their email, username, and password. After the user is
    created, an email with a confirmation token is sent, and the user receives access and refresh tokens.

    :param user_data: The user registration data (email, username, and password).
    :type user_data: UserCreate
    :param bt: The background task to send the confirmation email.
    :type bt: BackgroundTasks
    :param request: The incoming HTTP request used to construct the base URL for email confirmation.
    :type request: Request
    :param db: The database session.
    :type db: AsyncSession
    :return: A JSON response with the access token, refresh token, and user information.
    :rtype: JSONResponse
    :raises HTTPException: If the email is already registered or an internal error occurs during registration.
    """
    existing_user = await get_user_by_email(user_data.email, db)
    if existing_user:
        raise HTTPException(status_code=409, detail="User with this email already exists.")


    hashed_password = pwd_context.hash(user_data.password)
    new_user = User(email=user_data.email, hashed_password=hashed_password, username=user_data.username)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    access_token = create_access_token(data={"sub": new_user.email})
    refresh_token = create_refresh_token(data={"sub": new_user.email})

    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))

    return JSONResponse(
        status_code=201,
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "email": new_user.email,
                "id": new_user.id,
                'username': new_user.username
            }
        }
    )



@router.post("/login",tags=["auth"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    Logs in a user and provides access and refresh tokens.

    This endpoint authenticates the user by verifying the email and password. If successful, it returns
    an access token and a refresh token. If the email is not confirmed, it raises an error.

    :param form_data: The user's login credentials (email and password).
    :type form_data: OAuth2PasswordRequestForm
    :param db: The database session.
    :type db: AsyncSession
    :return: A dictionary with the access token, refresh token, and token type.
    :rtype: dict
    :raises HTTPException: If the email or password is incorrect, or if the email is not confirmed.
    """
    user = await get_user_by_email(form_data.username, db)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed",
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, 'refresh_token': refresh_token, "token_type": "bearer"}


@api_router.get('/confirmed_email/{token}',tags=["auth"])
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Confirms the user's email address via a token.

    This endpoint allows the user to confirm their email address by providing a verification token.
    If the user has already confirmed their email, a message is returned indicating that the email is
    already confirmed.

    :param token: The email confirmation token.
    :type token: str
    :param db: The database session.
    :type db: AsyncSession
    :return: A confirmation message.
    :rtype: dict
    :raises HTTPException: If the user is not found or if verification fails.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository.confirmed_email(email, db)
    return {"message": "Email confirmed"}




@router.post('/request_email',tags=["auth"])
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Requests an email confirmation for a user.

    This endpoint sends an email confirmation request to the user. If the email is already confirmed,
    a message indicating that is returned. If the user is found but the email is not confirmed, a confirmation
    email is sent.

    :param body: The request email data (user's email address).
    :type body: RequestEmail
    :param background_tasks: Background tasks for sending the email.
    :type background_tasks: BackgroundTasks
    :param request: The incoming HTTP request used to construct the base URL for email confirmation.
    :type request: Request
    :param db: The database session.
    :type db: AsyncSession
    :return: A message indicating the status of the confirmation email.
    :rtype: dict
    """
    user = await repository.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


