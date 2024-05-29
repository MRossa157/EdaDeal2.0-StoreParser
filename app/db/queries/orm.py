from typing import List

from db.database import (
    async_engine,
    async_session_factory,
    session_factory,
    sync_engine,
)
from db.models import Base, Category, Product
from sqlalchemy import Integer, and_, cast, func, insert, inspect, select, text


class AsyncORM:
    @staticmethod
    async def create_tables():
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @staticmethod
    async def insert_data(data: Category | Product):
        async with async_session_factory() as session:
            session.add(data)
            await session.flush()
            await session.commit()

    @staticmethod
    async def select_items() -> List[Product]:
        async with async_session_factory() as session:
            query = select(Product)
            result = await session.execute(query)
            items = result.scalars().all()
            return items

    @staticmethod
    async def select_categories() -> List[Category]:
        async with async_session_factory() as session:
            query = select(Category)
            result = await session.execute(query)
            items = result.scalars().all()
            return items