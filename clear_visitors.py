from database import get_connection

with get_connection() as connection:
    connection.execute("DELETE FROM visitor_log")

print("All visitor records cleared successfully.")
