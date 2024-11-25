from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date
from typing import Optional

class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    additional_data: Optional[str] = None

class ContactSchema(BaseModel):
    title: str
    description: str

class ContactUpdateSchema(ContactSchema):
    completed: bool
class ContactResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    additional_data: Optional[str]
    model_config = ConfigDict(from_attributes = True)  #noqa

