import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from psycopg2 import Error as Psycopg2Error
from app.db.connect import get_db_connection

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

def create_user_table(conn=None):
    """
    指定された接続（または get_db_connection() で取得した接続）を使って users テーブルを作成する。
    外部から渡した接続は閉じません。内部で作成した接続はこの関数で閉じます。
    戻り値: True 成功 / False 失敗
    """
    created_conn = False
    if conn is None:
        conn = get_db_connection()
        created_conn = True

    if conn is None:
        print("データベース接続に失敗したためテーブルを作成できませんでした。", file=sys.stderr)
        return False

    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_TABLE_SQL)
        # テーブル作成はDDLなのでコミット
        conn.commit()
        print("テーブル 'users' が正常に作成されました。")
        return True

    except Psycopg2Error as e:
        # エラー時はロールバックして詳細を出力
        try:
            conn.rollback()
        except Exception:
            pass
        print(f"データベースエラー: {e}", file=sys.stderr)
        return False

    finally:
        if created_conn:
            try:
                conn.close()
                print("データベース接続を閉じました。")
            except Exception as e:
                print(f"接続クローズ時のエラー: {e}", file=sys.stderr)


if __name__ == "__main__":
    create_user_table()
