from pathlib import Path

from src.Stores.Uniqlo.uniqlo import Uniqlo
# from src.Stores.Zara.zara2 import Zara
from src.models.store import Store


def get_store_obj(brand: str) -> Store:
    """Gets the Parser's class from brand name if file location is setup correctly."""
    store_dir = Path(__file__).parent.parent / 'src' / 'Stores'
    stores = [item.name for item in store_dir.iterdir() if item.is_dir()]
    if brand not in stores:
        raise Exception(f'Brand {brand} does not exist. Please add this store\'s parser to the src/Stores folder.')
    store_obj: Store = globals()[brand]()
    return store_obj


def main():
    print(get_store_obj('Uniqlo'))


if __name__ == '__main__':
    main()
