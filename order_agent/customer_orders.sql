CREATE TABLE customers (
    customer_id VARCHAR(50),
    order_id VARCHAR(50),
    product VARCHAR(100),
    status VARCHAR(50),
    shipping_date DATE,
    tracking_number VARCHAR(50),
    amount DECIMAL(10, 2),
    payment_date DATE
);

INSERT INTO customers (customer_id, order_id, product, status, shipping_date, tracking_number, amount, payment_date) VALUES
('customer_123', 'ORD78901', 'Laptop', 'Shipped', '2023-10-26', 'TRK456789', 1200.0, '2023-10-25'),
('customer_123', 'ORD78900', 'Keyboard', 'Delivered', '2023-10-20', 'TRK123456', 75.0, '2023-10-19'),
('customer_123', 'ORD78903', 'Mouse', 'Delivered', '2023-11-01', 'TRK987654', 25.0, '2023-10-31'),
('customer_456', 'ORD78902', 'Monitor', 'Processing', NULL, NULL, 300.0, NULL),
('customer_456', 'ORD78904', 'Webcam', 'Shipped', '2023-11-05', 'TRK112233', 50.0, '2023-11-04'),
('customer_789', 'ORD78905', 'Printer', 'Delivered', '2023-10-28', 'TRK445566', 200.0, '2023-10-27'),
('customer_789', 'ORD78906', 'Speakers', 'Shipped', '2023-11-08', 'TRK778899', 150.0, '2023-11-07');
