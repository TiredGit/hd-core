from typing import Optional

from pydantic import BaseModel, Field


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)

    # Для обычного пользователя адрес лучше сделать обязательным
    address: str = Field(..., min_length=3, max_length=255)
    apartment: str = Field(..., min_length=1, max_length=20)
    personal_account: str


class UserLogin(BaseModel):
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    message: str
    user_id: str
    user_phone: str