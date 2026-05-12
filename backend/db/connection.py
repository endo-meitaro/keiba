import psycopg2
from psycopg2.extras import execute_values
from contextlib import contextmanager
import config

def get_conn():
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
    )

@contextmanager
def transaction():
    conn = get_conn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def apply_schema():
    """schema.sql を実行してテーブルを作成する"""
    import os
    sql_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(sql_path, encoding="utf-8") as f:
        sql = f.read()
    with transaction() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    print("スキーマを適用しました")
