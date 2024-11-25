from passlib.context import CryptContext
from jose import JWTError, jwt
from src.conf.config import config
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """
    Hashes the given password using a secure hashing algorithm.

    This function takes a plain password as input and returns a hashed version of the password
    using the configured password hashing context.

    :param password: The plain password to be hashed.
    :type password: str
    :return: The hashed password.
    :rtype: str
    :raises ValueError: If the password is empty or invalid.
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain password matches a hashed password.

    This function compares the plain password with the hashed password and returns a boolean
    indicating whether the two passwords match.

    :param plain_password: The plain password to verify.
    :type plain_password: str
    :param hashed_password: The hashed password to compare against.
    :type hashed_password: str
    :return: True if the passwords match, False otherwise.
    :rtype: bool
    :raises ValueError: If either of the passwords is empty or invalid.
    """
    return pwd_context.verify(plain_password, hashed_password)

