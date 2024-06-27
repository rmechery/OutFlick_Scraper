from sqlalchemy import Uuid, TIMESTAMP, Boolean, Double
from sqlalchemy import ForeignKey, Column
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func

from utils.db_utils import get_remote_engine

# declarative base class
class Base(DeclarativeBase):
    pass

class ProductSQL(Base):
    __tablename__ = "product"

    uid = Column('uid', Uuid, primary_key=True, nullable=False, server_default=func.gen_random_uuid())
    time_scraped = Column('time_scraped', TIMESTAMP, server_default=func.statement_timestamp())
    product_name = Column("product_name", TEXT, nullable=False)
    brand = Column("brand", TEXT, nullable=False)
    gender = Column("gender", TEXT, nullable=False)
    main_image_url = Column("main_image_url", TEXT, nullable=False)
    product_url = Column("product_url", TEXT, nullable=False)
    price = Column("price", Double, nullable=False)
    on_sale = Column("on_sale", Boolean, default=False)
    # average_rating = Column("average_rating", Double, nullable=True)
    # rating_count = Column("rating_count", Integer, nullable=True)
    store_product_id = Column("store_product_id", TEXT, nullable=False, unique=True)
    category = Column("category", TEXT, nullable=True)
    active = Column("active", Boolean, nullable=False, default=True)

    sizes = relationship("ProductSizeSQL", backref="product", cascade='all, delete-orphan')
    images = relationship("ProductImageSQL", backref="product", cascade='all, delete-orphan')
    colors = relationship("ProductColorSQL", backref="product", cascade='all, delete-orphan')

    def __repr__(self) -> str:
        return f"{self.product_name}"

    def to_json(self) -> dict:
        return {
            'uid': self.uid,
            'time_scraped': self.time_scraped,
            'product_name': self.product_name,
            'brand': self.brand,
            'gender': self.gender,
            'main_image_url': self.main_image_url,
            'product_url': self.product_url,
            'price': self.price,
            'on_sale': self.on_sale,
            'average_rating': self.average_rating,
            'rating_count': self.rating_count,
            'store_product_id': self.store_product_id,
            'category': self.category,
            'active': self.active,
        }


class ProductColorSQL(Base):
    __tablename__ = "product_color"

    uid = Column('uid', Uuid, primary_key=True, nullable=False, server_default=func.gen_random_uuid())
    color = Column('color', TEXT, nullable=False)
    product_uid = Column('product_uid', Uuid, ForeignKey("product.uid", onupdate='CASCADE', ondelete='CASCADE'),
                         nullable=False)

    def __repr__(self) -> str:
        return f"ProductColorSQL(uid={self.uid}, color={self.color})"


class ProductImageSQL(Base):
    __tablename__ = "product_image"

    uid = Column('uid', Uuid, primary_key=True, nullable=False, server_default=func.gen_random_uuid())
    image_url = Column('image_url', TEXT, nullable=False)
    product_uid = Column('product_uid', Uuid, ForeignKey("product.uid", onupdate='CASCADE', ondelete='CASCADE'),
                         nullable=False)

    def __repr__(self) -> str:
        return f"ProductImageSQL(uid={self.uid}, image_url={self.image_url})"


class ProductSizeSQL(Base):
    __tablename__ = "product_size"

    uid = Column('uid', Uuid, primary_key=True, nullable=False, server_default=func.gen_random_uuid())
    size = Column('size', TEXT, nullable=False)
    product_uid = Column('product_uid', Uuid, ForeignKey("product.uid", onupdate='CASCADE', ondelete='CASCADE'),
                         nullable=False)

    def __repr__(self) -> str:
        return f"ProductSizeSQL(uid={self.uid}, size={self.size})"


def main():
    Base.metadata.create_all(bind=get_remote_engine())

if __name__ == '__main__':
    main()