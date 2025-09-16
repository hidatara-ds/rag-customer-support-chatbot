from typing import List, Optional, Tuple, Dict
from sqlalchemy import create_engine, select, desc, or_
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
        return list(reversed(rows))

# -------- Catalog (RAG) ----------
def list_categories() -> List[str]:
    with SessionLocal() as s:
        return list(s.scalars(select(Product.category).distinct().order_by(Product.category)))

def list_price_list(cat: Optional[str] = None) -> List[Tuple[str, float]]:
    with SessionLocal() as s:
        stmt = select(Product.name, Product.price)
        if cat: stmt = stmt.where(Product.category.ilike(cat))
        stmt = stmt.order_by(Product.price, Product.name)
        return list(s.execute(stmt).all())

def get_product_by_name(name: Optional[str]) -> Optional[Product]:
    if not name: return None
    with SessionLocal() as s:
        return s.scalars(select(Product).where(Product.name.ilike(name)).limit(1)).first()

def search_products_fuzzy(q: str) -> List[Product]:
    pattern = f"%{q}%"
    with SessionLocal() as s:
        stmt = select(Product).where(or_(
            Product.name.ilike(pattern), Product.brand.ilike(pattern), Product.category.ilike(pattern)
        )).order_by(Product.price)
        return list(s.scalars(stmt))

def list_products_by_category(cat: str) -> List[Product]:
    with SessionLocal() as s:
        return list(s.scalars(select(Product).where(Product.category.ilike(cat)).order_by(Product.price)))

def list_products_by_brand(brand: str) -> List[Product]:
    with SessionLocal() as s:
        return list(s.scalars(select(Product).where(Product.brand.ilike(brand)).order_by(Product.price)))

def list_by_category_and_size(cat: str, size: int) -> List[Product]:
    with SessionLocal() as s:
        rows = s.execute(
            select(Product)
            .join(ProductSize, Product.product_id==ProductSize.product_id)
            .where(Product.category.ilike(cat), ProductSize.size==size, ProductSize.stock>0)
            .order_by(Product.price)
        ).scalars()
        return list(rows)

def list_by_size(size: int) -> List[Product]:
    with SessionLocal() as s:
        rows = s.execute(
            select(Product)
            .join(ProductSize, Product.product_id==ProductSize.product_id)
            .where(ProductSize.size==size, ProductSize.stock>0)
            .order_by(Product.price)
        ).scalars()
        return list(rows)

def get_stock_for_product_size(p: Product, size: int) -> int:
    with SessionLocal() as s:
        val = s.scalar(select(ProductSize.stock).where(ProductSize.product_id==p.product_id, ProductSize.size==size))
        return int(val or 0)

def list_other_products(exclude_name: str, limit: int = 5, same_category_first: bool = True) -> List[str]:
    with SessionLocal() as s:
        base_cat = None
        if same_category_first and exclude_name:
            base_cat = s.scalar(select(Product.category).where(Product.name.ilike(exclude_name)).limit(1))
        names: List[str] = []
        if base_cat:
            names.extend(list(s.scalars(
                select(Product.name)
                .where(Product.category == base_cat, Product.name != exclude_name)
                .order_by(Product.price).limit(limit)
            )))
        if len(names) < limit:
            names.extend(list(s.scalars(
                select(Product.name)
                .where(Product.name != exclude_name)
                .order_by(Product.price).limit(limit - len(names))
            )))
        return names
