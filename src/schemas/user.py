from pydantic import constr,BaseModel, EmailStr,ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username:constr(min_length=3, max_length=50)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str
    avatar: str
    model_config = ConfigDict(from_attributes=True)  # noqa


class RequestEmail(BaseModel):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"