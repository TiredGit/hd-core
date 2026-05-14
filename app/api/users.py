from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import db_session
from app.database.models import User
from app.services.auth import get_current_user
from app.schemas.users import UserFullUpdate, UserMeResponse
from app.services.users import get_my_profile, update_full_user_data

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserMeResponse)
async def get_my_profile_endpoint(
    current_user: User = Depends(get_current_user),
):
    return await get_my_profile(current_user)


@router.patch("/me", response_model=UserMeResponse)
async def update_my_full_profile(
    db: db_session,
    update_data: UserFullUpdate,
    current_user: User = Depends(get_current_user),
):
    if not update_data.model_dump(exclude_unset=True):
        raise HTTPException(status_code=400, detail="Не передано данных для обновления")

    return await update_full_user_data(current_user, db, update_data)