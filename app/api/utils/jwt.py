from datetime import datetime, timedelta

import jwt

from config. config import ServiceConfig

ALGORITHM = "HS256"
access_token_jwt_subject = "access"


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    config = ServiceConfig()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire, "sub": access_token_jwt_subject})
    encoded_jwt = jwt.encode(to_encode, config.settings.secret_key.get_secret_value(), algorithm=ALGORITHM)
    return encoded_jwt
