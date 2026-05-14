import asyncio

from app.database.database import async_session
from app.services.initial_data import create_initial_admin


async def main() -> None:
    async with async_session() as db:
        await create_initial_admin(db)


if __name__ == "__main__":
    asyncio.run(main())