from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship


from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    voornaam = Column(String)
    achternaam = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    posts = relationship("Post", back_populates="users")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    titel = Column(String, unique=True)
    text = Column(String)
    date = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    type_id = Column(Integer, ForeignKey("types.id"))

    users = relationship("User", back_populates="posts")
    types = relationship("Type", back_populates="posts")


class Type(Base):
    __tablename__ = "types"
    id = Column(Integer, primary_key=True, index=True)
    type_naam = Column(String, unique=True)

    posts = relationship("Post", back_populates="types")


class Admin(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
