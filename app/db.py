from typing import List, Optional, Tuple, Dict
from sqlalchemy import create_engine, select, desc, or_
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, ProductSize, Order, Conversation
from .config import DATABASE_URL, MAX_HISTORY_MESSAGES

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    Base.metadata.create_all(engine)
    seed_if_empty()

# ---------- helpers ----------
def _sizes_csv_from_map(size_map: Dict[int, int]) -> str:
    return ",".join(str(s) for s in sorted(size_map.keys()))

def _stock_total_from_map(size_map: Dict[int, int]) -> int:
    return sum(max(0, int(v)) for v in size_map.values())

# =============== SEED PER-UKURAN (EXPLICIT) ===============
def seed_if_empty() -> None:
    """Seed dengan stok per-ukuran eksplisit untuk setiap produk."""
    with SessionLocal() as s:
        has_products = s.scalar(select(Product.product_id).limit(1)) is not None
        if not has_products:
            # name, brand, category, description, price, size_stock{size:qty}
            items = [
                ("Air Max 90","Nike","running","Classic running sneakers with visible Air unit.",120.0,
                 {38:2, 39:3, 40:4, 41:5, 42:5, 43:3, 44:2}),
                ("Ultraboost 22","Adidas","running","High-comfort running shoes with Boost midsole.",180.0,
                 {39:3, 40:4, 41:4, 42:4, 43:3}),
                ("Chuck Taylor All Star","Converse","casual","Iconic canvas sneakers with rubber toe cap.",65.0,
                 {36:2, 37:3, 38:4, 39:4, 40:5, 41:4, 42:4, 43:2, 44:2}),
                ("Vans Old Skool","Vans","skate","Signature side stripe, suede/canvas build.",70.0,
                 {38:3, 39:3, 40:4, 41:4, 42:4, 43:4}),
                ("Air Jordan 1 Mid","Nike","basketball","Legendary court style with cushioned midsole.",150.0,
                 {40:2, 41:3, 42:3, 43:3, 44:3, 45:1}),
                ("Kyrie Flytrap 6","Nike","basketball","Lightweight support for quick cuts.",110.0,
                 {40:2, 41:2, 42:3, 43:3, 44:2}),
                ("NB 990v5","New Balance","running","Stable, premium cushioning for daily miles.",185.0,
                 {39:1, 40:2, 41:2, 42:2, 43:2, 44:1}),
                ("NB 574 Core","New Balance","casual","Everyday classic with ENCAP cushioning.",85.0,
                 {38:4, 39:5, 40:5, 41:5, 42:5, 43:4}),
                ("Gazelle","Adidas","casual","Retro suede classic since the 60s.",95.0,
                 {38:2, 39:3, 40:3, 41:3, 42:3, 43:2}),
                ("Pegasus 40","Nike","running","Versatile daily trainer with responsive ride.",130.0,
                 {39:3, 40:4, 41:4, 42:4, 43:3, 44:2}),
                ("Metcon 9","Nike","training","Stable training shoe for HIIT & lifting.",140.0,
                 {39:2, 40:3, 41:3, 42:3, 43:3}),
                ("Nano X3","Reebok","training","All-round training with Lift & Run chassis.",135.0,
                 {39:2, 40:2, 41:3, 42:3, 43:2, 44:1}),
                ("Terrex Swift R3","Adidas","hiking","Grip & protection for fast hiking.",160.0,
                 {40:2, 41:2, 42:2, 43:2, 44:1}),
                ("Salomon XA Pro 3D","Salomon","hiking","Durable trail shoe with 3D chassis.",155.0,
                 {40:2, 41:2, 42:2, 43:1, 44:1}),
                ("Blazer Mid '77","Nike","casual","Vintage mid-cut with clean leather.",105.0,
                 {38:2, 39:3, 40:3, 41:3, 42:3, 43:3}),
                ("SK8-Hi","Vans","skate","High-top classic with padded collar.",80.0,
                 {38:3, 39:3, 40:3, 41:3, 42:3, 43:2, 44:2}),
            ]
            for name, brand, cat, desc, price, size_map in items:
                sizes_csv = _sizes_csv_from_map(size_map)
                stock_total = _stock_total_from_map(size_map)
                p = Product(
                    name=name, brand=brand, category=cat, description=desc,
                    price=price, sizes=sizes_csv, stock_total=stock_total
                )
                s.add(p); s.flush()  # dapat product_id
                for sz, qty in sorted(size_map.items()):
                    s.add(ProductSize(product_id=p.product_id, size=int(sz), stock=int(qty)))
            s.commit()

        has_orders = s.scalar(select(Order.order_id).limit(1)) is not None
        if not has_orders:
            airmax = s.scalar(select(Product).where(Product.name=="Air Max 90"))
            chuck  = s.scalar(select(Product).where(Product.name=="Chuck Taylor All Star"))
            ultrab = s.scalar(select(Product).where(Product.name=="Ultraboost 22"))
            s.add_all([
                Order(user_name="gilang", product_id=airmax.product_id, status="processing"),
                Order(user_name="sela",   product_id=ultrab.product_id, status="shipped"),
                Order(user_name="gilang", product_id=chuck.product_id,  status="delivered"),
            ])
            s.commit()

def save_message(user: str, role: str, message: str) -> None:
    with SessionLocal() as s:
        s.add(Conversation(user_name=user, role=role, message=message))
        s.commit()

def get_last_messages(user: str, limit: Optional[int] = None) -> List[Conversation]:
    lim = limit or MAX_HISTORY_MESSAGES
    with SessionLocal() as s:
        stmt = (select(Conversation)
                .where(Conversation.user_name == user)
                .order_by(desc(Conversation.timestamp))
                .limit(lim))
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
