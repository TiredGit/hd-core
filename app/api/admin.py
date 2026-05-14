from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from app.database.database import db_session

from app.database.models import User, UserRole
from app.services.auth import get_current_admin_user
from app.schemas.admin import UserCreateRequest, UserResponse, UserUpdateRequest, UserActive
from app.services import admin as admin_service

router = APIRouter(prefix="/admin/users", tags=["admin"])


@router.get("/", response_model=list[UserResponse])
async def read_users(
    db: db_session,
    skip: int = Query(0, ge=0, description="Pagination skip"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    _: User = Depends(get_current_admin_user),
):
    return await admin_service.list_users(
        db,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def read_user_by_id(
    db: db_session,
    user_id: int,
    _: User = Depends(get_current_admin_user),
):
    return await admin_service.get_user_by(db, id=user_id)


@router.get("/phone/{user_phone}", response_model=UserResponse)
async def read_user_by_phone(
    db: db_session,
    user_phone: str,
    _: User = Depends(get_current_admin_user),
):
    return await admin_service.get_user_by(db, phone=user_phone)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    db: db_session,
    data: UserCreateRequest,
    _: User = Depends(get_current_admin_user),
):
    return await admin_service.create_user(db, data)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    db: db_session,
    user_id: int,
    data: UserUpdateRequest,
    _: User = Depends(get_current_admin_user),
):
    return await admin_service.update_user(db, user_id, data)


@router.post("/activate/{user_id}", response_model=UserActive)
async def deactivate_user_by_user_id(
    db: db_session,
    user_id: int,
    _: User = Depends(get_current_admin_user),
):
    return await admin_service.activate_deactivate_user(db, user_id)