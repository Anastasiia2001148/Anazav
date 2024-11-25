from typing import Any

from pydantic import ConfigDict,field_validator,EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = 'postgresql+asyncpg://postgres:mysecretpassword@localhost:5432/newdatabase'

    SECRET_KEY_JWT: str = 'VsDxQG7uDFvyn8sozSuRU4h4wQhxb5lXvSdMR5Lr9fs='
    ALGORITHM: str = 'HS256'
    MAIL_USERNAME: EmailStr = 'zavalovanasta7@gmail.com'
    MAIL_PASSWORD: str= 'wbgx pxoe tdje imjm'
    MAIL_FROM: str = 'zavalovanasta7@gmail.com'
    PORT: int = 587
    MAIL_SERVER: str='smtp.gmail.com'
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None


    CLD_NAME:str = 'dwbh4irmh'
    CLD_API_KEY:int = 817174299541917
    CLD_API_SECRET:str = 'CBqxEy_cCJ-OK81beurLxexjnuQ'


    @field_validator('ALGORITHM')
    @classmethod
    def validate_algorithm(cls,v:Any):
        if v not in ['HS256', 'HS512']:
            raise ValueError('algorithm must be  HS256')
        return v

    model_config = ConfigDict(extra = 'ignore',env_file = ".env", env_file_encoding = "utf-8")  #noqa


config = Settings()