from dotenv import load_dotenv, find_dotenv
import os
import psycopg2
from psycopg2 import OperationalError

# .env をプロジェクトルートから自動検出して読み込む
env_path = find_dotenv()
if env_path:
        load_dotenv(env_path)

# 環境変数を取得（別名にも対応）
HOST = os.getenv("PGHOST") or os.getenv("DB_HOST") or "localhost"
PORT = os.getenv("PGPORT") or os.getenv("DB_PORT") or "5432"
USER = os.getenv("PGUSER") or os.getenv("DB_USER") or "postgres"
PASSWORD = os.getenv("PGPASSWORD") or os.getenv("DB_PASSWORD") or ""
DATABASE = os.getenv("PGDATABASE") or os.getenv("DB_NAME") or "postgres"
SSLMODE = os.getenv("PGSSLMODE")  # 例: "require"

_conn = None
try:
        conn_kwargs = dict(
                host=HOST,
                port=PORT,
                user=USER,
                password=PASSWORD,
                dbname=DATABASE,
        )
        if SSLMODE:
                conn_kwargs["sslmode"] = SSLMODE

        _conn = psycopg2.connect(**conn_kwargs)
except OperationalError as e:
        # 接続失敗の場合は例外をそのまま投げる（呼び出し元でハンドリング）
        raise

# 外部から利用する接続オブジェクト
conn = _conn