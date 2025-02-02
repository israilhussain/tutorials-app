from sqlalchemy import Column, Integer, String
# from ..base import Base
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    hashed_password = Column(String)