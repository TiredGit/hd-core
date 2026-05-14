import uvicorn
from fastapi import FastAPI
from app.api import main_router
# from contextlib import asynccontextmanager
# from app.database.database import async_engine, async_session
# from app.services.initial_data import create_initial_admin


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # При старте: создаём сессию и инициируем админа
#     async with async_session() as db:
#         await create_initial_admin(db)
#     yield
#     # При остановке: закрываем соединение с БД
#     await async_engine.dispose()


app = FastAPI()
app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)