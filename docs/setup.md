# セットアップガイド

---

## 前提条件

開発環境で以下がインストールされている必要があります：

### 必須ソフトウェア

| ソフトウェア | バージョン | 確認コマンド |
|------------|-----------|------------|
| Docker | 20.10以上 | `docker --version` |
| Docker Compose | 2.0以上 | `docker-compose --version` |
| Make | 任意 | `make --version` |
| Git | 任意 | `git --version` |

### システム要件

- メモリ: 最低4GB（推奨8GB以上）
- ディスク: 最低5GB の空き容量
- OS: macOS, Linux, Windows (WSL2)

---

## 初回セットアップ

### 1. リポジトリクローン

```bash
# リポジトリをクローン
git clone <repository-url>
cd finalwork

# ブランチ確認
git branch
```

### 2. 環境変数設定

バックエンド用の環境変数ファイルを作成します：

```bash
# backend/.env ファイルを作成
cat > backend/.env << 'EOF'
# Database
DATABASE_URL=postgresql://fastapi_user:fastapi_password@db:5432/commu_db

# JWT Settings
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000

# Environment
ENVIRONMENT=development
EOF
```

フロントエンド用の環境変数ファイルを作成します：

```bash
# frontend/.env.local ファイルを作成
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
```

> **セキュリティ注意事項**
> - `SECRET_KEY` は本番環境では必ず変更してください
> - `.env` ファイルはGit管理対象外です（`.gitignore` に含まれています）

### 3. Docker Composeでサービス起動

```bash
# 全サービスをビルドして起動
make up

# または、Docker Composeコマンドを直接使用
docker-compose up -d --build
```

起動には初回3-5分程度かかります。以下のログが表示されれば成功です：

```
✅ Backend: Application startup complete
✅ Frontend: Ready in 842ms
✅ Database: ready to accept connections
```

### 4. データベースマイグレーション実行

データベーススキーマを作成します：

```bash
# Alembicマイグレーション実行
make migrate-be

# または、Docker Composeコマンドで直接実行
docker exec finalwork-backend-1 python -m alembic upgrade head
```

マイグレーション成功の確認：

```bash
# 現在のマイグレーションリビジョン確認
docker exec finalwork-backend-1 python -m alembic current

# 期待される出力:
# 34b3d39281f3 (head)
```

### 5. データベーステーブル確認

```bash
# PostgreSQLに接続してテーブル一覧を表示
docker exec finalwork-db-1 psql -U fastapi_user -d commu_db -c "\dt"
```

期待される出力（全8テーブル + alembic_version）:

```
                   List of relations
 Schema |         Name          | Type  |    Owner
--------+-----------------------+-------+--------------
 public | alembic_version       | table | fastapi_user
 public | channels              | table | fastapi_user
 public | files                 | table | fastapi_user
 public | messages              | table | fastapi_user
 public | tags                  | table | fastapi_user
 public | user_tags             | table | fastapi_user
 public | users                 | table | fastapi_user
 public | wiki_page_permissions | table | fastapi_user
 public | wiki_pages            | table | fastapi_user
```

---

## 動作確認

### サービス状態確認

```bash
# 全サービスの状態確認
docker-compose ps
```

期待される出力：

```
NAME                   STATUS                    PORTS
finalwork-backend-1    Up (healthy)              0.0.0.0:8000->8000/tcp
finalwork-db-1         Up (healthy)              0.0.0.0:5432->5432/tcp
finalwork-frontend-1   Up                        0.0.0.0:3000->3000/tcp
```

### エンドポイント確認

#### 1. バックエンドAPI

```bash
# ヘルスチェック
curl http://localhost:8000/health

# 期待されるレスポンス:
# {"status":"healthy"}
```

#### 2. Swagger UI

ブラウザで以下にアクセス：

```
http://localhost:8000/docs
```

利用可能なエンドポイント：
- `POST /auth/signup` - ユーザー登録
- `POST /auth/token` - ログイン（JWT発行）
- `GET /users/me` - 現在のユーザー情報取得
- `GET /health` - ヘルスチェック

#### 3. フロントエンド

ブラウザで以下にアクセス：

```
http://localhost:3000
```

Next.jsのウェルカムページまたはログイン画面が表示されます。

### テスト実行

```bash
# pytest実行
docker exec finalwork-backend-1 python -m pytest test/test_api.py -v

# 期待される出力:
# test_root_endpoint PASSED              [ 25%]
# test_health_check_endpoint PASSED      [ 50%]
# test_openapi_spec PASSED               [ 75%]
# test_docs_available PASSED             [100%]
# 4 passed in 0.08s
```

---

## トラブルシューティング

### 問題1: コンテナが起動しない

**症状**
```
ERROR: Conflict. The container name "/finalwork-backend-1" is already in use
```

**解決方法**
```bash
# 既存のコンテナを停止・削除
make down
# または
docker-compose down

# 再起動
make up
```

### 問題2: ポートが既に使用されている

**症状**
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**解決方法**

使用中のポートを確認して解放：

```bash
# ポート使用状況確認（macOS/Linux）
lsof -i :8000
lsof -i :3000
lsof -i :5432

# プロセスを停止
kill <PID>
```

または、`docker-compose.yml` でポート番号を変更：

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # ホスト側を8001に変更
```

### 問題3: データベース接続エラー

**症状**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**解決方法**

1. データベースコンテナが起動しているか確認：

```bash
docker-compose ps db
```

2. データベースログを確認：

```bash
make logs-db
# または
docker-compose logs db
```

3. データベースコンテナを再起動：

```bash
docker-compose restart db
```

### 問題4: マイグレーションエラー

**症状**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**解決方法**

マイグレーション履歴をリセット：

```bash
# 現在のリビジョン確認
docker exec finalwork-backend-1 python -m alembic current

# マイグレーションを最新に更新
docker exec finalwork-backend-1 python -m alembic upgrade head

# それでも失敗する場合、データベースをリセット
docker-compose down -v  # ボリュームも削除
docker-compose up -d
make migrate-be
```

### 問題5: Dockerイメージビルドエラー

**症状**
```
ERROR: failed to solve: process "/bin/sh -c uv pip install . --system" did not complete successfully
```

**解決方法**

キャッシュをクリアして再ビルド：

```bash
# キャッシュなしでビルド
docker-compose build --no-cache

# または個別にビルド
docker-compose build --no-cache backend
```

---

## FAQ

### Q1: 開発時にコードを変更したら自動で反映される？

**A:** はい、ホットリロードが有効です。

- **バックエンド**: Uvicornが自動リロード（`--reload` オプション）
- **フロントエンド**: Next.jsが自動リロード

ただし、以下の場合は再ビルドが必要です：
- 依存関係を追加した場合（`pyproject.toml`, `package.json`）
- Dockerfileを変更した場合
- 環境変数を変更した場合

```bash
# 再ビルド
docker-compose up -d --build
```

### Q2: データベースのデータを永続化するには？

**A:** Docker Volumeが自動的に作成されます。

```bash
# ボリューム一覧確認
docker volume ls | grep finalwork

# データを含めて完全削除する場合のみ
docker-compose down -v
```

### Q3: 本番環境へのデプロイ方法は？

**A:** 以下の点に注意してください：

1. 環境変数を本番用に変更（特に `SECRET_KEY`）
2. `ENVIRONMENT=production` に設定
3. データベースは外部サービス（AWS RDS等）を推奨
4. HTTPS証明書の設定
5. CORSの設定を厳格化

詳細は `docs/operations.md` を参照してください。

### Q4: テストデータを投入するには？

**A:** 現在はSwagger UIから手動でデータ投入が可能です。

```bash
# Swagger UIにアクセス
open http://localhost:8000/docs

# POST /auth/signup でユーザー登録
# リクエストボディ例:
{
  "username": "testuser",
  "email": "test@example.com",
  "kategori": "学生",
  "gakuseki_bango": "B2024001",
  "faculty": "工学部",
  "password": "password123"
}
```

### Q5: ログをリアルタイムで確認するには？

**A:** 以下のコマンドを使用します：

```bash
# 全サービスのログ
make logs

# 特定のサービス
make logs-be   # バックエンド
make logs-fe   # フロントエンド
make logs-db   # データベース

# tail -f のように継続表示
docker-compose logs -f backend
```

### Q6: コンテナ内でシェルを開くには？

**A:** 以下のコマンドでシェルにアクセスできます：

```bash
# バックエンドコンテナ
make sh-be
# または
docker exec -it finalwork-backend-1 /bin/bash

# データベースコンテナ
make sh-db
# または
docker exec -it finalwork-db-1 /bin/bash

# PostgreSQLに直接接続
docker exec -it finalwork-db-1 psql -U fastapi_user -d commu_db
```

### Q7: 開発を中断して後で再開するには？

**A:**

```bash
# サービスを停止（データは保持）
make down
# または
docker-compose down

# 再開
make up
```

---

## 次のステップ

セットアップが完了したら、以下のドキュメントを参照してください：

- [システムアーキテクチャ](./architecture.md) - システム全体構成の理解
- [運用ガイド](./operations.md) - 日常的な運用タスク
- [テストガイド](./testing.md) - テストの実行と作成方法
- [データフロー図](./data-flow.md) - 認証フローの理解

---

**作成日**: 2025-11-09
**作成者**: worker3
**バージョン**: 1.0.0
