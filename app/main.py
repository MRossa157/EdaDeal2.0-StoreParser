import asyncio
import logging
import time
from parser.enums import Stores
from parser.sbermarket_store_parser import SbermarketStoreParser

from db.queries.orm import AsyncORM

logging.basicConfig(level=logging.INFO)

async def main():
    await AsyncORM.create_tables()

    store_parser = await SbermarketStoreParser().create(store=Stores.AUCHAN)
    result = await store_parser.run()


if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    logging.info(f"Время работы парсинга составило {(time.time() - start_time):.2f} сек.")
