import json
import logging
import re
from parser.enums import Stores
from typing import Dict, List, Union

import nodriver as uc
from db.models import Category, Product
from db.queries.orm import AsyncORM
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)


class SbermarketStoreParser:
    def __init__(self) -> None:
        self.store: Stores = None
        self.driver: uc.Browser = None
        self.debug_mode: bool = False

        self.store_categories = {}

    @classmethod
    async def create(cls, store: Stores, debug_mode: bool = False):
        self = cls()
        self.driver = await uc.start()
        self.store = store
        self.debug_mode = debug_mode
        return self

    async def run(self, drop_all_tables: bool = True) -> None:
        if drop_all_tables:
            await AsyncORM.create_tables()

        # Initialize categories list for each deep (deep = 0, 1, 2)
        if drop_all_tables:
            self.store_categories[0] = [
                Category(id=0,
                         name='Главная категория',
                         image_url=None,
                         isFinal=False,
                         parent_id=None)]
        else:
            self.store_categories[0] = []
        self.store_categories[1] = []        # for deep=1
        self.store_categories[2] = []        # for deep=2

        base_url = f"https://sbermarket.ru/api/v3/stores/{self.store.value['id']}/departments/"
        all_items = await self.get_all_items(base_url)
        self.driver.stop()

        exists_categories = await AsyncORM.select_categories()
        unique_categories = self.__unique_categories(exists_categories, self.store_categories)

        await self.__categories_to_db(unique_categories)
        await self.__items_to_db(all_items)

        logging.info(
            f'[{self.store.value['slug'].upper()}] {len(all_items)} items was loaded to DB from {self.__count_unique_categories(unique_categories)} unique categories'
            )

        return all_items

    async def get_all_items(self, base_url: str, slug: str='', deep=1) -> List[Dict[str, Union[str, List]]]:
        all_items = []
        page_num = 1

        if deep > 2:
            return all_items

        while True:
            url = base_url + slug + f"?offers_limit=100&per_page=100&page={page_num}"
            # Getting data we want
            page_data = await self.get_json(url)
            department_data = page_data.get('department', None)
            departments_data = page_data.get('departments', None)


            if department_data:
                current_id = department_data['id']
            else:
                current_id = 0      # If current_id not exists, then it's "Главная категории" with id=0

            if departments_data == []:
                logging.info(f'Empty departments in {slug if slug != '' else 'base page'} |\n{url}')
                break

            for child_data in departments_data:
                child_slug = child_data['slug']
                has_child = await self.check_child(base_url=base_url, slug=child_slug)
                if has_child:
                    child_items = await self.get_all_items(base_url, slug=child_slug, deep=deep+1)
                    if child_items != []:
                        self.store_categories[deep].append(Category(id=child_data['id'],
                                                                name=child_data['name'],
                                                                image_url=None,
                                                                isFinal=False,
                                                                parent_id=current_id))
                        all_items.extend(child_items)
                else:
                    self.store_categories[deep].append(Category(id=child_data['id'],
                                                                name=child_data['name'],
                                                                image_url=None,
                                                                isFinal=True,
                                                                parent_id=current_id))
                    all_items.extend(await self.__normalize_special_category_products(child_data))

                if self.debug_mode:
                    break

            page_num += 1

        return all_items

    async def check_child(self, base_url: str, slug: str) -> bool:
        url = base_url + slug
        page_data = await self.get_json(url, new_tab=True)
        if page_data.get('message'):
            if page_data['message'].count('category without children') > 0:
                return False
        return True

    async def get_json(self, url: str, new_tab=False) -> Dict:
        page = await self.driver.get(url, new_tab=new_tab)
        # If there is no delay - does not have time to collect data correctly
        await page.sleep(0.1875)
        page_content = await page.get_content()
        match = re.search(r"<pre>(.*?)</pre>", page_content)
        pre_text = '{}'
        if match:
            pre_text = match.group(1)
        if new_tab:
            await page.close()
        return json.loads(pre_text)

    def __count_unique_categories(self, categories_deep_dict: Dict[int, List[Category]]) -> int:
        return sum(len(categories) for categories in categories_deep_dict.values())


    async def __categories_to_db(self, categories: Dict[int, List[Category]]) -> None:
        #TODO: Добавить tqdm progress bar
        #pbar = tqdm(categories.values(), desc="Loadig categories to DB", total=self.__count_unique_categories(categories))
        for deep_list in categories.values():
            for item in deep_list:
                await AsyncORM.insert_data(item)

    def __unique_categories(self, exists_categories: List[Category], new_categories: Dict[int, List[Category]]) -> Dict[int, List[Category]]:
        new_categories = new_categories.copy()
        for deep_idx, deep_idx_list in new_categories.items():
            unique_category_set = set(exists_categories + deep_idx_list)
            new_categories[deep_idx] = list(unique_category_set)

        return new_categories

    async def __items_to_db(self, items: List[Product]) -> None:
        for item in tqdm(items, desc="Loadig items to DB"):
            await AsyncORM.insert_data(item)

    async def __normalize_special_category_products(self, departament: dict) -> List[Dict[str, Union[str, List]]]:
        category_id = departament['id']

        items = []
        for product in departament['products']:
            item_data = Product(
                name=product.get('name', None),
                image_url=product.get('image_urls', [None])[0],
                category_id=category_id,
                link=product.get('canonical_url', None)
                )
            items.append(item_data)
        return items