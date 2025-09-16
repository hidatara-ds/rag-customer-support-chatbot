from typing import List, Optional
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, Order, Conversation
from .config import DATABASE_URL, MAX_HISTORY_MESSAGES

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    Base.metadata.create_all(engine)
    seed_if_empty()

def seed_if_empty() -> None:
    from sqlalchemy import select
    with SessionLocal() as s:
        has_products = s.scalar(select(Product.product_id).limit(1)) is not None
        if not has_products:
            s.add_all([
                Product(
                    name="Air Max 90",
                    description="Classic running sneakers with visible Air cushioning and durable leather/mesh upper.",
                    price=120.00
                ),
                Product(
                    name="Ultraboost 22",
                    description="High-comfort running shoes with responsive Boost midsole and Primeknit upper.",
                    price=180.00
                ),
                Product(
                    name="Chuck Taylor All Star",
                    description="Iconic canvas sneakers with rubber toe cap and timeless street style.",
                    price=65.00
                ),
                Product(
                    name="Vans Old Skool",
                    description="Skate-inspired shoes with signature side stripe and sturdy suede/canvas build.",
                    price=70.00
                ),
            ])
            s.commit()
        has_orders = s.scalar(select(Order.order_id).limit(1)) is not None
        if not has_orders:
            airmax   = s.scalar(select(Product).where(Product.name=="Air Max 90"))
            ultra    = s.scalar(select(Product).where(Product.name=="Ultraboost 22"))
            chuck    = s.scalar(select(Product).where(Product.name=="Chuck Taylor All Star"))
            vans     = s.scalar(select(Product).where(Product.name=="Vans Old Skool"))
            s.add_all([
                Order(user_name="gilang", product_id=airmax.product_id, status="processing"),
                Order(user_name="sela",   product_id=ultra.product_id,  status="shipped"),
                Order(user_name="gilang", product_id=chuck.product_id,  status="delivered"),
                Order(user_name="ayu",    product_id=vans.product_id,   status="pending"),
            ])
            s.commit()

def save_message(user: str, role: str, message: str) -> None:
    with SessionLocal() as s:
        s.add(Conversation(user_name=user, role=role, message=message))
        s.commit()

def get_last_messages(user: str, limit: Optional[int] = None) -> List[Conversation]:
    """
    Ambil pesan terakhir user untuk konteks LLM.
    - Jika limit=None -> gunakan MAX_HISTORY_MESSAGES dari env.
    - Penyimpanan di DB sendiri unlimited.
    """
    lim = limit or MAX_HISTORY_MESSAGES
    with SessionLocal() as s:
        stmt = (
            select(Conversation)
            .where(Conversation.user_name == user)
            .order_by(desc(Conversation.timestamp))
            .limit(lim)
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
