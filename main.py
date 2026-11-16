import os
import ipaddress
import json
import secrets
from pathlib import Path
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException, Depends, Request as FastAPIRequest
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.concurrency import run_in_threadpool

from database import get_connection, create_table, record_visit, get_visitors

app = FastAPI(title="Basic Product Catalogue")
STATIC_DIR = Path(__file__).with_name("static")
security = HTTPBasic()


def find_country(ip_address):
    # Private and localhost IPs cannot be mapped to a public country.
    try:
        address = ipaddress.ip_address(ip_address)
        if address.is_private or address.is_loopback or address.is_link_local:
            return "Local / Private network"
    except ValueError:
        return "Unknown"

    # Query a free IP geolocation service only for a newly seen public IP.
    try:
        url = f"https://ipapi.co/{ip_address}/json/"
        request = Request(url, headers={"User-Agent": "BasicProductCatalogue/1.0"})
        with urlopen(request, timeout=2) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("country_name") or "Unknown"
    except Exception:
        return "Unknown"


def check_admin(credentials: HTTPBasicCredentials = Depends(security)):
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        raise HTTPException(
            status_code=503,
            detail="Admin is disabled. Set the ADMIN_PASSWORD environment variable.",
        )

    username_ok = secrets.compare_digest(credentials.username, "admin")
    password_ok = secrets.compare_digest(credentials.password, password)
    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=401,
            detail="Incorrect admin username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


create_table()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.middleware("http")
async def track_visitors(request: FastAPIRequest, call_next):
    response = await call_next(request)
    path = request.url.path

    # Exclude admin requests and static files.
    if (
        not path.startswith("/admin")
        and not path.startswith("/api/admin")
        and not path.startswith("/static")
    ):
        if request.client:
            # Start with the actual client IP.
            ip = request.client.host
            simulated_ip = request.headers.get("X-Simulated-IP")

            simulation_enabled = os.getenv("ALLOW_SIMULATED_IPS") == "1"
            is_local_client = ip in {"127.0.0.1", "::1", "localhost", "testclient"}

            # Accept simulated IPs only for local testing.
            if simulation_enabled and is_local_client and simulated_ip:
                try:
                    parsed_ip = ipaddress.ip_address(simulated_ip)

                    if parsed_ip.is_global:
                        ip = str(parsed_ip)

                except ValueError:
                    pass

            # Check whether this IP has already been recorded.
            with get_connection() as connection:
                known = connection.execute(
                    "SELECT country FROM visitor_log WHERE ip_address = ?", (ip,)
                ).fetchone()

            if known:
                country = known["country"]
            else:
                # Look up the country for a newly seen IP.
                country = await run_in_threadpool(find_country, ip)

            await run_in_threadpool(record_visit, ip, country)

    return response


@app.get("/")
def home():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/admin", dependencies=[Depends(check_admin)])
def admin_page():
    return FileResponse(STATIC_DIR / "admin.html")


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


@app.get("/api/admin/visitors", dependencies=[Depends(check_admin)])
def admin_visitors():
    visitors = [dict(row) for row in get_visitors()]
    return {"total_unique_ips": len(visitors), "visitors": visitors}
