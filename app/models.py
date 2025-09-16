from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Text, ForeignKey, DateTime, func, UniqueConstraint

class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = "products"
    product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str]       = mapped_column(String(100), index=True, unique=True)
    brand: Mapped[str]      = mapped_column(String(60), index=True)
    category: Mapped[str]   = mapped_column(String(60), index=True)   # running, casual, basketball, skate, hiking, training
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float]    = mapped_column(Float)
    sizes: Mapped[str]      = mapped_column(Text)   # CSV: "38,39,40,..."
    stock_total: Mapped[int] = mapped_column(Integer)  # total stok semua ukuran
    sizes_detail: Mapped[list["ProductSize"]] = relationship(back_populates="product", cascade="all, delete-orphan")

class ProductSize(Base):
    __tablename__ = "product_sizes"
    __table_args__ = (UniqueConstraint("product_id","size", name="uq_product_size"),)
    id: Mapped[int]        = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int]= mapped_column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), index=True)
    size: Mapped[int]      = mapped_column(Integer, index=True)  # EU size (36..47 etc.)
    stock: Mapped[int]     = mapped_column(Integer)
    product: Mapped["Product"] = relationship(back_populates="sizes_detail")

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
