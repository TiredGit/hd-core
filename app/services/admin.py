from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import EmployeeProfile, User, UserProfile, UserRole
from app.schemas.admin import UserCreateRequest, UserUpdateRequest, UserActive
from app.services.jwt_security import hash_password


async def list_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
):
    query = select(User).options(
        selectinload(User.profile),
        selectinload(User.employee_profile),
    )

    if is_active is not None:
        query = query.where(User.is_active.is_(is_active))

    if role is not None:
        query = query.where(User.role == role)

    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


async def get_user_by(db: AsyncSession, **filters) -> User:
    query = (
        select(User)
        .filter_by(**filters)
        .options(
            selectinload(User.profile),
            selectinload(User.employee_profile),
        )
    )

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


async def create_user(db: AsyncSession, data: UserCreateRequest) -> User:
    check = await db.execute(select(User).where(User.phone == data.phone))
    if check.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone already registered",
        )

    new_user = User(
        full_name=data.full_name,
        phone=data.phone,
        password=hash_password(data.password),
        role=data.role,
        is_active=True,
    )
    db.add(new_user)
    await db.flush()

    if data.role == UserRole.USER:
        if data.profile is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="profile is required for USER role",
            )

        db.add(
            UserProfile(
                user_id=new_user.id,
                address=data.profile.address,
                apartment=data.profile.apartment,
                personal_account=data.profile.personal_account,
            )
        )

    elif data.role == UserRole.EMPLOYEE:
        if data.employee_type is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="employee_type is required for EMPLOYEE role",
            )

        db.add(
            EmployeeProfile(
                user_id=new_user.id,
                employee_type=data.employee_type,
            )
        )

    await db.commit()
    return await get_user_by(db, id=new_user.id)


async def update_user(db: AsyncSession, user_id: int, data: UserUpdateRequest) -> User:
    user = await get_user_by(db, id=user_id)

    update_data = data.model_dump(exclude_unset=True)

    password = update_data.pop("password", None)
    role = update_data.pop("role", None)
    employee_type = update_data.pop("employee_type", None)

    if "phone" in update_data and update_data["phone"] != user.phone:
        check = await db.execute(
            select(User).where(User.phone == update_data["phone"], User.id != user.id)
        )
        if check.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone already registered",
            )

    for field in ("full_name", "phone"):
        if field in update_data and update_data[field] is not None:
            setattr(user, field, update_data[field])

    if password:
        user.password = hash_password(password)

    target_role = role or user.role

    profile_fields_present = any(
        update_data.get(field) is not None
        for field in ("address", "apartment", "personal_account")
    )

    if target_role == UserRole.USER:
        if user.employee_profile is not None:
            await db.delete(user.employee_profile)
            user.employee_profile = None

        if user.profile is None:
            if not profile_fields_present:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="address/apartment/personal_account are required for USER role when profile does not exist",
                )
            user.profile = UserProfile(user_id=user.id)

        if "address" in update_data and update_data["address"] is not None:
            user.profile.address = update_data["address"]
        if "apartment" in update_data and update_data["apartment"] is not None:
            user.profile.apartment = update_data["apartment"]
        if "personal_account" in update_data and update_data["personal_account"] is not None:
            user.profile.personal_account = update_data["personal_account"]

    elif target_role == UserRole.EMPLOYEE:
        if profile_fields_present:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User profile fields are not allowed for EMPLOYEE role",
            )

        if user.profile is not None:
            await db.delete(user.profile)
            user.profile = None

        final_employee_type = employee_type or (
            user.employee_profile.employee_type if user.employee_profile else None
        )

        if final_employee_type is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="employee_type is required for EMPLOYEE role",
            )

        if user.employee_profile is None:
            user.employee_profile = EmployeeProfile(
                user_id=user.id,
                employee_type=final_employee_type,
            )
        else:
            user.employee_profile.employee_type = final_employee_type

    elif target_role == UserRole.ADMIN:
        if profile_fields_present or employee_type is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Profiles are not allowed for ADMIN role",
            )

        if user.profile is not None:
            await db.delete(user.profile)
            user.profile = None

        if user.employee_profile is not None:
            await db.delete(user.employee_profile)
            user.employee_profile = None

    if role is not None:
        user.role = role

    await db.commit()
    return await get_user_by(db, id=user.id)


async def activate_deactivate_user(db: AsyncSession, user_id: int) -> UserActive:
    user = await get_user_by(db, id=user_id)
    if user.is_active:
        user.is_active = False
    else:
        user.is_active = True
    await db.commit()
    return UserActive.model_validate(user)