-- ============================================================
--  ShopMind AI — Database Schema + Seed Data
--  Run: mysql -u root -p shopmind_db < database/schema.sql
-- ============================================================

-- 1. Products Table
CREATE TABLE IF NOT EXISTS products (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(150)   NOT NULL,
    category    VARCHAR(80)    NOT NULL,
    price       DECIMAL(10,2)  NOT NULL,
    rating      DECIMAL(3,2)   DEFAULT 0.0,
    stock       INT            DEFAULT 0,
    image_url   VARCHAR(255),
    created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- 2. Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id     INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)   NOT NULL,
    email       VARCHAR(150)   UNIQUE NOT NULL,
    phone       VARCHAR(15),
    created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- 3. Orders Table
CREATE TABLE IF NOT EXISTS orders (
    order_id        INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT            NOT NULL,
    product_id      INT            NOT NULL,
    status          ENUM('placed','confirmed','shipped','delivered','cancelled','returned')
                    DEFAULT 'placed',
    delivery_date   DATE,
    created_at      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- 4. FAQs Table
CREATE TABLE IF NOT EXISTS faqs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    question    TEXT           NOT NULL,
    answer      TEXT           NOT NULL,
    category    VARCHAR(80),
    created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- 5. Chat Logs Table (for analytics)
CREATE TABLE IF NOT EXISTS chat_logs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_query  TEXT           NOT NULL,
    intent      VARCHAR(80),
    confidence  DECIMAL(5,2),
    response    TEXT,
    created_at  TIMESTAMP      DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
--  SEED DATA
-- ============================================================

-- Products
INSERT INTO products (name, category, price, rating, stock) VALUES
('Nike Air Max 270',        'shoes',       1899.00, 4.7, 50),
('Puma Softride Enzo',      'shoes',       1499.00, 4.5, 40),
('Skechers Go Walk 6',      'shoes',       1750.00, 4.4, 30),
('Boat Rockerz 550',        'headphones',  1299.00, 4.6, 60),
('Sony WH-CH720N',          'headphones',  7990.00, 4.8, 20),
('JBL Tune 510BT',          'headphones',  1899.00, 4.5, 35),
("Levi's 511 Jeans",        'clothing',    1699.00, 4.6, 45),
('H&M Oversized Tee',       'clothing',     699.00, 4.3, 80),
('Samsung Galaxy Buds2',    'headphones',  3499.00, 4.7, 25),
('Adidas Ultraboost 22',    'shoes',       4999.00, 4.9, 15);

-- Users
INSERT INTO users (name, email, phone) VALUES
('Jenny Sharma',  'jenny@example.com',  '9876543210'),
('Rahul Verma',   'rahul@example.com',  '9123456789'),
('Priya Singh',   'priya@example.com',  '9988776655');

-- Orders
INSERT INTO orders (user_id, product_id, status, delivery_date) VALUES
(1, 1,  'shipped',   '2026-03-27'),
(1, 4,  'delivered', '2026-03-22'),
(2, 7,  'shipped',   '2026-03-29'),
(3, 5,  'placed',    '2026-04-01'),
(2, 2,  'delivered', '2026-03-20');

-- FAQs
INSERT INTO faqs (question, answer, category) VALUES
('What is the return policy?',            'You can return products within 7 days of delivery for a full refund.', 'returns'),
('How long does delivery take?',           'Standard delivery takes 3-5 business days. Express delivery 1-2 days.', 'shipping'),
('Are payments secure?',                  'Yes. All transactions are protected by 256-bit SSL encryption.', 'payments'),
('Can I cancel my order?',                'Orders can be cancelled within 24 hours of placement.', 'orders'),
('How do I track my order?',              'Type "Track order #ID" in the chat to get live order status.', 'tracking'),
('What payment methods are accepted?',    'We accept UPI, credit/debit cards, net banking, and COD.', 'payments'),
('Is Cash on Delivery available?',        'Yes, COD is available for orders under ₹5000.', 'payments'),
('How do I contact support?',             'Chat with ShopMind AI 24/7 or email support@shopmind.in.', 'support');
