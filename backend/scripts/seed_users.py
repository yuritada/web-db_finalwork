#!/usr/bin/env python3
"""
テストユーザー投入スクリプト

テスト用の初期ユーザーを作成します。

使用方法:
    docker exec finalwork-backend-1 python scripts/seed_users.py

作成されるユーザー:
    1. 学生ユーザー (gakuseki_bango: "2024001")
    2. 教授ユーザー (gakuseki_bango: 自動生成)
    3. 事務ユーザー (gakuseki_bango: 自動生成)

全ユーザーのパスワード: testpass123
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


def seed_test_users():
    """テストユーザーを作成する"""

    # データベースセッションを作成
    db = SessionLocal()

    try:
        # テストユーザーデータ
        test_users = [
            {
                "username": "student_test",
                "email": "student@example.com",
                "password": "testpass123",
                "kategori": UserKategori.STUDENT,
                "gakuseki_bango": "2024001",
                "faculty": "工学部"
            },
            {
                "username": "professor_test",
                "email": "professor@example.com",
                "password": "testpass123",
                "kategori": UserKategori.PROFESSOR,
                "gakuseki_bango": None,  # 自動生成される
                "faculty": "情報工学科"
            },
            {
                "username": "staff_test",
                "email": "staff@example.com",
                "password": "testpass123",
                "kategori": UserKategori.STAFF,
                "gakuseki_bango": None,  # 自動生成される
                "faculty": None
            }
        ]

        created_users = []

        for user_data in test_users:
            try:
                # パスワードをハッシュ化（bcrypt直接使用）
                password_bytes = user_data["password"].encode('utf-8')
                salt = bcrypt.gensalt()
                hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

                # gakuseki_bangoの処理
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

                print(f"✅ ユーザー作成成功: {user.username} ({user.kategori.value})")
                print(f"   - Email: {user.email}")
                print(f"   - 学籍番号: {user.gakuseki_bango}")
                print(f"   - ID: {user.id}")
                print()

            except IntegrityError as e:
                db.rollback()
                print(f"⚠️  ユーザー '{user_data['username']}' は既に存在します")
                print(f"   - Email: {user_data['email']}")
                print()
                continue
            except Exception as e:
                db.rollback()
                print(f"❌ ユーザー作成失敗: {user_data['username']}")
                print(f"   - エラー: {str(e)}")
                print()
                continue

        print("=" * 60)
        print(f"✅ 完了: {len(created_users)}/{len(test_users)} ユーザーを作成しました")
        print("=" * 60)
        print()
        print("📝 作成されたユーザーでログインできます:")
        print("   - student@example.com / testpass123")
        print("   - professor@example.com / testpass123")
        print("   - staff@example.com / testpass123")
        print()
        print("🔗 Swagger UIでテスト: http://localhost:8000/docs")

    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("テストユーザー投入スクリプト")
    print("=" * 60)
    print()

    seed_test_users()
