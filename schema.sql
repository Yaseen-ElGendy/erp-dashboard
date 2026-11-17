-- schema.sql
-- Creates the six ERP style tables. Run this once in the Supabase SQL Editor.
-- Tables are created in order, so every table a foreign key points to already exists.

-- Customers: who buys from us (like the SAP customer master).
CREATE TABLE customers (
    customer_id  SERIAL PRIMARY KEY,
    name         TEXT NOT NULL,
    city         TEXT NOT NULL,
    segment      TEXT NOT NULL CHECK (segment IN ('Retail', 'Wholesale'))
);

-- Vendors: who supplies our products.
CREATE TABLE vendors (
    vendor_id  SERIAL PRIMARY KEY,
    name       TEXT NOT NULL,
    country    TEXT NOT NULL
);

-- Products: what we sell, what it costs us, and what we charge (like the SAP material master).
CREATE TABLE products (
    product_id  SERIAL PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT NOT NULL,
    vendor_id   INT NOT NULL REFERENCES vendors (vendor_id),
    unit_cost   NUMERIC(10, 2) NOT NULL CHECK (unit_cost >= 0),
    unit_price  NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

-- Sales orders: one row per order, who ordered, when, and its status (like a sales order header).
CREATE TABLE sales_orders (
    order_id     SERIAL PRIMARY KEY,
    customer_id  INT NOT NULL REFERENCES customers (customer_id),
    order_date   DATE NOT NULL,
    status       TEXT NOT NULL CHECK (status IN ('Open', 'Shipped', 'Delivered', 'Cancelled'))
);

-- Order lines: one row per product on an order (like sales order items).
-- unit_price is the price at the time of sale, so later price changes don't alter past revenue.
CREATE TABLE order_lines (
    line_id     SERIAL PRIMARY KEY,
    order_id    INT NOT NULL REFERENCES sales_orders (order_id),
    product_id  INT NOT NULL REFERENCES products (product_id),
    quantity    INT NOT NULL CHECK (quantity > 0),
    unit_price  NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0)
);

-- Stock levels: how many of each product we hold, and when to reorder. One row per product.
CREATE TABLE stock_levels (
    product_id        INT PRIMARY KEY REFERENCES products (product_id),
    quantity_on_hand  INT NOT NULL CHECK (quantity_on_hand >= 0),
    reorder_level     INT NOT NULL CHECK (reorder_level >= 0)
);
