from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, Index=True)
    title = Column(String, unique=True, index=True, nullable=False)

    #Relationships
    posts = relationship("Post", back_populates="category")
