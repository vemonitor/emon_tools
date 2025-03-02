"""
FastApi login routes
"""
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from emon_tools.fastapi import crud
from emon_tools.fastapi.api.deps import CurrentUser
from emon_tools.fastapi.api.deps import SessionDep
from emon_tools.fastapi.core import security
from emon_tools.fastapi.core.config import settings
from emon_tools.fastapi.models.db import Token
from emon_tools.fastapi.models.db import UserPublic


router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    response: Response,
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = security.create_refresh_token(
        user.id, expires_delta=refresh_token_expires
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_COOKIE_EXPIRE_SECONDS
    )
    return Token(
        access_token=access_token
    )


@router.post("/login/refresh-token")
def login_refresh_token(
    response: Response,
    session: SessionDep,
    refresh_token: str = Depends(security.get_refresh_token_from_cookie)
) -> Token:
    """
    OAuth2 compatible token login, get an refresh token for future requests
    """
    try:
        user_id = security.decode_refresh_token(refresh_token)
    except security.InvalidToken as ex:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        ) from ex

    user = crud.get_user(session=session, user_id=user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="Invalid user or inactive user"
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = security.create_refresh_token(
        user.id, expires_delta=refresh_token_expires
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_COOKIE_EXPIRE_SECONDS
    )
    return Token(
        access_token=access_token
    )


@router.post("/logout")
async def logout(response: Response):
    """
    Logout
    """
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user
