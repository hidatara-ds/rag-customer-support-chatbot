from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Text, ForeignKey, DateTime, func

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]       = mapped_column(String(100), index=True, unique=True)
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float]    = mapped_column(Float)

class Order(Base):
    __tablename__ = "orders"
    order_id: Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_name: Mapped[str]  = mapped_column(String(100), index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.product_id"))
    status: Mapped[str]     = mapped_column(String(50))
    product: Mapped["Product"] = relationship("Product")

class Conversation(Base):
    __tablename__ = "conversations"
    convo_id: Mapped[int]   = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_name: Mapped[str]  = mapped_column(String(100), index=True)
    role: Mapped[str]       = mapped_column(String(20))  # 'user' | 'assistant'
    message: Mapped[str]    = mapped_column(Text)
    timestamp: Mapped["DateTime"] = mapped_column(DateTime, server_default=func.now(), index=True)
