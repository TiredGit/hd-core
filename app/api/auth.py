from fastapi import APIRouter

from app.database.database import db_session
from app.schemas.auth import (
    RefreshRequest,
    RegisterResponse,
    Token,
    UserLogin,
    UserRegister, TokenRefresh,
)
from app.services.auth import register_user, login_user, refresh_user_tokens

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=RegisterResponse)
async def register(user_data: UserRegister, db: db_session):
    new_user = await register_user(db, user_data)
    return {
        "message": "User created",
        "user_id": str(new_user.id),
        "user_phone": str(new_user.phone),
    }


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: db_session):
    return await login_user(
        db,
        login_data.phone,
        login_data.password,
    )


@router.post("/refresh", response_model=TokenRefresh)
async def refresh_token(payload: RefreshRequest, db: db_session):
    return await refresh_user_tokens(
        db,
        payload.refresh_token,
    )