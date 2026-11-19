-- views.sql
-- Creates the five KPI views the dashboard and the AI question box read from.
-- Run this in the Supabase SQL Editor. CREATE OR REPLACE means you can safely run it again.
-- Cancelled orders are left out of revenue and margin, because that money never came in.

-- Monthly revenue: how many orders and how much money came in each month.
CREATE OR REPLACE VIEW monthly_revenue AS
SELECT DATE_TRUNC('month', o.order_date)::date AS month,
       COUNT(DISTINCT o.order_id)              AS orders,
       SUM(l.quantity * l.unit_price)          AS revenue
FROM sales_orders o
JOIN order_lines l ON l.order_id = o.order_id
WHERE o.status <> 'Cancelled'
GROUP BY month
ORDER BY month;

-- Top products: units sold and revenue per product per month.
-- The month column lets the dashboard filter by date, then rank the products.
CREATE OR REPLACE VIEW top_products AS
SELECT DATE_TRUNC('month', o.order_date)::date AS month,
       p.product_id,
       p.name                                  AS product_name,
       p.category,
       SUM(l.quantity)                         AS units_sold,
       SUM(l.quantity * l.unit_price)          AS revenue
FROM order_lines l
JOIN sales_orders o ON o.order_id = l.order_id
JOIN products p     ON p.product_id = l.product_id
WHERE o.status <> 'Cancelled'
GROUP BY month, p.product_id, p.name, p.category;

-- Order status: how many orders are Open, Shipped, Delivered or Cancelled, per month.
CREATE OR REPLACE VIEW order_status AS
SELECT DATE_TRUNC('month', order_date)::date AS month,
       status,
       COUNT(*)                              AS orders
FROM sales_orders
GROUP BY month, status;

-- Low stock: products whose stock is below the reorder level, and how many units are missing.
CREATE OR REPLACE VIEW low_stock AS
SELECT p.product_id,
       p.name                              AS product_name,
       p.category,
       s.quantity_on_hand,
       s.reorder_level,
       s.reorder_level - s.quantity_on_hand AS shortfall
FROM stock_levels s
JOIN products p ON p.product_id = s.product_id
WHERE s.quantity_on_hand < s.reorder_level;

-- Gross margin: revenue, cost and profit per product per month.
-- Cost uses the product's cost price from the products table (quantity x unit_cost).
CREATE OR REPLACE VIEW gross_margin AS
SELECT DATE_TRUNC('month', o.order_date)::date              AS month,
       p.product_id,
       p.name                                               AS product_name,
       p.category,
       SUM(l.quantity * l.unit_price)                       AS revenue,
       SUM(l.quantity * p.unit_cost)                        AS cost,
       SUM(l.quantity * (l.unit_price - p.unit_cost))       AS margin,
       ROUND(100 * SUM(l.quantity * (l.unit_price - p.unit_cost))
             / NULLIF(SUM(l.quantity * l.unit_price), 0), 1) AS margin_pct
FROM order_lines l
JOIN sales_orders o ON o.order_id = l.order_id
JOIN products p     ON p.product_id = l.product_id
WHERE o.status <> 'Cancelled'
GROUP BY month, p.product_id, p.name, p.category;
