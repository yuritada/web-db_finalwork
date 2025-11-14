# セットアップガイド

このドキュメントは、プロジェクトの初期セットアップ手順を説明します。

## 🚀 クイックスタート

### 初回セットアップ

```bash
# 1. 環境変数ファイルを確認（.envファイルが存在することを確認）
ls -la .env

# 2. クリーンセットアップを実行
make setup
```

`make setup` コマンドは以下を自動的に実行します:
1. Docker コンテナのビルドと起動
2. データベースマイグレーションの実行
3. テストデータの投入

### クリーンアップして再セットアップ

```bash
# すべてをクリーンアップ（ボリューム、イメージ、ネットワークを削除）
make clean

# 再度セットアップ
make setup
```

## 📋 利用可能なコマンド

### 基本コマンド

- `make up` - サービスを起動
- `make down` - サービスを停止
- `make clean` - すべてのリソースを削除（ボリューム、イメージ、ネットワーク）
- `make setup` - クリーンセットアップ（up + migrate + init）
- `make restart` - サービスを再起動
- `make ps` - 実行中のコンテナ一覧を表示

### ログ確認

- `make logs` - すべてのサービスのログを表示
- `make logs-be` - バックエンドのログを表示
- `make logs-fe` - フロントエンドのログを表示

### データベース管理

- `make migrate-be` - マイグレーションを実行
- `make init` - テストデータを投入
- `make sh-db` - データベースに接続（psql）

### 開発用

- `make sh-be` - バックエンドコンテナのシェルに入る
- `make sh-fe` - フロントエンドコンテナのシェルに入る
- `make install-be` - バックエンドの依存関係を再インストール
- `make install-fe` - フロントエンドの依存関係を再インストール
- `make build` - サービスを再ビルド

## 🔑 テスト用アカウント

初期化スクリプトは以下のテストユーザーを作成します:

### 学生アカウント
- **ユーザー名**: `student_test`
- **パスワード**: `password123`
- **メール**: student@test.com
- **学籍番号**: S12345
- **学部**: 情報工学部

### 教員アカウント
- **ユーザー名**: `professor_test`
- **パスワード**: `password123`
- **メール**: professor@test.com
- **学部**: 情報工学部

### 職員アカウント
- **ユーザー名**: `staff_test`
- **パスワード**: `password123`
- **メール**: staff@test.com

## 📦 初期データ

初期化スクリプトは以下のサンプルデータを作成します:

### チャンネル
1. **#general** - 一般的な話題のチャンネル（パブリック）
2. **#技術相談** - 技術的な質問や相談ができるチャンネル（パブリック）
3. **#プロジェクト管理** - プロジェクトの進捗管理用（プライベート）

すべてのテストユーザーは、すべてのチャンネルのメンバーとして追加されます。

### Wikiページ
1. **プロジェクト概要** - プロジェクトの概要を説明するページ
2. **使い方ガイド** - システムの使い方を説明するページ

すべてのWikiページは、student_testユーザーが作成者として設定されます。

## 🔧 トラブルシューティング

### ポートが既に使用されている

```bash
# エラー例: port is already allocated
# 解決方法: 既存のサービスを停止
make down
make up
```

### データベース接続エラー

```bash
# データベースが起動していることを確認
make ps

# データベースログを確認
docker compose logs db

# データベースを再起動
make restart
```

### マイグレーションエラー

```bash
# 現在のマイグレーションバージョンを確認
docker compose exec backend alembic current

# マイグレーション履歴を確認
docker compose exec backend alembic history

# 最新バージョンにアップグレード
make migrate-be
```

### 初期化スクリプトエラー

```bash
# 初期化スクリプトを手動で実行
docker compose exec backend python scripts/init_db.py

# データベースに直接接続して確認
make sh-db
\dt  # テーブル一覧を表示
SELECT * FROM users;  # ユーザー一覧を表示
```

## 📝 開発ワークフロー

### 通常の開発

```bash
# 1. サービスを起動
make up

# 2. ログを監視（別ターミナル）
make logs

# 3. コードを編集（ホットリロードが有効）

# 4. 必要に応じてコンテナに入る
make sh-be  # バックエンド
make sh-fe  # フロントエンド
```

### データベーススキーマ変更

```bash
# 1. モデルを変更（backend/app/models/*.py）

# 2. マイグレーションを自動生成
docker compose exec backend alembic revision --autogenerate -m "説明"

# 3. マイグレーションファイルを確認・編集
# backend/alembic/versions/*.py

# 4. マイグレーションを適用
make migrate-be

# 5. 初期化スクリプトを更新（必要に応じて）
# backend/scripts/init_db.py
```

### クリーンな状態でテスト

```bash
# すべてをリセット
make clean

# 再セットアップ
make setup

# ブラウザでテスト
# http://localhost:3000
```

## 🌐 アクセス先

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

## 📚 関連ドキュメント

- [API仕様書](backend/docs/api/)
- [データベーススキーマ](backend/app/models/)
- [マイグレーション履歴](backend/alembic/versions/)
