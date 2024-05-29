import asyncio
import logging
import time
from parser.enums import Stores
from parser.sbermarket_store_parser import SbermarketStoreParser

logging.basicConfig(level=logging.INFO)

async def main():
    for idx, store in enumerate(Stores):
        store_parser = await SbermarketStoreParser().create(store=store)
        if idx == 0:
            await store_parser.run(drop_all_tables=True)
        else:
            await store_parser.run(drop_all_tables=False)


if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    logging.info(f"Total running time of the parsing was {(time.time() - start_time):.2f} sec.")
