#!/usr/bin/env python3
"""
データベース初期化スクリプト

このスクリプトは以下を実行します：
1. テストユーザーの作成
2. サンプルチャンネルの作成
3. チャンネルメンバーシップの設定
4. サンプルWikiページの作成

使い方:
    docker-compose exec backend python scripts/init_db.py
"""

import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.connect import get_session
from app.db.create import create_user, create_channel, add_channel_member, create_wiki_page
from app.models.user import UserKategori
from app.models.wiki import PermissionLevel
from app.schemas.user import UserCreate
from app.schemas.channel import ChannelCreate
from app.schemas.wiki import WikiPageCreate
from sqlalchemy.exc import IntegrityError


def init_test_users(db):
    """テストユーザーを作成"""
    print("Creating test users...")

    test_users = [
        UserCreate(
            username="student_test",
            email="student@test.com",
            password="password123",
            kategori=UserKategori.STUDENT,
            gakuseki_bango="S12345",
            faculty="情報工学部"
        ),
        UserCreate(
            username="professor_test",
            email="professor@test.com",
            password="password123",
            kategori=UserKategori.PROFESSOR,
            faculty="情報工学部"
        ),
        UserCreate(
            username="staff_test",
            email="staff@test.com",
            password="password123",
            kategori=UserKategori.STAFF
        ),
    ]

    created_users = []
    for user_data in test_users:
        try:
            user = create_user(db, user_data)
            created_users.append(user)
            print(f"  ✓ Created user: {user.username} ({user.email})")
        except IntegrityError:
            db.rollback()
            print(f"  - User already exists: {user_data.username}")
            # 既存ユーザーを取得
            from app.db.read import get_user_by_username
            user = get_user_by_username(db, user_data.username)
            if user:
                created_users.append(user)
        except Exception as e:
            db.rollback()
            print(f"  ✗ Error creating user {user_data.username}: {e}")

    return created_users


def init_sample_channels(db, users):
    """サンプルチャンネルを作成"""
    print("\nCreating sample channels...")

    channels_data = [
        ChannelCreate(
            name="general",
            description="一般的な話題のチャンネル",
            is_private=False
        ),
        ChannelCreate(
            name="技術相談",
            description="技術的な質問や相談ができるチャンネル",
            is_private=False
        ),
        ChannelCreate(
            name="プロジェクト管理",
            description="プロジェクトの進捗管理用",
            is_private=True
        ),
    ]

    created_channels = []
    for channel_data in channels_data:
        try:
            channel = create_channel(db, channel_data)
            created_channels.append(channel)
            print(f"  ✓ Created channel: #{channel.name}")

            # 全ユーザーをチャンネルメンバーとして追加
            for user in users:
                try:
                    add_channel_member(db, channel.id, user.id)
                    print(f"    + Added {user.username} to #{channel.name}")
                except IntegrityError:
                    db.rollback()
                except Exception as e:
                    db.rollback()
                    print(f"    ! Error adding {user.username}: {e}")

        except IntegrityError:
            db.rollback()
            print(f"  - Channel already exists: #{channel_data.name}")
            from app.db.read import get_channel_by_name
            channel = get_channel_by_name(db, channel_data.name)
            if channel:
                created_channels.append(channel)
        except Exception as e:
            db.rollback()
            print(f"  ✗ Error creating channel {channel_data.name}: {e}")

    return created_channels


def init_sample_wiki_pages(db, users):
    """サンプルWikiページを作成"""
    print("\nCreating sample wiki pages...")

    if not users:
        print("  ! No users available, skipping wiki creation")
        return []

    creator = users[0]  # 最初のユーザーをWiki作成者とする

    wiki_pages_data = [
        WikiPageCreate(
            title="プロジェクト概要",
            content="""# プロジェクト概要

このプロジェクトは、大学内のコミュニケーションを円滑にするためのプラットフォームです。

## 主な機能

- チャンネルベースのメッセージング
- ダイレクトメッセージ（DM）
- Wiki機能
- タグ管理
- 検索機能

## 利用方法

1. アカウントを作成
2. チャンネルに参加
3. メッセージを送信
4. 必要に応じてWikiにまとめる
"""
        ),
        WikiPageCreate(
            title="使い方ガイド",
            content="""# 使い方ガイド

## チャンネルの使い方

1. 左メニューから「チャンネル」を選択
2. 参加したいチャンネルをクリック
3. メッセージを入力して送信

## DMの使い方

1. 検索機能でユーザーを探す
2. 「DMを送る」ボタンをクリック
3. メッセージを送信

## Wikiの使い方

1. チャンネルやDMで「Wikiにまとめる」をクリック
2. タイトルと内容を編集
3. 保存して共有
"""
        ),
    ]

    created_pages = []
    for page_data in wiki_pages_data:
        try:
            page = create_wiki_page(db, page_data, creator.id)
            created_pages.append(page)
            print(f"  ✓ Created wiki page: {page.title}")
        except Exception as e:
            db.rollback()
            print(f"  ✗ Error creating wiki page {page_data.title}: {e}")

    return created_pages


def main():
    """メイン処理"""
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)

    # データベースセッションを取得
    db = next(get_session())

    try:
        # 1. テストユーザーを作成
        users = init_test_users(db)

        # 2. サンプルチャンネルを作成
        channels = init_sample_channels(db, users)

        # 3. サンプルWikiページを作成
        wiki_pages = init_sample_wiki_pages(db, users)

        print("\n" + "=" * 60)
        print("Initialization completed successfully!")
        print("=" * 60)
        print(f"Created {len(users)} users")
        print(f"Created {len(channels)} channels")
        print(f"Created {len(wiki_pages)} wiki pages")
        print("\nTest credentials:")
        print("  Username: student_test")
        print("  Password: password123")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        db.rollback()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())
