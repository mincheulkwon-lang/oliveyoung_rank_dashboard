import sqlite3
import pandas as pd

from config import DB_PATH


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS rankings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        collected_date TEXT NOT NULL,
        collected_time TEXT NOT NULL,
        category_name TEXT NOT NULL,
        rank INTEGER NOT NULL,
        brand_name TEXT,
        product_name TEXT,
        goods_no TEXT,
        normal_price INTEGER,
        sale_price INTEGER,
        discount_rate TEXT,
        product_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(
            collected_date,
            collected_time,
            category_name,
            goods_no
        )
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS crawl_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        category_name TEXT,
        status TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()


def insert_log(category_name, status, message):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO crawl_logs (
        category_name,
        status,
        message
    )
    VALUES (?, ?, ?)
    """, (
        category_name,
        status,
        message
    ))

    conn.commit()
    conn.close()


def insert_rankings(rows):
    if not rows:
        return 0

    conn = get_connection()
    cur = conn.cursor()

    inserted = 0

    for row in rows:
        try:
            cur.execute("""
            INSERT OR IGNORE INTO rankings (
                collected_date,
                collected_time,
                category_name,
                rank,
                brand_name,
                product_name,
                goods_no,
                normal_price,
                sale_price,
                discount_rate,
                product_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row.get("collected_date"),
                row.get("collected_time"),
                row.get("category_name"),
                row.get("rank"),
                row.get("brand_name"),
                row.get("product_name"),
                row.get("goods_no"),
                row.get("normal_price"),
                row.get("sale_price"),
                row.get("discount_rate"),
                row.get("product_url"),
            ))

            if cur.rowcount > 0:
                inserted += 1

        except Exception as e:
            insert_log(
                row.get("category_name", "알 수 없음"),
                "ERROR",
                f"DB 저장 실패: {e}"
            )

    conn.commit()
    conn.close()

    return inserted


def load_rankings():
    init_db()

    conn = get_connection()

    df = pd.read_sql_query("""
    SELECT *
    FROM rankings
    ORDER BY
        collected_date DESC,
        collected_time DESC,
        category_name ASC,
        rank ASC
    """, conn)

    conn.close()

    return df


def load_logs(limit=200):
    init_db()

    conn = get_connection()

    df = pd.read_sql_query(f"""
    SELECT *
    FROM crawl_logs
    ORDER BY log_time DESC
    LIMIT {limit}
    """, conn)

    conn.close()

    return df