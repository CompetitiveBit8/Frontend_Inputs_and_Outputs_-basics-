from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str

class PostSchema(BaseModel):
    title: str
    content: str
    author: str
    fileName: str