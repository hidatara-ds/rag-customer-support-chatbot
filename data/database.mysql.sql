-- Create database
CREATE DATABASE IF NOT EXISTS coffee_support CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE coffee_support;

-- Tables
CREATE TABLE IF NOT EXISTS products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  description TEXT,
  price DECIMAL(10,2)
);

CREATE TABLE IF NOT EXISTS orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  user_name VARCHAR(100),
  product_id INT,
  status VARCHAR(50),
  CONSTRAINT fk_orders_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS conversations (
  convo_id INT AUTO_INCREMENT PRIMARY KEY,
  user_name VARCHAR(100),
  role VARCHAR(20), -- 'user' or 'assistant'
  message TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dummy coffee products
INSERT INTO products (name, description, price) VALUES
('Espresso', 'Strong and rich coffee shot', 2.50),
('Latte', 'Espresso with steamed milk and light foam', 3.50),
('Cold Brew', 'Smooth cold brewed coffee, less acidic', 3.00)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Dummy orders
INSERT INTO orders (user_name, product_id, status) VALUES
('alice', 1, 'shipped'),
('bob',   2, 'delivered'),
('alice', 3, 'pending');

def seed_if_empty() -> None:
    from sqlalchemy import select
    with SessionLocal() as s:
        has_products = s.scalar(select(Product.product_id).limit(1)) is not None
        if not has_products:
            s.add_all([
                Product(name="Espresso", description="Strong and rich coffee shot", price=2.50),
                Product(name="Latte", description="Espresso with steamed milk and light foam", price=3.50),
                Product(name="Cold Brew", description="Smooth cold brewed coffee, less acidic", price=3.00),
            ])
            s.commit()
        has_orders = s.scalar(select(Order.order_id).limit(1)) is not None
        if not has_orders:
            espresso = s.scalar(select(Product).where(Product.name=="Espresso"))
            latte    = s.scalar(select(Product).where(Product.name=="Latte"))
            coldbrew = s.scalar(select(Product).where(Product.name.ilike("Cold Brew")))
            s.add_all([
                Order(user_name="alice", product_id=espresso.product_id, status="shipped"),
                Order(user_name="bob",   product_id=latte.product_id,    status="delivered"),
                Order(user_name="alice", product_id=coldbrew.product_id, status="pending"),
            ])
            s.commit()

def init_db() -> None:
    Base.metadata.create_all(engine)
    seed_if_empty()
