import asyncio
import logging
import time
from parser.enums import Stores
from parser.sbermarket_store_parser import SbermarketStoreParser

from db.queries.orm import AsyncORM

logging.basicConfig(level=logging.INFO)

async def main():
    await AsyncORM.create_tables()
    for store in Stores:
        store_parser = await SbermarketStoreParser().create(store=store)
        result = await store_parser.run()


if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    logging.info(f"The running time of the parsing was {(time.time() - start_time):.2f} sec.")
