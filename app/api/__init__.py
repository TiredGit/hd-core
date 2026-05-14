from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.admin import router as admin_router
from app.api.users import router as users_router

main_router = APIRouter()
main_router.include_router(auth_router)
main_router.include_router(admin_router)
main_router.include_router(users_router)