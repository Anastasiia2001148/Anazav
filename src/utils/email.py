from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.utils.check import auth_service
from src.conf.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_USERNAME,
    MAIL_PORT=config.PORT,
    MAIL_SERVER= config.MAIL_SERVER,
    MAIL_FROM_NAME="Verify System",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends an email to the user for email verification with a verification token.

    This function generates a token for email verification using the provided email address, creates an
    email message with a confirmation link, and sends the email using the configured email service.

    :param email: The email address of the user to whom the verification email will be sent.
    :type email: EmailStr
    :param username: The username of the user to include in the verification email message.
    :type username: str
    :param host: The host URL used to generate the verification link.
    :type host: str
    :return: None
    :raises ConnectionErrors: If an error occurs while trying to send the email, such as a connection failure.
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "user_id": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)