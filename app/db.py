from typing import List, Optional
from sqlalchemy import create_engine, select, desc
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, Order, Conversation
from .config import DATABASE_URL
import logging

logger = logging.getLogger(__name__)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
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

def list_products() -> List[Product]:
    """Get all products ordered by ID"""
    try:
        with SessionLocal() as s:
            return list(s.scalars(select(Product).order_by(Product.product_id)))
    except Exception as e:
        logger.error(f"Failed to list products: {e}")
        return []
