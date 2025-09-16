CREATE DATABASE IF NOT EXISTS shoe_support CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shoe_support;

DROP TABLE IF EXISTS product_sizes;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS conversations;
DROP TABLE IF EXISTS products;

CREATE TABLE products (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) UNIQUE,
  brand VARCHAR(60),
  category VARCHAR(60),
  description TEXT,
  price DECIMAL(10,2),
  sizes TEXT,
  stock_total INT
);

CREATE TABLE product_sizes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  size INT NOT NULL,
  stock INT NOT NULL,
  CONSTRAINT uq_product_size UNIQUE (product_id, size),
  CONSTRAINT fk_ps_product FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

CREATE TABLE orders (
  order_id INT AUTO_INCREMENT PRIMARY KEY,
  user_name VARCHAR(100),
  product_id INT,
  status VARCHAR(50),
  CONSTRAINT fk_orders_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE conversations (
  convo_id INT AUTO_INCREMENT PRIMARY KEY,
  user_name VARCHAR(100),
  role VARCHAR(20),
  message TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Seed minimal (tanpa per-size explicit karena di app akan generate otomatis juga untuk SQLite).
INSERT INTO products (name,brand,category,description,price,sizes,stock_total) VALUES
('Air Max 90','Nike','running','Classic running sneakers with visible Air unit.',120.00,'38,39,40,41,42,43,44',24),
('Ultraboost 22','Adidas','running','High-comfort running shoes with Boost midsole.',180.00,'39,40,41,42,43',18),
('Chuck Taylor All Star','Converse','casual','Iconic canvas sneakers with rubber toe cap.',65.00,'36,37,38,39,40,41,42,43,44',30),
('Vans Old Skool','Vans','skate','Signature side stripe, suede/canvas build.',70.00,'38,39,40,41,42,43',22),
('Air Jordan 1 Mid','Nike','basketball','Legendary court style with cushioned midsole.',150.00,'40,41,42,43,44,45',15),
('Kyrie Flytrap 6','Nike','basketball','Lightweight support for quick cuts.',110.00,'40,41,42,43,44',12),
('NB 990v5','New Balance','running','Stable, premium cushioning for daily miles.',185.00,'39,40,41,42,43,44',10),
('NB 574 Core','New Balance','casual','Everyday classic with ENCAP cushioning.',85.00,'38,39,40,41,42,43',28),
('Gazelle','Adidas','casual','Retro suede classic since the 60s.',95.00,'38,39,40,41,42,43',16),
('Pegasus 40','Nike','running','Versatile daily trainer with responsive ride.',130.00,'39,40,41,42,43,44',20),
('Metcon 9','Nike','training','Stable training shoe for HIIT & lifting.',140.00,'39,40,41,42,43',14),
('Nano X3','Reebok','training','All-round training with Lift & Run chassis.',135.00,'39,40,41,42,43,44',13),
('Terrex Swift R3','Adidas','hiking','Grip & protection for fast hiking.',160.00,'40,41,42,43,44',9),
('Salomon XA Pro 3D','Salomon','hiking','Durable trail shoe with 3D chassis.',155.00,'40,41,42,43,44',8),
('Blazer Mid ''77','Nike','casual','Vintage mid-cut with clean leather.',105.00,'38,39,40,41,42,43',17),
('SK8-Hi','Vans','skate','High-top classic with padded collar.',80.00,'38,39,40,41,42,43,44',19);

-- contoh per-size manual untuk salah satu produk (lainnya bisa diisi via aplikasi / script)
INSERT INTO product_sizes (product_id,size,stock)
SELECT product_id, size, 2 FROM products, JSON_TABLE(CONCAT('[', REPLACE(sizes, ',', '],['), ']'),
'$[*]' COLUMNS (size INT PATH '$')) j WHERE name='Ultraboost 22';
