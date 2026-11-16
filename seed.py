import json
from pathlib import Path
from database import get_connection, create_table

BASE_DIR = Path(__file__).resolve().parent
create_table()

with open(BASE_DIR / "sample_products.json", encoding="utf-8") as file:
    products = json.load(file)

with get_connection() as connection:
    connection.execute("DELETE FROM products")
    connection.executemany("""
        INSERT INTO products (name, category, price, stock, description)
        VALUES (:name, :category, :price, :stock, :description)
    """, products)

print(f"Added {len(products)} sample products.")
