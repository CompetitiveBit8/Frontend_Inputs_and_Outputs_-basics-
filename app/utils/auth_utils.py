from passlib.context import CryptContext
from datetime import timedelta, datetime
from fastapi import Request
from jose import JWTError, jwt
import hashlib
from fastapi import Cookie, HTTPException
from app.config.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


#hashing password with sha256 before bcrypt
def _pre_hash_password(password: str):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_password(password):
    # pre_hash = _pre_hash_password(password)
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    # pre_hash = _pre_hash_password(plain_password)
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=1))
    to_encode.update({"exp": expire})
    encode_jtw = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encode_jtw

def decode_access_token(request: Request = None):
    token = request.cookies.get("access_token")

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username = payload.get("sub")
    except JWTError:
        return None
    return payload

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=settings.access_token_expire_time))
    to_encode.update({"exp": expire})
    encode_jtw = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encode_jtw

def decode_refresh_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        # username = payload.get("sub")
        return payload
    except JWTError:
        return None
    
def get_current_user(access_token: str = Cookie(None)):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Access token missing")
    try:
        payload = jwt.decode(access_token, settings.secret_key, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
