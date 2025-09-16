-- Buat database
CREATE DATABASE IF NOT EXISTS coffee_support CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE coffee_support;

-- Tabel
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

-- Produk kopi dummy
INSERT INTO products (name, description, price) VALUES
('Espresso', 'Strong and rich coffee shot', 2.50),
('Latte', 'Espresso with steamed milk and light foam', 3.50),
('Cold Brew', 'Smooth cold brewed coffee, less acidic', 3.00)
ON DUPLICATE KEY UPDATE name=VALUES(name);

-- Pesanan dummy
INSERT INTO orders (user_name, product_id, status) VALUES
('alice', 1, 'shipped'),
('bob',   2, 'delivered'),
('alice', 3, 'pending');
