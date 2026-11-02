from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database import get_connection, create_table

app = FastAPI(title="Product Catalogue")
STATIC_DIR = Path(__file__).with_name("static")

create_table()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/api/products")
def list_products(search: str = "", category: str = ""):
    sql = "SELECT * FROM products WHERE name LIKE ?"
    values = [f"%{search}%"]

    if category:
        sql += " AND category = ?"
        values.append(category)

    sql += " ORDER BY id"
    with get_connection() as connection:
        rows = connection.execute(sql, values).fetchall()
    return [dict(row) for row in rows]

@app.get("/api/categories")
def list_categories():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT DISTINCT category FROM products ORDER BY category"
        ).fetchall()
    return [row["category"] for row in rows]

@app.get("/api/products/{product_id}")
def product_details(product_id: int):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)
