from typing import List, Optional
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, Order, Conversation
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    Base.metadata.create_all(engine)

def save_message(user: str, role: str, message: str) -> None:
    with SessionLocal() as s:
        s.add(Conversation(user_name=user, role=role, message=message))
        s.commit()

def get_last_messages(user: str, limit: int = 6) -> List[Conversation]:
    """Ambil N pesan terakhir untuk user (gabungan user+assistant). Default 6 = 3 interaksi."""
    with SessionLocal() as s:
        stmt = (
            select(Conversation)
            .where(Conversation.user_name == user)
            .order_by(desc(Conversation.timestamp))
            .limit(limit)
        )
        rows = list(s.scalars(stmt))
        return list(reversed(rows))  # kronologis

def get_latest_order(user: str) -> Optional[Order]:
    with SessionLocal() as s:
        stmt = (
            select(Order)
            .where(Order.user_name == user)
            .order_by(desc(Order.order_id))
            .limit(1)
        )
        return s.scalars(stmt).first()

def get_order_by_id(order_id: int) -> Optional[Order]:
    with SessionLocal() as s:
        stmt = select(Order).where(Order.order_id == order_id).limit(1)
        return s.scalars(stmt).first()

def get_product_by_name(name: str) -> Optional[Product]:
    with SessionLocal() as s:
        stmt = select(Product).where(Product.name.ilike(name)).limit(1)
        return s.scalars(stmt).first()

def list_products() -> List[Product]:
    with SessionLocal() as s:
        return list(s.scalars(select(Product).order_by(Product.product_id)))
