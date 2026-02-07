from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.database import Base, Base_sqlite_old
from sqlalchemy.orm import relationship

class UserDetails(Base):
    __tablename__ = "user_details"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    password = Column(String, index=True)


class posts(Base_sqlite_old):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String, index=True)
    author = Column(String, index=True)

    image = relationship("images", back_populates="post")



class images(Base_sqlite_old):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True)
    file_path = Column(String, index=True)
    file_name = Column(String, index=True)
    file_type = Column(String, index=True)
    post_id = Column(Integer, ForeignKey(posts.id))

    post = relationship("posts", back_populates="image") 