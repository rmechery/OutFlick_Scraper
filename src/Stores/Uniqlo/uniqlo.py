import json
from operator import itemgetter
from pathlib import Path
from typing import List, Dict, Literal

import requests
from pydantic import Json

from src.models.store import Product, Store
from src.Stores.Uniqlo.uniqlo_pydantic_model import UniqloProduct, ImageMainItem

Extension = Literal['json', 'csv']

def get_local_data() -> Json:
    f = open(Path(__file__).parent / 'downloaded_data' / 'ranked_data.json' )
    data = json.load(f)
    return [(data['result']['items'], '')]


def get_api_data():
    url = "https://www.uniqlo.com/us/api/commerce/v5/en/recommendations/ranked-products"
    payload = ""
    headers = {
        "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
        "Referer": "https://www.uniqlo.com/us/en/spl/ranking/men",
        "DNT": "1",
        "x-fr-clientid": "uq.us.web-spa",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/125.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "\"macOS\""
    }

    script_dir = Path(__file__).parent
    categories_file_path = script_dir / 'downloaded_data' / 'categories.json'
    category_file = open(categories_file_path)
    cats = json.load(category_file)

    data = []

    for gender_query in ["men", "women"]:
        for category_id_query, category in cats[gender_query].items():
            querystring = {
                "schema": "general",
                "genders": gender_query,
                "isDiscount": "false",
                "isAreaAvailable": "false",
                "limit": "62",
                "categoryIds": category_id_query,
                "temperatureSensitive": "false",
                "httpFailure": "true"
            }

            response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
            data.append([response.json()['result']['items'], category])  #response.json()

    return data


def parse_images(imgs: Dict[str, ImageMainItem]) -> List[str]:
    image_urls = []
    for key in imgs:
        image_urls.append(imgs[key].image)
    image_urls = sorted(image_urls, key=itemgetter(0))
    return image_urls


def parse_gender(g: str) -> str:
    if g == 'MEN':
        return 'M'
    elif g == 'WOMEN':
        return 'F'
    return 'U'


def parse_product(product: UniqloProduct, category='') -> Product:
    image_urls = parse_images(product.images.main)

    product_name = product.name
    brand = 'Uniqlo'
    category = category
    gender = parse_gender(product.genderName)
    price = product.prices.promo.value if product.prices.promo is not None else product.prices.base.value
    on_sale = product.prices.promo is not None
    sizes_raw = [s.name for s in product.sizes if s != 'One Size']
    store_product_id = product.productId
    main_image_url = image_urls[0]
    product_url = "https://www.uniqlo.com/us/en/products/" + store_product_id
    colors_raw = [c.name for c in product.colors]
    images_raw = image_urls

    product = Product(product_name=product_name, brand=brand, category=category, gender=gender, price=price,
                      on_sale=on_sale, sizes_raw=sizes_raw, images_raw=images_raw, store_product_id=store_product_id,
                      main_image_url=main_image_url, product_url=product_url, colors_raw=colors_raw)

    return product


class Uniqlo(Store):
    def __init__(self):
        super().__init__(brand='Uniqlo')

    def get_data(self, local_data=False):
        if local_data:
            self.raw_data = get_local_data()
        else:
            self.raw_data = get_api_data()
        return self.raw_data

    def parse_file(self) -> None:
        data = self.raw_data
        if data is None:
            raise FileNotFoundError("Raw data not set")

        unique_ids = []

        for d, cat in data:
            for item in d:
                uniqloProduct = UniqloProduct(**item)
                product = parse_product(uniqloProduct, category=cat)
                if product.store_product_id in unique_ids:
                    continue
                unique_ids.append(product.store_product_id)
                self.products.append(product)


def main():
    uniqlo = Uniqlo()
    uniqlo.get_data(local_data=True)
    uniqlo.parse_file()
    print(uniqlo.get_json())



if __name__ == '__main__':
    main()
