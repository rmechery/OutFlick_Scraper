from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    mapped_column,
    relationship,
    Mapped,
)
from sqlalchemy.orm import DeclarativeBase

from src.models.store import Store
from utils.db_utils import SessionLocal, get_local_engine
from utils.get_parser import get_store_obj

class Base(DeclarativeBase):
    """This Base Class Extends SQLAlchemy's DeclaritiveBase"""
    pass


class Brand(Base):
    """This represents the raw data parsed from a website."""
    __tablename__ = "store"
    """Name of table in SQLite Database"""
    id: Mapped[int] = mapped_column(primary_key=True)
    """Primary Key"""
    brand: Mapped[str] = mapped_column(nullable=False)
    time_created: Mapped[datetime] = mapped_column(default=datetime.now(), nullable=False)
    data: Mapped[Optional[str]]
    """JSON string containing Pydantic validated raw data fetched from website."""
    alias: Mapped[Optional[str]] = mapped_column(unique=True)
    """Unique name for this brand."""
    comments: Mapped[Optional[str]]

    catalogues: Mapped[List["Catalog"]] = relationship(back_populates="store", cascade="all, delete-orphan")
    """One-to-many relationship between store and catalogues."""

    def __init__(self, brand: str, alias: str = None, comments: str = None, data: str = None):
        super().__init__()
        self.brand = brand
        self.alias = alias
        self.comments = comments
        self.data = data

    def __repr__(self) -> str:
        return f"<Brand(brand={self.brand}, time={self.time_created})>"

    def __iter__(self):
        yield str(self.id)
        yield self.brand
        yield str(self.time_created)
        yield self.alias
        yield self.comments


class Catalog(Base):
    __tablename__ = "catalog"
    id: Mapped[int] = mapped_column(primary_key=True)
    """Primary Key"""
    data: Mapped[Optional[str]]
    """JSON string containing Pydantic validated parsed data from `Brand.raw_data`."""
    time_parsed: Mapped[datetime] = mapped_column(default=datetime.now(), nullable=False)
    commited: Mapped[bool] = mapped_column(default=False, nullable=False)
    """Data committed to the Remote database or not."""
    error: Mapped[bool] = mapped_column(default=False, nullable=False)
    """Error parsing data or committing to the Remote database or not."""
    alias: Mapped[Optional[str]] = mapped_column(unique=True)
    """Unique name for parse."""
    comments: Mapped[Optional[str]]
    store_id: Mapped[int] = mapped_column(ForeignKey("store.id"))
    """Foreign key to store."""

    store: Mapped["Brand"] = relationship(back_populates="catalogues")
    """One-to-many relationship between store and catalogues."""

    def __init__(self, store_id: int, alias: str, comments: str, data: str = None, commited: bool = False, error=False):
        super().__init__()
        self.alias = alias
        self.comments = comments
        self.commited = commited
        self.data = data
        self.error = error
        self.store_id = store_id

        self.time_parsed = datetime.now()

    def __repr__(self) -> str:
        return f"<Catalog(brand={self.store.brand}, time={self.time_parsed})>"

    def __iter__(self):
        """Returns iterator that is used to print to the data in the CLI."""
        yield str(self.id)
        yield str(self.store.brand)
        yield str(self.time_parsed)
        yield "" if self.alias is None else self.alias
        yield "" if self.comments is None else self.alias
        yield '✅' if self.commited == 1 else '❌'
        yield '✅' if self.error == 1 else '❌'


def add_store(brand: str, alias: str = None, comments: str = None, data: str = None):
    """Adds store to the local database."""
    with SessionLocal() as session:
        store = Brand(brand, alias, comments, data=data)
        session.add(store)
        session.commit()


def get_all_stores() -> list[list[str | None]]:
    """Returns all stores in the local database."""
    with SessionLocal() as session:
        stores = [list(s) for s in session.query(Brand).all()]
        return stores


def get_all_catalogs() -> list[list[str | None]]:
    """Returns all catalogs in the local database."""
    with SessionLocal() as session:
        catalogs = [list(c) for c in session.query(Catalog).all()]
        return catalogs


def add_catalog(brand_alias: str, alias: str, comments: str = None):
    """Checks if `brand_alias` exists in the Brand table and adds it to the local database."""
    with SessionLocal() as session:
        get_store: Brand | None = session.query(Brand).where(brand_alias == Brand.alias).first()
        if get_store is None:
            raise Exception(f"The alias `{brand_alias}` does not exist in Brand")

        catalog = Catalog(get_store.id, alias, comments)

        store = get_store_obj(get_store.brand)
        store.load_raw_data(get_store.data)
        store.parse_file()

        catalog.data = store.get_json()
        #print(catalog.data)

        session.add(catalog)
        session.commit()


def commit_catalog(alias: str = None):
    """Commits catalog to the remote database."""
    with SessionLocal() as session:
        cur_cat: Catalog | None = session.query(Catalog).where(alias == Catalog.alias).first()
        if cur_cat is None:
            raise Exception(f"Brand {alias} does not exist in store.")

        store = get_store_obj(cur_cat.store.brand)
        store.load_data(cur_cat.data)
        # print(cur_cat.data)
        # store.save_json()
        store.commit_products()

        try:

            cur_cat.error = False
            cur_cat.commited = True
        except Exception as e:
            print(f"Error committing catalog {e}")
            cur_cat.error = True
            cur_cat.commited = False

        session.commit()


def delete_store(alias: str = None):
    """Removes store from the local database."""
    with SessionLocal() as session:
        store: Brand | None = session.query(Brand).where(alias == Brand.alias).first()
        if store is None:
            raise Exception(f"There is no store associated with the alias `{alias}`.")

        session.delete(store)
        session.commit()


def delete_catalog(alias: str = None):
    """Removes catalog from the local database."""
    with SessionLocal() as session:
        cat: Catalog | None = session.query(Catalog).where(alias == Catalog.alias).first()
        if cat is None:
            raise Exception(f"There is no catalog associated with the alias `{alias}`.")

        session.delete(cat)
        session.commit()


def main() -> None:
    pass
    #add_store("Uniqlo", "Uniqlo_24_06_26")
    #delete_store("Uniqlo_24_06_26")
    #add_catalog("Uniqlo")
    # print(get_all_stores())
    # print(get_all_catalogs())
    #commit_catalog("Parse")
    #print(get_store_obj("Uniqlo"))


if __name__ == "__main__":
    #Base.metadata.create_all(bind=get_local_engine())
    main()
