CREATE DATABASE IF NOT EXISTS shoe_support CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shoe_support;

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
  role VARCHAR(20),
  message TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO products (name, description, price) VALUES
('Air Max 90', 'Classic running sneakers with visible Air cushioning and durable leather/mesh upper.', 120.00),
('Ultraboost 22', 'High-comfort running shoes with responsive Boost midsole and Primeknit upper.', 180.00),
('Chuck Taylor All Star', 'Iconic canvas sneakers with rubber toe cap and timeless street style.', 65.00),
('Vans Old Skool', 'Skate-inspired shoes with signature side stripe and sturdy suede/canvas build.', 70.00)
ON DUPLICATE KEY UPDATE name=VALUES(name);

INSERT INTO orders (user_name, product_id, status) VALUES
('gilang', (SELECT product_id FROM products WHERE name='Air Max 90'), 'processing'),
('sela',   (SELECT product_id FROM products WHERE name='Ultraboost 22'), 'shipped'),
('gilang', (SELECT product_id FROM products WHERE name='Chuck Taylor All Star'), 'delivered'),
('ayu',    (SELECT product_id FROM products WHERE name='Vans Old Skool'), 'pending');
