from typing import List, Optional
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, Order, Conversation
from .config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def init_db() -> None:
    """Initialize database and create all tables"""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

def check_db_health() -> bool:
    """Check if database connection is healthy"""
    try:
        with SessionLocal() as s:
            s.execute(select(1))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False

# ---- Init & Seed (with retry so we wait for MySQL to be ready) ---------------
def init_db(retries: int = 15, delay: float = 2.0) -> None:
    """
    Create tables + seed.
    Waits for DB to be reachable (useful when starting with docker-compose).
    """
    last_err: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            Base.metadata.create_all(engine)
            seed_if_empty()
            log.info("DB ready (attempt %s/%s)", attempt, retries)
            return
        except OperationalError as e:
            last_err = e
            log.warning("DB not ready yet (attempt %s/%s): %s", attempt, retries, e)
            time.sleep(delay)
    raise last_err if last_err else RuntimeError("DB init retry exhausted")


# ---- Seed helpers ------------------------------------------------------------
def _sizes_csv_from_map(size_map: Dict[int, int]) -> str:
    return ",".join(str(s) for s in sorted(size_map.keys()))


def _stock_total_from_map(size_map: Dict[int, int]) -> int:
    return sum(max(0, int(v)) for v in size_map.values())


# ---- Seed data (explicit per-size stock) -------------------------------------
def seed_if_empty() -> None:
    """Seed catalog with explicit per-size stock on first run."""
    with SessionLocal() as s:
        has_products = s.scalar(select(Product.product_id).limit(1)) is not None
        if not has_products:
            items: List[Tuple[str, str, str, str, float, Dict[int, int]]] = [
                (
                    "Air Max 90",
                    "Nike",
                    "running",
                    "Classic running sneakers with visible Air unit.",
                    120.0,
                    {38: 2, 39: 3, 40: 4, 41: 5, 42: 5, 43: 3, 44: 2},
                ),
                (
                    "Ultraboost 22",
                    "Adidas",
                    "running",
                    "High-comfort running shoes with Boost midsole.",
                    180.0,
                    {39: 3, 40: 4, 41: 4, 42: 4, 43: 3},
                ),
                (
                    "Chuck Taylor All Star",
                    "Converse",
                    "casual",
                    "Iconic canvas sneakers with rubber toe cap.",
                    65.0,
                    {36: 2, 37: 3, 38: 4, 39: 4, 40: 5, 41: 4, 42: 4, 43: 2, 44: 2},
                ),
                (
                    "Vans Old Skool",
                    "Vans",
                    "skate",
                    "Signature side stripe, suede/canvas build.",
                    70.0,
                    {38: 3, 39: 3, 40: 4, 41: 4, 42: 4, 43: 4},
                ),
                (
                    "Air Jordan 1 Mid",
                    "Nike",
                    "basketball",
                    "Legendary court style with cushioned midsole.",
                    150.0,
                    {40: 2, 41: 3, 42: 3, 43: 3, 44: 3, 45: 1},
                ),
                (
                    "Kyrie Flytrap 6",
                    "Nike",
                    "basketball",
                    "Lightweight support for quick cuts.",
                    110.0,
                    {40: 2, 41: 2, 42: 3, 43: 3, 44: 2},
                ),
                (
                    "NB 990v5",
                    "New Balance",
                    "running",
                    "Stable, premium cushioning for daily miles.",
                    185.0,
                    {39: 1, 40: 2, 41: 2, 42: 2, 43: 2, 44: 1},
                ),
                (
                    "NB 574 Core",
                    "New Balance",
                    "casual",
                    "Everyday classic with ENCAP cushioning.",
                    85.0,
                    {38: 4, 39: 5, 40: 5, 41: 5, 42: 5, 43: 4},
                ),
                (
                    "Gazelle",
                    "Adidas",
                    "casual",
                    "Retro suede classic since the 60s.",
                    95.0,
                    {38: 2, 39: 3, 40: 3, 41: 3, 42: 3, 43: 2},
                ),
                (
                    "Pegasus 40",
                    "Nike",
                    "running",
                    "Versatile daily trainer with responsive ride.",
                    130.0,
                    {39: 3, 40: 4, 41: 4, 42: 4, 43: 3, 44: 2},
                ),
                (
                    "Metcon 9",
                    "Nike",
                    "training",
                    "Stable training shoe for HIIT & lifting.",
                    140.0,
                    {39: 2, 40: 3, 41: 3, 42: 3, 43: 3},
                ),
                (
                    "Nano X3",
                    "Reebok",
                    "training",
                    "All-round training with Lift & Run chassis.",
                    135.0,
                    {39: 2, 40: 2, 41: 3, 42: 3, 43: 2, 44: 1},
                ),
                (
                    "Terrex Swift R3",
                    "Adidas",
                    "hiking",
                    "Grip & protection for fast hiking.",
                    160.0,
                    {40: 2, 41: 2, 42: 2, 43: 2, 44: 1},
                ),
                (
                    "Salomon XA Pro 3D",
                    "Salomon",
                    "hiking",
                    "Durable trail shoe with 3D chassis.",
                    155.0,
                    {40: 2, 41: 2, 42: 2, 43: 1, 44: 1},
                ),
                (
                    "Blazer Mid '77",
                    "Nike",
                    "casual",
                    "Vintage mid-cut with clean leather.",
                    105.0,
                    {38: 2, 39: 3, 40: 3, 41: 3, 42: 3, 43: 3},
                ),
                (
                    "SK8-Hi",
                    "Vans",
                    "skate",
                    "High-top classic with padded collar.",
                    80.0,
                    {38: 3, 39: 3, 40: 3, 41: 3, 42: 3, 43: 2, 44: 2},
                ),
            ]

            for name, brand, cat, desc, price, size_map in items:
                sizes_csv = _sizes_csv_from_map(size_map)
                stock_total = _stock_total_from_map(size_map)
                p = Product(
                    name=name,
                    brand=brand,
                    category=cat,
                    description=desc,
                    price=price,
                    sizes=sizes_csv,
                    stock_total=stock_total,
                )
                s.add(p)
                s.flush()  # get product_id
                for sz, qty in sorted(size_map.items()):
                    s.add(ProductSize(product_id=p.product_id, size=int(sz), stock=int(qty)))
            s.commit()

        has_orders = s.scalar(select(Order.order_id).limit(1)) is not None
        if not has_orders:
            airmax = s.scalar(select(Product).where(Product.name == "Air Max 90"))
            chuck = s.scalar(select(Product).where(Product.name == "Chuck Taylor All Star"))
            ultrab = s.scalar(select(Product).where(Product.name == "Ultraboost 22"))
            s.add_all(
                [
                    Order(user_name="adit", product_id=airmax.product_id, status="processing"),
                    Order(user_name="sela", product_id=ultrab.product_id, status="shipped"),
                    Order(user_name="gilang", product_id=chuck.product_id, status="delivered"),
                ]
            )
            s.commit()


# ---- Conversation history ----------------------------------------------------
def save_message(user: str, role: str, message: str) -> None:
    """Save a conversation message to database"""
    try:
        with SessionLocal() as s:
            s.add(Conversation(user_name=user, role=role, message=message))
            s.commit()
            logger.debug(f"Saved {role} message for user {user}")
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        raise

def get_last_messages(user: str, limit: int = 6) -> List[Conversation]:
    """
    Get last N messages for a user (combined user+assistant messages).
    Default 6 = 3 interactions (Q&A pairs).
    Returns messages in chronological order.
    """
    try:
        with SessionLocal() as s:
            stmt = (
                select(Conversation)
                .where(Conversation.user_name == user)
                .order_by(desc(Conversation.timestamp))
                .limit(limit)
            )
            rows = list(s.scalars(stmt))
            return list(reversed(rows))  # chronological order
    except Exception as e:
        logger.error(f"Failed to get messages for user {user}: {e}")
        return []

def get_latest_order(user: str) -> Optional[Order]:
    """Get the most recent order for a user"""
    try:
        with SessionLocal() as s:
            stmt = (
                select(Order)
                .where(Order.user_name == user)
                .order_by(desc(Order.order_id))
                .limit(1)
            )
            return s.scalars(stmt).first()
    except Exception as e:
        logger.error(f"Failed to get latest order for user {user}: {e}")
        return None

def get_order_by_id(order_id: int) -> Optional[Order]:
    """Get a specific order by ID"""
    try:
        with SessionLocal() as s:
            stmt = select(Order).where(Order.order_id == order_id).limit(1)
            return s.scalars(stmt).first()
    except Exception as e:
        logger.error(f"Failed to get order {order_id}: {e}")
        return None

def get_product_by_name(name: str) -> Optional[Product]:
    """Get a product by name (case-insensitive)"""
    try:
        with SessionLocal() as s:
            stmt = select(Product).where(Product.name.ilike(f"%{name}%")).limit(1)
            return s.scalars(stmt).first()
    except Exception as e:
        logger.error(f"Failed to get product {name}: {e}")
        return None

# ---- Catalog queries (RAG) ---------------------------------------------------
def list_products() -> List[Product]:
    """Get all products ordered by ID"""
    try:
        with SessionLocal() as s:
            return list(s.scalars(select(Product).order_by(Product.product_id)))
    except Exception as e:
        logger.error(f"Failed to list products: {e}")
        return []
