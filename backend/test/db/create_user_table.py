import psycopg2
from psycopg2 import sql

# --- PostgreSQL接続情報 ---
# ご自身の環境に合わせて、ユーザー名、パスワード、ホスト、ポート、データベース名を変更してください
DB_NAME = "miscat_db"
DB_USER = "admin"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = "5432"

# --- テーブル作成SQL ---
# Userクラスの属性に基づいてテーブルを定義します
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    role VARCHAR(50),
    faculty VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    icon_path VARCHAR(255)
);
"""

def create_user_table():
    """
    PostgreSQLデータベースに接続し、usersテーブルを作成します。
    """
    conn = None
    try:
        # データベースに接続
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # カーソルを取得
        cur = conn.cursor()
        
        # テーブル作成SQLを実行
        cur.execute(CREATE_TABLE_SQL)
        
        # 変更をコミット
        conn.commit()
        
        print("テーブル'users'が正常に作成されました。")
        
    except psycopg2.Error as e:
        print(f"データベースエラー: {e}")
        
    finally:
        # 接続を閉じる
        if conn is not None:
            cur.close()
            conn.close()
            print("データベース接続を閉じました。")

if __name__ == "__main__":
    create_user_table()
