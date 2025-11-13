#!/usr/bin/env python3
"""
テストアカウント投入スクリプト（開発環境専用）

開発・テスト用の各種ユーザーアカウントを作成します。

使用方法:
    # Dockerコンテナ内で実行
    docker exec finalwork-backend-1 python tests/seed_test_accounts.py

    # ローカルで実行（仮想環境内）
    cd backend
    python tests/seed_test_accounts.py

作成されるテストアカウント:
    - 学生 x 2名 (student1, student2)
    - 教授 x 1名 (professor1)
    - 准教授 x 1名 (associate_prof1)
    - 講師 x 1名 (lecturer1)
    - 事務 x 1名 (staff1)
    合計: 6名

全アカウントのパスワード: test1234
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.exc import IntegrityError
import bcrypt
from app.db.connect import SessionLocal
from app.models.user import User, UserKategori
import uuid


# テストアカウント定義
TEST_ACCOUNTS = [
    # 学生アカウント x 2
    {
        "username": "student1",
        "email": "student1@test.com",
        "password": "test1234",
        "kategori": UserKategori.STUDENT,
        "gakuseki_bango": "2024001",
        "faculty": "工学部"
    },
    {
        "username": "student2",
        "email": "student2@test.com",
        "password": "test1234",
        "kategori": UserKategori.STUDENT,
        "gakuseki_bango": "2024002",
        "faculty": "情報学部"
    },
    {
        "username": "多田有里",
        "email": "s2422110@stu.musashino-u.ac.jp",
        "password": "test1234",
        "kategori": UserKategori.STUDENT,
        "gakuseki_bango": "2422110",
        "faculty": "データサイエンス学部"
    },
    # 教授アカウント x 1
    {
        "username": "professor1",
        "email": "professor1@test.com",
        "password": "test1234",
        "kategori": UserKategori.PROFESSOR,
        "gakuseki_bango": None,  # 自動生成
        "faculty": "情報工学科"
    },
    # 准教授アカウント x 1
    {
        "username": "associate_prof1",
        "email": "associate_prof1@test.com",
        "password": "test1234",
        "kategori": UserKategori.ASSOCIATE_PROFESSOR,
        "gakuseki_bango": None,  # 自動生成
        "faculty": "数学科"
    },
    # 講師アカウント x 1
    {
        "username": "lecturer1",
        "email": "lecturer1@test.com",
        "password": "test1234",
        "kategori": UserKategori.LECTURER,
        "gakuseki_bango": None,  # 自動生成
        "faculty": "物理学科"
    },
    # 事務アカウント x 1
    {
        "username": "staff1",
        "email": "staff1@test.com",
        "password": "test1234",
        "kategori": UserKategori.STAFF,
        "gakuseki_bango": None,  # 自動生成
        "faculty": None
    },
]


def create_test_accounts():
    """テストアカウントを作成する"""

    db = SessionLocal()

    try:
        created_users = []
        skipped_users = []

        print("🔧 テストアカウント作成開始...")
        print()

        for user_data in TEST_ACCOUNTS:
            try:
                # パスワードをハッシュ化
                password_bytes = user_data["password"].encode('utf-8')
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

                # gakuseki_bangoの処理（学生以外は自動生成）
                gakuseki_bango = user_data["gakuseki_bango"]
                if user_data["kategori"] != UserKategori.STUDENT:
                    gakuseki_bango = f"staff_{uuid.uuid4().hex[:8]}"

                # Userモデルのインスタンスを作成
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hashed_password,
                    kategori=user_data["kategori"],
                    gakuseki_bango=gakuseki_bango,
                    faculty=user_data["faculty"]
                )

                db.add(user)
                db.commit()
                db.refresh(user)

                created_users.append(user)

                print(f"✅ {user.kategori.value}: {user.username}")
                print(f"   Email: {user.email}")
                print(f"   学籍番号: {user.gakuseki_bango}")
                print(f"   ID: {user.id}")
                print()

            except IntegrityError:
                db.rollback()
                skipped_users.append(user_data["username"])
                print(f"⚠️  スキップ: {user_data['username']} (既に存在)")
                print(f"   Email: {user_data['email']}")
                print()
                continue

            except Exception as e:
                db.rollback()
                print(f"❌ エラー: {user_data['username']}")
                print(f"   {str(e)}")
                print()
                continue

        # サマリー表示
        print("=" * 70)
        print(f"✅ 完了: {len(created_users)}/{len(TEST_ACCOUNTS)} アカウントを作成")
        if skipped_users:
            print(f"⚠️  スキップ: {len(skipped_users)} アカウント（既存）")
        print("=" * 70)
        print()

        # ログイン情報表示
        print("📝 テストアカウント一覧:")
        print()
        print("【学生】")
        print("  - student1@test.com / test1234")
        print("  - student2@test.com / test1234")
        print()
        print("【教授】")
        print("  - professor1@test.com / test1234")
        print()
        print("【准教授】")
        print("  - associate_prof1@test.com / test1234")
        print()
        print("【講師】")
        print("  - lecturer1@test.com / test1234")
        print()
        print("【事務】")
        print("  - staff1@test.com / test1234")
        print()
        print("🔗 APIドキュメント: http://localhost:8000/docs")
        print("🔗 フロントエンド: http://localhost:3000")
        print()

    except Exception as e:
        print(f"❌ 予期せぬエラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 70)
    print("テストアカウント投入スクリプト（開発環境専用）")
    print("=" * 70)
    print()
    print("⚠️  注意: このスクリプトは開発環境でのみ使用してください")
    print()

    create_test_accounts()
