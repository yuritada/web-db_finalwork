# Miscat デプロイメントガイド

**最終更新**: 2025-11-14
**バージョン**: 1.0
**対象環境**: 本番環境・ステージング環境

---

## 📋 目次

1. [前提条件](#前提条件)
2. [環境変数設定](#環境変数設定)
3. [Docker Composeを使った起動](#docker-composeを使った起動)
4. [データベースマイグレーション](#データベースマイグレーション)
5. [本番環境へのデプロイ](#本番環境へのデプロイ)
6. [トラブルシューティング](#トラブルシューティング)
7. [メンテナンス](#メンテナンス)

---

## 前提条件

### 必須ソフトウェア

- **Docker**: 20.10.0 以上
- **Docker Compose**: 2.0.0 以上
- **Git**: 2.30.0 以上

### 推奨環境

- **OS**: Ubuntu 20.04 LTS / Ubuntu 22.04 LTS / macOS 12以降
- **CPU**: 2コア以上
- **メモリ**: 4GB以上
- **ディスク**: 20GB以上の空き容量

### ポート要件

以下のポートが利用可能であることを確認してください：

- `3000`: フロントエンド（Next.js）
- `8000`: バックエンド（FastAPI）
- `5432`: データベース（PostgreSQL）

---

## 環境変数設定

### 1. 環境変数ファイルの作成

プロジェクトルートに `.env` ファイルを作成します。

```bash
# プロジェクトルートで実行
cp .env.example .env
```

`.env.example` が存在しない場合は、以下のテンプレートを使用してください。

### 2. 環境変数テンプレート

#### `.env` (プロジェクトルート)

```bash
# PostgreSQL データベース設定
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=miscat_db

# データベース接続URL（バックエンド用）
DATABASE_URL=postgresql://postgres:your_secure_password_here@db:5432/miscat_db

# JWT認証用のシークレットキー
SECRET_KEY=your_very_long_and_random_secret_key_here_at_least_32_characters

# 環境識別
ENVIRONMENT=production
```

#### `backend/.env` (バックエンド固有)

```bash
# データベース接続URL
DATABASE_URL=postgresql://postgres:your_secure_password_here@db:5432/miscat_db

# JWT認証用のシークレットキー
SECRET_KEY=your_very_long_and_random_secret_key_here_at_least_32_characters

# CORS設定（本番環境では特定のオリジンのみ許可）
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# ログレベル
LOG_LEVEL=INFO
```

### 3. シークレットキーの生成

**重要**: 本番環境では必ず強力なシークレットキーを生成してください。

```bash
# Pythonを使用して生成
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# または openssl を使用
openssl rand -base64 32
```

生成されたキーを `.env` ファイルの `SECRET_KEY` に設定します。

### 4. 環境変数の検証

環境変数が正しく設定されているか確認します：

```bash
# .envファイルの存在確認
ls -la .env backend/.env

# 環境変数の読み込みテスト（Docker Compose）
docker-compose config
```

---

## Docker Composeを使った起動

### 1. 基本的な起動手順

#### 開発環境での起動

```bash
# プロジェクトルートで実行
cd /path/to/finalwork

# すべてのサービスをビルドして起動
docker-compose up --build

# バックグラウンドで起動
docker-compose up -d --build
```

#### 本番環境での起動

```bash
# 本番用のDockerイメージをビルド
docker-compose -f docker-compose.prod.yml build

# 本番環境で起動
docker-compose -f docker-compose.prod.yml up -d
```

### 2. 各サービスの起動確認

```bash
# コンテナの状態確認
docker-compose ps

# ログの確認
docker-compose logs -f

# 特定のサービスのログのみ確認
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### 3. ヘルスチェック

各サービスが正常に起動しているか確認します：

```bash
# バックエンドヘルスチェック
curl http://localhost:8000/health

# フロントエンドヘルスチェック
curl http://localhost:3000

# データベース接続確認
docker exec finalwork-db-1 pg_isready -U postgres -d miscat_db
```

**期待される出力**:
- バックエンド: `{"status":"ok"}`
- フロントエンド: HTMLレスポンス
- データベース: `accepting connections`

---

## データベースマイグレーション

### 1. Alembicによるマイグレーション

#### 初回セットアップ

```bash
# バックエンドコンテナに入る
docker exec -it finalwork-backend-1 bash

# マイグレーション履歴の確認
alembic history

# 最新バージョンにマイグレーション
alembic upgrade head
```

#### マイグレーションの作成（開発時）

```bash
# バックエンドコンテナ内で実行
alembic revision --autogenerate -m "Add new table or column"

# 生成されたマイグレーションファイルを確認
ls backend/alembic/versions/

# マイグレーションを適用
alembic upgrade head
```

#### マイグレーションのロールバック

```bash
# 1つ前のバージョンに戻す
alembic downgrade -1

# 特定のバージョンに戻す
alembic downgrade <revision_id>

# すべてのマイグレーションを取り消す
alembic downgrade base
```

### 2. 手動でのデータベース初期化

```bash
# データベースコンテナに入る
docker exec -it finalwork-db-1 psql -U postgres -d miscat_db

# テーブル一覧確認
\dt

# ユーザーテーブルの確認
SELECT * FROM users LIMIT 5;

# 終了
\q
```

### 3. データベースバックアップ

#### バックアップの作成

```bash
# SQLダンプファイルを作成
docker exec finalwork-db-1 pg_dump -U postgres miscat_db > backup_$(date +%Y%m%d_%H%M%S).sql

# カスタムフォーマットでバックアップ（推奨）
docker exec finalwork-db-1 pg_dump -U postgres -Fc miscat_db > backup_$(date +%Y%m%d_%H%M%S).dump
```

#### バックアップからの復元

```bash
# SQLファイルから復元
cat backup_20251114_120000.sql | docker exec -i finalwork-db-1 psql -U postgres -d miscat_db

# カスタムフォーマットから復元
docker exec -i finalwork-db-1 pg_restore -U postgres -d miscat_db -c < backup_20251114_120000.dump
```

---

## 本番環境へのデプロイ

### 1. VPS・クラウドサーバーへのデプロイ

#### サーバー準備

```bash
# サーバーにSSH接続
ssh user@your-server.com

# 必要なパッケージのインストール
sudo apt update
sudo apt install -y docker.io docker-compose git

# Dockerの起動と自動起動設定
sudo systemctl start docker
sudo systemctl enable docker

# 現在のユーザーをdockerグループに追加
sudo usermod -aG docker $USER
```

#### リポジトリのクローン

```bash
# プロジェクトをクローン
git clone https://github.com/yourusername/miscat.git
cd miscat

# 本番用ブランチに切り替え（存在する場合）
git checkout production
```

#### 環境変数設定

```bash
# .envファイルを作成
nano .env

# 環境変数を設定（上記テンプレート参照）
# 本番環境では強力なパスワードとシークレットキーを使用
```

#### Docker Composeでデプロイ

```bash
# イメージをビルド
docker-compose build --no-cache

# サービスを起動
docker-compose up -d

# ログを確認
docker-compose logs -f
```

### 2. Nginx リバースプロキシの設定（推奨）

#### Nginxのインストール

```bash
sudo apt install -y nginx
```

#### Nginx設定ファイル

`/etc/nginx/sites-available/miscat` を作成：

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # フロントエンド
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # バックエンドAPI
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket (将来的な拡張用)
    location /ws/ {
        proxy_pass http://localhost:8000/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### Nginxの有効化

```bash
# シンボリックリンクを作成
sudo ln -s /etc/nginx/sites-available/miscat /etc/nginx/sites-enabled/

# デフォルト設定を無効化
sudo rm /etc/nginx/sites-enabled/default

# 設定ファイルのテスト
sudo nginx -t

# Nginxを再起動
sudo systemctl restart nginx
```

### 3. SSL/TLS証明書の設定（Let's Encrypt）

```bash
# Certbotのインストール
sudo apt install -y certbot python3-certbot-nginx

# SSL証明書を取得
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 証明書の自動更新設定
sudo certbot renew --dry-run
```

### 4. 自動起動の設定

```bash
# Docker Composeサービスの自動起動
# docker-compose.ymlで `restart: unless-stopped` が設定されていることを確認

# システム再起動時の確認
sudo reboot

# 再起動後、サービスの状態を確認
docker-compose ps
```

---

## トラブルシューティング

### 1. データベース接続エラー

#### 問題: `could not connect to server: Connection refused`

**原因**: データベースコンテナが起動していない、またはネットワーク設定が不正

**解決策**:

```bash
# データベースコンテナの状態確認
docker-compose ps db

# データベースログを確認
docker-compose logs db

# データベースコンテナを再起動
docker-compose restart db

# ヘルスチェック
docker exec finalwork-db-1 pg_isready -U postgres
```

### 2. バックエンドが起動しない

#### 問題: `ModuleNotFoundError` または依存関係エラー

**原因**: Pythonパッケージが正しくインストールされていない

**解決策**:

```bash
# バックエンドコンテナを再ビルド
docker-compose build --no-cache backend

# コンテナ内で依存関係を確認
docker exec -it finalwork-backend-1 bash
pip list

# 手動でパッケージをインストール（必要な場合）
pip install -r requirements.txt
```

### 3. フロントエンドが起動しない

#### 問題: `npm install` エラーまたはビルドエラー

**原因**: node_modulesの不整合、またはメモリ不足

**解決策**:

```bash
# フロントエンドコンテナを再ビルド
docker-compose build --no-cache frontend

# node_modulesを削除して再インストール
docker-compose run --rm frontend rm -rf node_modules
docker-compose run --rm frontend npm install

# メモリ制限を増やす（docker-compose.yml）
# deploy:
#   resources:
#     limits:
#       memory: 2G
```

### 4. ポートが既に使用されている

#### 問題: `Bind for 0.0.0.0:3000 failed: port is already allocated`

**原因**: 指定されたポートが他のプロセスで使用されている

**解決策**:

```bash
# ポートを使用しているプロセスを確認
sudo lsof -i :3000
sudo lsof -i :8000
sudo lsof -i :5432

# プロセスを停止
sudo kill -9 <PID>

# または、docker-compose.ymlでポートを変更
ports:
  - "3001:3000"  # 3000 -> 3001に変更
```

### 5. マイグレーションエラー

#### 問題: `alembic.util.exc.CommandError: Can't locate revision identified by`

**原因**: マイグレーション履歴の不整合

**解決策**:

```bash
# マイグレーション履歴を確認
docker exec -it finalwork-backend-1 alembic history

# データベースの現在のバージョンを確認
docker exec -it finalwork-backend-1 alembic current

# マイグレーションを強制的にリセット（開発環境のみ）
docker exec -it finalwork-backend-1 alembic stamp head
```

### 6. 権限エラー（Permission Denied）

#### 問題: ファイルやディレクトリへのアクセス権限エラー

**原因**: Dockerコンテナ内のユーザーとホストユーザーの権限不一致

**解決策**:

```bash
# ホスト側で権限を修正
sudo chown -R $USER:$USER backend/ frontend/

# Dockerfileでユーザー権限を設定（推奨）
# USER node  # Node.jsの場合
# USER www-data  # Pythonの場合
```

---

## メンテナンス

### 1. ログ管理

#### ログの確認

```bash
# すべてのサービスのログ
docker-compose logs -f

# 最新100行のみ表示
docker-compose logs --tail=100

# 特定の時間以降のログ
docker-compose logs --since 2025-11-14T10:00:00
```

#### ログのローテーション

```bash
# Dockerのログローテーション設定（/etc/docker/daemon.json）
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# Dockerを再起動して設定を適用
sudo systemctl restart docker
```

### 2. データベースメンテナンス

#### VACUUM（不要なデータの削除）

```bash
docker exec -it finalwork-db-1 psql -U postgres -d miscat_db -c "VACUUM FULL;"
```

#### インデックスの再構築

```bash
docker exec -it finalwork-db-1 psql -U postgres -d miscat_db -c "REINDEX DATABASE miscat_db;"
```

### 3. コンテナの更新

#### イメージの更新

```bash
# 最新のコードを取得
git pull origin main

# イメージを再ビルド
docker-compose build --no-cache

# サービスを再起動
docker-compose up -d
```

#### 不要なイメージの削除

```bash
# 使用されていないイメージを削除
docker image prune -a

# 使用されていないボリュームを削除（注意！）
docker volume prune
```

### 4. モニタリング

#### リソース使用状況の確認

```bash
# コンテナのリソース使用状況
docker stats

# ディスク使用状況
df -h
docker system df
```

#### パフォーマンス監視（推奨ツール）

- **Prometheus + Grafana**: メトリクス収集と可視化
- **ELK Stack**: ログ集約と分析
- **Datadog / New Relic**: APM（Application Performance Monitoring）

---

## セキュリティベストプラクティス

### 1. 環境変数の保護

```bash
# .envファイルの権限を制限
chmod 600 .env backend/.env

# .envファイルをGitにコミットしない（.gitignoreで除外）
echo ".env" >> .gitignore
```

### 2. ファイアウォール設定

```bash
# UFWのインストール（Ubuntu）
sudo apt install -y ufw

# 必要なポートのみ許可
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# ファイアウォールを有効化
sudo ufw enable
```

### 3. 定期的な更新

```bash
# システムパッケージの更新
sudo apt update && sudo apt upgrade -y

# Dockerイメージの更新
docker-compose pull
docker-compose up -d
```

---

## まとめ

このデプロイメントガイドに従うことで、Miscatアプリケーションを安全かつ効率的に本番環境にデプロイできます。

### 重要なチェックリスト

- [ ] 強力なパスワードとシークレットキーを設定
- [ ] SSL/TLS証明書を設定
- [ ] データベースバックアップを定期的に実行
- [ ] ログローテーションを設定
- [ ] ファイアウォールを設定
- [ ] モニタリングツールを導入

### サポート

問題が発生した場合は、以下を確認してください：

1. [トラブルシューティング](#トラブルシューティング)セクション
2. プロジェクトのGitHub Issuesページ
3. Docker公式ドキュメント: https://docs.docker.com/

---

**作成者**: worker3 (インフラ・ドキュメント担当)
**最終更新日**: 2025-11-14
