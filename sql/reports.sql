--order totals 
SELECT 
    COUNT(*) AS total_orders,
    round(SUM(o.quantity * p.price *(1 - COALESCE(d.discount_pct, 0) / 100.0)), 2) AS total_revenue,
    round(AVG(o.quantity * p.price *(1 - COALESCE(d.discount_pct, 0) / 100.0)), 2) AS average_order_value
FROM orders o
JOIN products p ON o.product_id = p.product_id;


--COUNT(*) vs COUNT(column)
SELECT
COUNt (*) AS total_orders,
COUNT(rating) AS rated_orders,
(COUNT(*)) - COUNT(rating) AS unrated_orders
FROM orders;

--finding inactive customers
SELECT c.customer_id, c.name
FROM customers c 
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
HAVING COUNT(o.order_id) = 0;


--high retunr rate cities
SELECT
      c.city, 
      COUNT(o.order_id) AS total_orders,
      SUM(o.returned) AS returned_orders,
      ROUND(100.0 *SUM(o.returned) / COUNT(o.order_id), 2) AS return_rate_pct
      FROM orders o                              
      JOIN customers c ON o.customer_id = c.customer_id
      GROUP BY c.city
      HAVING return_rate_pct > 20
      ORDER BY return_rate_pct DESC


--top spenders
SELECT
     c.customer_id, c.name, SUM(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0))) AS total_spent
FROM orders o JOIN customers c ON o.customer_id = c.customer_id JOIN products p ON o.product_id = p.product_id 
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC, c.customer_id ASC
LIMIT 3 OFFSET 2;

-- independent check using NOT IN
SELECT c.customer_id, c.name
FROM customers c
WHERE c.customer_id NOT IN (SELECT DISTINCT O.customer_id FROM orders o);

 -- e) Ranking with ORDER BY + LIMIT/OFFSET (Top 5 Spenders)
SELECT 
    c.customer_id, 
    c.name, 
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS total_spend
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
GROUP BY c.customer_id, c.name
ORDER BY total_spend DESC, c.customer_id ASC
LIMIT 5;

-- f) Three-table JOIN with GROUP BY
SELECT 
    p.category,
    COUNT(o.order_id) AS order_count,
    ROUND(SUM(o.quantity * p.price * (1 - COALESCE(o.discount_pct, 0) / 100.0)), 2) AS category_revenue
FROM orders o
JOIN products p ON o.product_id = p.product_id
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY p.category
ORDER BY category_revenue DESC;


-- g) LIKE pattern match
SELECT * 
FROM customers 
WHERE name LIKE 'A%';

-- h) DISTINCT
SELECT DISTINCT acquisition_source 
FROM customers;

-- i) ALTER TABLE + UPDATE with CASE
ALTER TABLE customers ADD COLUMN loyalty_tier VARCHAR(10);
UPDATE customers SET loyalty_tier = CASE WHEN city_tier = 1 THEN 'Gold' ELSE 'Silver' END;

SELECT loyalty_tier, COUNT(*) AS count 
FROM customers 
GROUP BY loyalty_tier;





















    