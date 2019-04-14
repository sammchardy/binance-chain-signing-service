import json
from datetime import timedelta

from fastapi import APIRouter, HTTPException

from config.config import ServiceConfig
from api.security.auth import user_authenticate
from api.utils.jwt import create_access_token
from api.models.token import Token
from api.models.auth import Login

router = APIRouter()


@router.post("/auth/login", response_model=Token, tags=["login"])
def login(login_details: Login):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    config = ServiceConfig()
    user = user_authenticate(username=login_details.username, password=login_details.password)
    if not user:
        raise HTTPException(status_code=400, detail=json.dumps({"error": "Incorrect email or password"}))
    access_token_expires = timedelta(minutes=config.settings.access_token_expiry_minutes)
    return {
        "access_token": create_access_token(
            data={"username": user.username}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
