
from sqlalchemy import create_engine, Column, Integer, String,Float, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.sql import func

DATABASE_URL = "sqlite:///./ecommerce.db"

engine = create_engine(DATABASE_URL,echo=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# User table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)

    cart_items = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# Product table
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(String(500), default="")
    price = Column(Float, nullable=False)
    stock = Column(Integer, nullable=False, default=0)


# Shopping cart table
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)

    user = relationship("User", back_populates="cart_items")
    product = relationship("Product")


# Order table
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(String(30), default="Placed")
    created_at = Column(DateTime, server_default=func.now())

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


# Order items table
class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column( Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")


# Create all database tables
Base.metadata.create_all(bind=engine)


# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


print("E-Commerce database and tables created successfully!")
