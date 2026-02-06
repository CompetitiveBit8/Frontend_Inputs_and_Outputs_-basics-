from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

load_dotenv()

class Settings(BaseSettings):
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_time: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTE")
    refresh_token_expire_days: int = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
    _link: str = os.getenv("users")
    sq_link: str = os.getenv("sqlite_1")
    sq_link_old: str = os.getenv("sqlite_2")
    


settings = Settings()   