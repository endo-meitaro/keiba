import os

# ── JV-Link ──────────────────────────────────────────────
# JRA-VAN Data Lab のマイページで確認できる「ソフトウェアID」を設定する
JVLINK_SID: str = os.getenv("JVLINK_SID", "")

# ── PostgreSQL ───────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST",     "localhost")
DB_PORT     = int(os.getenv("DB_PORT", "5432"))
DB_NAME     = os.getenv("DB_NAME",     "keiba")
DB_USER     = os.getenv("DB_USER",     "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "keiba")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
