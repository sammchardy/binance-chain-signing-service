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

from config.config import ServiceConfig, UserSettings, WalletConfig
from api.constants.constants import WalletPermission

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def user_authenticate(username: str, password: str) -> Optional[UserSettings]:
    config = ServiceConfig()

    for user in config.users:
        if user.username != username:
            continue

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
        payload = jwt.decode(token, config.settings.secret_key.get_secret_value(), algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )

    user = get_user_by_username(username=token_data.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def assert_user_has_wallet_permission(user: UserSettings, wallet_name: str, permission: WalletPermission):
    if not user.has_wallet_permission(wallet_name, permission):
        raise HTTPException(
            status_code=403,
            detail=f"User has no permission {permission} on wallet {wallet_name}"
        )


def assert_wallet_has_permission(wallet: WalletConfig, permission: WalletPermission):
    if not wallet.has_permission(permission):
        raise HTTPException(status_code=403, detail=f"No permission {permission}")


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str):
    return pwd_context.hash(password)
