import uuid
from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()

user_tracked_products_table = Table(
    "user_tracked_products",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id")),
    Column("product_id", UUID(as_uuid=True), ForeignKey("products.id")),
)


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    name = Column(String)
    products = relationship(
        "Product", secondary=user_tracked_products_table, back_populates="users"
    )

    def __repr__(self):
        return f"<User(name='{self.name}')"


class Product(Base):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    name = Column(String)
    url = Column(String, nullable=False)
    users = relationship(
        "User", secondary=user_tracked_products_table, back_populates="products"
    )
    prices = relationship("Price", cascade="all, delete")

    def __repr__(self):
        return f"<Product(name='{self.name}', url='{self.url}')>"


class Price(Base):
    __tablename__ = "prices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    product_id = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id"),
    )
    value = Column(Integer, nullable=False)
    datetime = Column(DateTime(timezone=True), nullable=False, default=datetime.now())

    def __repr__(self):
        return f"<Price(product_id='{self.product_id}', value='{self.value}' , datetime='{self.datetime}')>"
