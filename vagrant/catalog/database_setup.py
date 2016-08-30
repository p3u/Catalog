import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(String(250), ForeignKey('user.id'))


class Product(Base):
    __tablename__ = "product"

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    category = relationship(Category)
    category_id = Column(Integer, ForeignKey('category.id'))
    imgpath = Column(String)
    user_id = Column(String(250), ForeignKey('user.id'))


class User(Base):
    __tablename__ = "user"
    id = Column(String(250), primary_key=True)
    email = Column(String(250))

engine = create_engine('sqlite:///catalog.db')


Base.metadata.create_all(engine)
