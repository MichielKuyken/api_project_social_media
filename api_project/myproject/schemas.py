from pydantic import BaseModel
from datetime import datetime


class UserBase(BaseModel):
    username: str
    voornaam: str
    achternaam: str
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


class PostBase(BaseModel):
    titel: str
    text: str
    date: datetime = None
    user_id: int | None = None
    type_id: int


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int

    class Config:
        orm_mode = True


class TypeBase(BaseModel):
    type_naam: str


class TypeCreate(TypeBase):
    pass


class Type(TypeBase):
    id: int

    class Config:
        orm_mode = True


class AdminBase(BaseModel):
    username: str


class AdminCreate(AdminBase):
    password: str


class Admin(AdminBase):
    id: int

    class Config:
        orm_mode = True