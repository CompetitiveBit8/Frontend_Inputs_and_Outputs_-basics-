from sqlalchemy import Column, Integer, String
from app.db.database import Base_pg, Base_sqlite

class UserDetails(Base_pg):
    __tablename__ = "user_details"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String, index=True)


class posts_old(Base_pg):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    author = Column(String, index=True)

class posts(Base_sqlite):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    author = Column(String, index=True)
    fileName = Column(String, index=True)