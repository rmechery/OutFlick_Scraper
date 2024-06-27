import json
from pathlib import Path
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from src.models.productsql import ProductSQL, ProductColorSQL, ProductImageSQL, ProductSizeSQL

from typing import List, Optional
from pydantic import BaseModel, Json
from pydantic.dataclasses import Literal

from utils.db_utils import SessionRemote

Extension = Literal['json', 'csv']

import src.Stores as Parsers

class Product(BaseModel):
    product_name: str
    brand: str
    category: str
    gender: Literal["M", "F", "U"]
    price: float
    on_sale: bool
    sizes_raw: List[str]
    store_product_id: str
    main_image_url: str
    product_url: str
    colors_raw: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    images_raw: Optional[List[str]] = []
    extra: Optional[Json] = None

class Store(object):
    def __init__(self, brand: str):
        self.raw_data = None
        self.brand: str = brand
        self.sqlproducts: List[ProductSQL] = []
        self.products: List[Product] = []

    def get_data(self, local_data=False):
        raise NotImplemented("Hello")

    def add_product(self, product: Product):
        product.brand = self.brand

        prod_dump = product.model_dump(exclude_unset=True)
        del prod_dump['sizes_raw']
        del prod_dump['colors_raw']
        del prod_dump['images_raw']

        product_model: ProductSQL = ProductSQL(**prod_dump)
        product_model.images = [ProductImageSQL(image_url=url) for url in product.images_raw]
        product_model.colors = [ProductColorSQL(color=col) for col in product.colors_raw]
        product_model.sizes = [ProductSizeSQL(size=size) for size in product.sizes_raw]

        #self.products.append(product)
        self.sqlproducts.append(product_model)

    def parse_file(self) -> None:
        pass

    def print_products(self) -> None:
        for product in self.products:
            print(product)

    def commit_products(self) -> None:
            for product in self.products:
                self.add_product(product)

            unique_prods = 0
            for product in self.sqlproducts:
                session = SessionRemote()
                session.begin()
                try:
                    session.add(product)
                    session.commit()
                    unique_prods += 1
                except IntegrityError:
                    session.rollback()
                    # Query for the existing item that caused the unique constraint violation
                    existing_item : ProductSQL = session.query(ProductSQL).filter_by(store_product_id=product.store_product_id).one()

                    # Compare time_scraped and update if the new item is more recent
                    #if product.time_scraped is not None and product.time_scraped > existing_item.time_scraped:
                    existing_item.data = product
                    #existing_item.time_scraped = datetime.now()
                    session.commit()
                finally:
                    session.close()
            print(f"Unique products committed: {unique_prods}")
    def save_file(self, data: any, extension: Extension, alias: Optional[str] = ""):
        date = datetime.now()
        date_dir = date.strftime("data/%Y/%m")
        new_dir = Path(__file__).parent.parent / self.brand / date_dir

        new_dir.mkdir(parents=True, exist_ok=True)

        new_file = new_dir / date.strftime(f"%H-%M-%S_%Y_%m_%d{alias}.{extension}")

        with new_file.open("w", encoding ="utf-8") as f:
            f.write(data)

    def save_raw_json(self):
        products_json = [product.model_dump(exclude_unset=True) for product in self.products]
        json_str = json.dumps(products_json, indent=2)

        self.save_file(json_str, "json", alias="_raw")

    def save_json(self):
        products_json = [product.model_dump(exclude_unset=True) for product in self.products]
        json_str = json.dumps(products_json, indent=2)
        self.save_file(json_str, "json", alias="_parse")

    def load_raw_data(self, json_str: str) -> None:
        products_json = json.loads(json_str)
        print(products_json)
        self.raw_data = products_json

    def load_data(self, json_str: str) -> None:
        products_json = json.loads(json_str)
        for p in products_json:
            print(p)
            self.products.append(Product(**p))


    def get_json(self):
        products_json = [product.model_dump(exclude_unset=True) for product in self.products]
        return json.dumps(products_json, indent=2)
