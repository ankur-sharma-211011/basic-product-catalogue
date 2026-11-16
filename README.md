# Basic Product Catalogue with Admin Visitor Page

A beginner-friendly FastAPI + SQLite product catalogue. The admin page displays unique visitor IP addresses, estimated countries, request counts, and first/last seen times. The table refreshes every five seconds.

## Requirements
- Python 3.9+
- FastAPI and Uvicorn from `requirements.txt`
- SQLite is included with Python (`sqlite3`). No MySQL server or extra database driver is needed.

## Run on Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python seed.py
$env:ADMIN_PASSWORD = "choose-a-strong-password"
uvicorn main:app --reload
```

Open:
- Store: http://127.0.0.1:8000
- Admin: http://127.0.0.1:8000/admin
- API docs: http://127.0.0.1:8000/docs

Admin login uses HTTP Basic Authentication:
- Username: `admin`
- Password: the value assigned to `ADMIN_PASSWORD`

If `ADMIN_PASSWORD` is not set, admin access is disabled. There is no default password. Keep the terminal open while using the site.

## Features
- Product listing, name search, category filter, and product details popup.
- Admin page with total unique IP count and one table row per IP.
- Country, request count, first-seen and last-seen timestamps.
- Table refreshes automatically every five seconds.
- Admin page and its API require authentication.

## How visitor tracking works
FastAPI middleware records each non-admin, non-static request. The IP address is the primary key in the `visitor_log` table. If the IP already exists, its request count and last-seen timestamp are updated. Otherwise, a new row is inserted.

For a new public IP, the backend asks `ipapi.co` for an approximate country name. Local/private IP addresses (including localhost) are labelled `Local / Private network`. If the lookup fails, country is `Unknown`. Country lookup is only attempted the first time an IP is seen.

## Privacy and limitations
IP addresses may be personal data. Tell visitors that IP addresses are logged, restrict admin access, and delete records when no longer needed. Country lookup is approximate and may be inaccurate due to VPNs, mobile networks, or proxies. The visitor IP is sent to ipapi.co for country lookup. This demo uses the direct client IP; behind a reverse proxy, trusted proxy configuration is needed. Do not deploy this admin page publicly without HTTPS and a strong password.

This counts IP addresses, not individual people: multiple people may share one IP, and one person may use multiple IPs. Local testing will normally show `Local / Private network`.

## Architecture
```text
Browser (store) --> FastAPI routes --> SQLite products table
                         |
                         +-- visitor middleware --> SQLite visitor_log
                         |
Browser (admin) --> authenticated admin API --> visitor_log
       |
       +-- JavaScript refreshes table every 5 seconds
```

- `main.py`: routes, visitor middleware, IP country lookup, admin authentication.
- `database.py`: SQLite connection and database operations.
- `seed.py`: loads sample products.
- `sample_products.json`: sample catalogue.
- `static/index.html`: storefront.
- `static/admin.html`: admin dashboard.
- `products.db`: SQLite database, created automatically.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/products` | List/search/filter products |
| GET | `/api/categories` | List categories |
| GET | `/api/products/{product_id}` | Get product details |
| GET | `/api/admin/visitors` | Protected visitor statistics |

`python seed.py` resets product rows to the sample data. It does not delete visitor history.
