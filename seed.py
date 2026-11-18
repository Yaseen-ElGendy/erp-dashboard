# seed.py
# Fills the six ERP tables with about 12 months of synthetic (made up) data.
# Run it from PowerShell in the project folder. The database link is read from .env.

import os
import random
from datetime import date, timedelta

import psycopg
from dotenv import load_dotenv
from faker import Faker

# Use the same random seed on every run, so the "random" data comes out identical each time.
random.seed(42)
Faker.seed(42)
fake = Faker("de_DE")

START_DATE = date(2025, 11, 19)
END_DATE = date(2026, 11, 18)
NUM_VENDORS = 8
NUM_CUSTOMERS = 200
NUM_ORDERS = 3000

VENDOR_COUNTRIES = ["Germany", "Netherlands", "Poland", "Italy", "China", "USA"]

# The product catalogue: 5 categories with 8 products each, 40 products in total.
CATALOGUE = {
    "Office Furniture": ["Office Desk", "Office Chair", "Filing Cabinet", "Bookshelf",
                         "Standing Desk", "Meeting Table", "Desk Lamp", "Whiteboard"],
    "Computers": ["Laptop 14", "Laptop 16", "Desktop PC", "Monitor 24", "Monitor 27",
                  "Tablet", "Docking Station", "External SSD"],
    "Accessories": ["Keyboard", "Mouse", "Headset", "Webcam", "USB Hub",
                    "Laptop Bag", "Monitor Arm", "Mouse Pad"],
    "Office Supplies": ["Printer Paper", "Ballpoint Pens", "Stapler", "Notebooks",
                        "Sticky Notes", "Folders", "Toner Cartridge", "Envelopes"],
    "Networking": ["Router", "Network Switch", "WiFi Access Point", "Network Cable",
                   "Firewall", "Patch Panel", "Server Rack", "NAS Storage"],
}


# Empties all six tables and resets their IDs to start at 1 again, so a re-run gives the same result.
def clear_tables(cur):
    cur.execute("TRUNCATE order_lines, sales_orders, stock_levels, products, customers, vendors "
                "RESTART IDENTITY")


# Creates the vendors (the suppliers).
def seed_vendors(cur):
    rows = [(fake.company(), random.choice(VENDOR_COUNTRIES)) for _ in range(NUM_VENDORS)]
    cur.executemany("INSERT INTO vendors (name, country) VALUES (%s, %s)", rows)


# Creates the products. The selling price is 1.3 to 2.0 times the cost, so every product makes a profit.
# Returns a list of (product_id, unit_price) that the orders use later.
def seed_products(cur):
    rows = []
    for category, names in CATALOGUE.items():
        for name in names:
            cost = round(random.uniform(5, 500), 2)
            price = round(cost * random.uniform(1.3, 2.0), 2)
            rows.append((name, category, random.randint(1, NUM_VENDORS), cost, price))
    cur.executemany("INSERT INTO products (name, category, vendor_id, unit_cost, unit_price) "
                    "VALUES (%s, %s, %s, %s, %s)", rows)
    # IDs start at 1 because clear_tables reset them, so the first product has id 1, and so on.
    return [(i + 1, row[4]) for i, row in enumerate(rows)]


# Creates the customers. About 80% are Retail and 20% are Wholesale.
def seed_customers(cur):
    rows = []
    for _ in range(NUM_CUSTOMERS):
        segment = "Retail" if random.random() < 0.8 else "Wholesale"
        rows.append((fake.company(), fake.city(), segment))
    cur.executemany("INSERT INTO customers (name, city, segment) VALUES (%s, %s, %s)", rows)


# Picks a status based on the order's age: new orders are Open or Shipped, older ones Delivered.
# About 5% of all orders are Cancelled.
def pick_status(order_date):
    if random.random() < 0.05:
        return "Cancelled"
    age_days = (END_DATE - order_date).days
    if age_days < 7:
        return random.choice(["Open", "Shipped"])
    if age_days < 30:
        return random.choice(["Shipped", "Delivered"])
    return "Delivered"


# Creates the sales orders (sorted by date, so order 1 is the oldest), then gives each order 1 to 5 lines.
# Each line copies the product's current price, just like a real sales order does.
def seed_orders(cur, products):
    total_days = (END_DATE - START_DATE).days
    dates = sorted(START_DATE + timedelta(days=random.randint(0, total_days)) for _ in range(NUM_ORDERS))
    orders = [(random.randint(1, NUM_CUSTOMERS), d, pick_status(d)) for d in dates]
    cur.executemany("INSERT INTO sales_orders (customer_id, order_date, status) VALUES (%s, %s, %s)",
                    orders)

    lines = []
    for order_id in range(1, NUM_ORDERS + 1):
        for product_id, price in random.sample(products, random.randint(1, 5)):
            lines.append((order_id, product_id, random.randint(1, 10), price))
    cur.executemany("INSERT INTO order_lines (order_id, product_id, quantity, unit_price) "
                    "VALUES (%s, %s, %s, %s)", lines)


# Sets how many of each product is in the warehouse and the level at which to reorder.
# Some products land below their reorder level, so the low stock view will have results.
def seed_stock(cur, products):
    rows = [(product_id, random.randint(0, 500), random.randint(20, 100)) for product_id, _ in products]
    cur.executemany("INSERT INTO stock_levels (product_id, quantity_on_hand, reorder_level) "
                    "VALUES (%s, %s, %s)", rows)


# Prints how many rows each table now holds.
def print_counts(cur):
    for table in ["vendors", "products", "customers", "sales_orders", "order_lines", "stock_levels"]:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"{table}: {cur.fetchone()[0]}")


# Connects with the link from .env and runs every step in order (parents before children).
# Everything is saved together at the end. If any step fails, nothing is saved.
def main():
    load_dotenv()
    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            clear_tables(cur)
            seed_vendors(cur)
            products = seed_products(cur)
            seed_customers(cur)
            seed_orders(cur, products)
            seed_stock(cur, products)
            print_counts(cur)


if __name__ == "__main__":
    main()
