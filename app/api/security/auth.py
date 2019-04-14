import logging
from typing import Optional

from passlib.context import CryptContext
import jwt
from jwt import PyJWTError

from fastapi import HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_403_FORBIDDEN

from api.utils.jwt import ALGORITHM
from api.models.token import TokenPayload

from config.config import ServiceConfig, UserSettings
from api.constants.constants import WalletPermission

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def user_authenticate(username: str, password: str) -> Optional[UserSettings]:
    config = ServiceConfig()

    for user in config.users:
        if user.username != username:
            continue

        logging.info(f'trying to match {get_password_hash(password)}')
        if not verify_password(password, user.password_hash.get_secret_value()):
            continue

        return user

    return None


def get_user_by_username(username: str) -> Optional[UserSettings]:
    config = ServiceConfig()

    for user in config.users:
        if user.username != username:
            continue

        return user

    return None


def get_current_user(token: str = Security(reusable_oauth2)) -> Optional[UserSettings]:
    config = ServiceConfig()
    try:
        logging.info(f'got token: {token}')
        payload = jwt.decode(token, config.settings.secret_key.get_secret_value(), algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
        logging.info(f'got payload: {token_data}')
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    user = get_user_by_username(username=token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def user_has_wallet_permission(current_user: UserSettings, wallet_name: str, permission: WalletPermission) -> bool:
    for wallet in current_user.wallet_permissions:
        if wallet.wallet_name != wallet_name:
            continue
        if permission not in wallet.permissions:
            continue
        return True

    return False


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)
