from sqlalchemy import Column, String, Date,Boolean, Integer,ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contapp'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), index=True)
    description = Column(String(250))
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String)
    birthday = Column(Date)
    additional_data = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="contacts")

class User(Base):
    __tablename__ = 'users'
    id =  Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String,unique=True, index=True)
    hashed_password = Column(String)
    avatar = Column(String(255), nullable=True)
    contacts = relationship('Contact', back_populates='user')
    confirmed= Column(Boolean, default=False)

class Token(BaseModel):
    access_token: str
    token_type:str
    refresh_token:str