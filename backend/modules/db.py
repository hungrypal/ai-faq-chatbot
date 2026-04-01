# ============================================================
#  modules/db.py — MySQL Database Helper
# ============================================================

import mysql.connector
from config import DB_CONFIG


def get_connection():
    """Create and return a MySQL connection."""
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=None, fetch='all'):
    """
    Run a SELECT query and return results.
    fetch = 'all'  → returns list of dicts
    fetch = 'one'  → returns a single dict or None
    """
    conn   = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(sql, params or ())
    result = cursor.fetchall() if fetch == 'all' else cursor.fetchone()
    cursor.close()
    conn.close()
    return result


def execute(sql, params=None):
    """
    Run an INSERT / UPDATE / DELETE statement.
    Returns the last inserted row ID (useful for INSERT).
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params or ())
    conn.commit()
    last_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return last_id


# ── Convenience helpers ───────────────────────────────────

def get_order(order_id):
    """Fetch a single order with product and user details."""
    sql = """
        SELECT o.order_id, o.status, o.delivery_date,
               p.name AS product_name, p.price,
               u.name AS user_name
        FROM   orders o
        JOIN   products p ON o.product_id = p.id
        JOIN   users    u ON o.user_id    = u.user_id
        WHERE  o.order_id = %s
    """
    return query(sql, (order_id,), fetch='one')


def get_products_by_category(category, max_price=None):
    """Fetch products, optionally filtered by category and max price."""
    if max_price:
        sql    = "SELECT * FROM products WHERE category = %s AND price <= %s ORDER BY rating DESC"
        params = (category, max_price)
    else:
        sql    = "SELECT * FROM products WHERE category = %s ORDER BY rating DESC"
        params = (category,)
    return query(sql, params)


def get_all_faqs():
    return query("SELECT * FROM faqs ORDER BY category")


def log_chat(user_query, intent, confidence, response):
    """Save chat interaction to DB for analytics."""
    execute(
        "INSERT INTO chat_logs (user_query, intent, confidence, response) VALUES (%s, %s, %s, %s)",
        (user_query, intent, confidence, response)
    )
