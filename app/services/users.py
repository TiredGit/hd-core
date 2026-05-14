from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.database.models import User, UserProfile, UserRole
from app.schemas.users import UserFullUpdate, UserMeResponse
from app.services.jwt_security import hash_password



async def get_my_profile(current_user: User) -> UserMeResponse:
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserMeResponse.model_validate(current_user)


async def update_full_user_data(
    current_user: User,
    db: AsyncSession,
    data: UserFullUpdate,
) -> UserMeResponse:
    update_dict = data.model_dump(exclude_unset=True)

    user_fields = ("full_name", "phone", "password")
    profile_fields = ("address", "apartment", "personal_account")

    profile_update_requested = any(update_dict.get(field) is not None for field in profile_fields)

    user_updated = False

    for field in user_fields:
        if field in update_dict:
            new_value = update_dict[field]
            if new_value is None:
                continue

            if field == "password":
                current_user.password = hash_password(new_value)
                user_updated = True
                continue

            if field == "phone" and new_value != current_user.phone:
                existing = await db.execute(
                    select(User).where(User.phone == new_value, User.id != current_user.id)
                )
                if existing.scalar_one_or_none():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Этот телефон уже занят другим пользователем",
                    )

            setattr(current_user, field, new_value)
            user_updated = True

    profile_updated = False

    if current_user.role == UserRole.USER:
        profile = current_user.profile

        if profile is None:
            if profile_update_requested:
                profile = UserProfile(user_id=current_user.id)
                current_user.profile = profile
                db.add(profile)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Для пользователя отсутствует профиль",
                )

        for field in profile_fields:
            if field in update_dict and update_dict[field] is not None:
                setattr(profile, field, update_dict[field])
                profile_updated = True

    if user_updated or profile_updated:
        await db.commit()

    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(
            selectinload(User.profile),
            selectinload(User.employee_profile),
        )
    )
    user = result.scalar_one()

    profile = user.profile
    employee_profile = user.employee_profile

    return UserMeResponse(
        id=user.id,
        full_name=user.full_name,
        phone=user.phone,
        role=user.role.value,
        address=profile.address if profile else None,
        apartment=profile.apartment if profile else None,
        personal_account=profile.personal_account if profile else None,
        employee_type=employee_profile.employee_type if employee_profile else None,
    )