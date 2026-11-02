# Basic Product Catalogue

A deliberately small product listing website built with **FastAPI**, **SQLite**, and plain HTML/CSS/JavaScript.

## Requirements
- Python 3.9+
- Internet connection only to install the two Python packages in `requirements.txt`

SQLite is included with Python (`sqlite3`). You do not need to install MySQL, a database server, or a separate database driver.

## Run on Windows

Open a terminal in this folder and run:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** in your browser. Keep the terminal open while using the site.

## What it does
- Shows all seeded products as cards.
- Searches by product name.
- Filters by category.
- Opens a product details dialog with description, price, category, and stock.
- Stores products in a local SQLite database file (`products.db`).

## Architecture

There are only three main parts:

1. `static/index.html` — the entire browser interface and its small JavaScript.
2. `main.py` — FastAPI routes. It receives browser requests and returns JSON.
3. `database.py` — opens SQLite connections and creates the table.

`seed.py` inserts the sample data from `sample_products.json`.

```text
Browser (HTML + JavaScript)
          |
          | fetch()
          v
       main.py
      FastAPI API
          |
          v
     database.py
       sqlite3
          |
          v
      products.db
```

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/products` | List products |
| GET | `/api/products?search=watch` | Search by name |
| GET | `/api/products?category=Electronics` | Filter by category |
| GET | `/api/categories` | Get category names |
| GET | `/api/products/1` | Get one product's details |

Interactive API documentation: `http://127.0.0.1:8000/docs`

## Project files

```text
basic_product_catalogue/
├── main.py
├── database.py
├── seed.py
├── schema.sql
├── sample_products.json
├── products.db          # created/updated by seed.py
├── requirements.txt
├── README.md
├── static/
│   └── index.html
└── screenshots/
    ├── product-listing.png
    └── product-details.png
```

To reset the sample data, run `python seed.py` again. It replaces the current rows with the sample products.
