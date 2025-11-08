from dotenv import load_dotenv, find_dotenv
import os
import psycopg2
from psycopg2 import OperationalError
import sys

# .env をプロジェクトルートから自動検出して読み込む
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path)
    # print(f".envファイル ({env_path}) を読み込みました。") # デバッグ用
else:
    print(".envファイルが見つかりません。", file=sys.stderr)


def get_db_connection():
    """
    環境変数に基づいてPostgreSQLデータベースへの接続を試み、
    接続オブジェクトまたはNoneを返します。
    """
    
    # .env ファイルのキー構造に合わせて環境変数を取得
    # .env に定義がない場合はデフォルト値（'localhost'や'5432'）を使用
    conn_kwargs = {
        "host": os.getenv("PGHOST") or "localhost",
        "port": os.getenv("PGPORT") or "5432",
        "user": os.getenv("POSTGRES_USER"), # .env から読み込む
        "password": os.getenv("POSTGRES_PASSWORD"), # .env から読み込む
        "dbname": os.getenv("POSTGRES_DB"), # .env から読み込む
    }
    
    # ユーザー名やパスワードが設定されていない場合のエラーチェック
    if not conn_kwargs["user"] or not conn_kwargs["password"]:
        print("エラー: POSTGRES_USER または POSTGRES_PASSWORD が .env に設定されていません。", file=sys.stderr)
        return None

    try:
        # データベースへ接続
        conn = psycopg2.connect(**conn_kwargs)
        return conn
    except OperationalError as e:
        # 接続失敗の場合はエラーメッセージを表示
        print(f"データベース接続に失敗しました:\n{e}", file=sys.stderr)
        return None

# このファイルが直接実行された場合（お試し実行用）
if __name__ == "__main__":
    
    print("データベース接続を試みます...")
    
    # 接続オブジェクトを初期化
    conn = None
    
    try:
        # 接続関数を呼び出す
        conn = get_db_connection()
        
        # 接続に成功した場合
        if conn:
            print("\n✅ 接続に成功しました！")
            
            # 接続確認のため、簡単なクエリ（バージョン情報取得）を実行
            # 'with' を使うとカーソルとトランザクションが自動で管理されます
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                db_version = cur.fetchone()
                print(f"データベースのバージョン:\n{db_version[0]}")
            
    except Exception as e:
        # その他の予期せぬエラー
        print(f"予期せぬエラーが発生しました: {e}", file=sys.stderr)
        
    finally:
        # 接続オブジェクトが作成されていたら（＝接続に一度成功したら）
        if conn:
            # 接続を閉じる
            conn.close()
            print("\nデータベース接続を切断しました。")