from sqlalchemy import Uuid, TIMESTAMP, Boolean, Double
from sqlalchemy import ForeignKey, Column
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

from utils.db_utils import get_remote_engine


# declarative base class
class Base(DeclarativeBase):
    """This Base Class Extends SQLAlchemy's DeclaritiveBase"""
    pass


class ProductSQL(Base):
    """SQLAlchemy `product` object that will go into remote database."""
    __tablename__ = "product"

    uid = Column('uid', Uuid, primary_key=True, nullable=False, server_default=func.gen_random_uuid())
    """Primary key which is a uuid."""
    time_scraped = Column('time_scraped', TIMESTAMP, server_default=func.statement_timestamp())
    product_name = Column("product_name", TEXT, nullable=False)
    brand = Column("brand", TEXT, nullable=False)
    """Company the product was scraped from."""
    gender = Column("gender", TEXT, nullable=False)
    """Can only be 'M', 'F', or 'U' for unisex."""
    main_image_url = Column("main_image_url", TEXT, nullable=False)
    product_url = Column("product_url", TEXT, nullable=False)
    price = Column("price", Double, nullable=False)
    on_sale = Column("on_sale", Boolean, default=False)
    # average_rating = Column("average_rating", Double, nullable=True)
    # rating_count = Column("rating_count", Integer, nullable=True)
    store_product_id = Column("store_product_id", TEXT, nullable=False, unique=True)
    """Product id found on the website."""
    category = Column("category", TEXT, nullable=True)
    """Type of product. Ex. Tops, Bottoms, Skirts."""
    active = Column("active", Boolean, nullable=False, default=True)
    """Boolean that determines if the product still exists or not."""

    sizes = relationship("ProductSizeSQL", backref="product", cascade='all, delete-orphan')
    """One-to-many relation of sizes. Ex. 'S', 'M', 'US-30'."""
    images = relationship("ProductImageSQL", backref="product", cascade='all, delete-orphan')
    """One-to-many relation of image URLs.."""
    colors = relationship("ProductColorSQL", backref="product", cascade='all, delete-orphan')
    """One-to-many relation of image product colors."""

    def __repr__(self) -> str:
        return f"<ProductSQL {self.product_name}>"


class ProductColorSQL(Base):
    """SQLAlchemy `product` color object that will go into remote database"""
    __tablename__ = "product_color"

    uid = Column('uid', Uuid, primary_key=True, nullable=False, server_default=func.gen_random_uuid())
    """Primary key which is a uuid."""
    color = Column('color', TEXT, nullable=False)
    product_uid = Column('product_uid', Uuid, ForeignKey("product.uid", onupdate='CASCADE', ondelete='CASCADE'),
                         nullable=False)
    """Foreign key which refers to the `product`'s primary key."""

    def __repr__(self) -> str:
        return f"ProductColorSQL(uid={self.uid}, color={self.color})"


class ProductImageSQL(Base):
    """SQLAlchemy `product` image url object that will go into remote database"""
    __tablename__ = "product_image"

    uid = Column('uid', Uuid, primary_key=True, nullable=False, server_default=func.gen_random_uuid())
    """Primary key which is a uuid."""
    image_url = Column('image_url', TEXT, nullable=False)
    product_uid = Column('product_uid', Uuid, ForeignKey("product.uid", onupdate='CASCADE', ondelete='CASCADE'),
                         nullable=False)
    """Foreign key which refers to the `product`'s primary key."""

    def __repr__(self) -> str:
        return f"ProductImageSQL(uid={self.uid}, image_url={self.image_url})"


class ProductSizeSQL(Base):
    """SQLAlchemy `product` size object that will go into remote database"""
    __tablename__ = "product_size"

    uid = Column('uid', Uuid, primary_key=True, nullable=False, server_default=func.gen_random_uuid())
    """Primary key which is a uuid."""
    size = Column('size', TEXT, nullable=False)
    product_uid = Column('product_uid', Uuid, ForeignKey("product.uid", onupdate='CASCADE', ondelete='CASCADE'),
                         nullable=False)
    """Foreign key which refers to the `product`'s primary key."""

    def __repr__(self) -> str:
        return f"ProductSizeSQL(uid={self.uid}, size={self.size})"


def main():
    pass


if __name__ == '__main__':
    main()
else:
    Base.metadata.create_all(bind=get_remote_engine())
