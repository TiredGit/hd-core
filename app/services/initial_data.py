from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database.models import User, UserRole
from app.services.jwt_security import hash_password


async def create_initial_admin(db: AsyncSession) -> bool:
    """
    Создаёт первого администратора, если:
    - включён флаг CREATE_INITIAL_ADMIN
    - администратора ещё нет
    - переданы все необходимые данные
    """
    if not settings.admin.CREATE_INITIAL_ADMIN:
        return False

    result = await db.execute(
        select(User).where(User.role == UserRole.ADMIN)
    )
    existing_admin = result.scalars().first()
    if existing_admin:
        return False

    phone = settings.admin.INITIAL_ADMIN_PHONE
    password = settings.admin.INITIAL_ADMIN_PASSWORD
    full_name = settings.admin.INITIAL_ADMIN_NAME

    if not phone or not password or not full_name:
        return False

    admin = User(
        full_name=full_name,
        phone=phone,
        password=hash_password(password),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(admin)
    await db.commit()
    return True