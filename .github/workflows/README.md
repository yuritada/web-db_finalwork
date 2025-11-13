# CI/CD ワークフロー

このディレクトリには、GitHub Actionsを使用したCI/CDワークフローの設定ファイルが含まれています。

## 概要

このプロジェクトでは、GitHub Actionsを使用して以下のCI/CDプロセスを自動化しています：

- ✅ **バックエンド統合テスト**: APIエンドポイントの自動テスト
- ✅ **フロントエンドビルド・テスト**: Next.jsアプリケーションのビルドとテスト
- 🚧 **デプロイ自動化**: 計画中

## 現在のワークフロー

### 1. Backend Integration Tests (`integration-test.yml`)

**トリガー**:
- `main`ブランチへのpush
- `develop`ブランチへのpush
- `main`または`develop`ブランチへのPull Request

**実行内容**:
1. PostgreSQL 15データベースを起動（GitHub Actions services）
2. Python 3.11環境をセットアップ
3. 依存パッケージをインストール（キャッシュ使用）
4. 環境変数を設定
5. Alembicマイグレーションを実行（セットアップされている場合）
6. バックエンドサーバーを起動（uvicorn）
7. 統合テストを実行（`backend/tests/integration_test.py`）
8. テスト結果をアップロード
9. Pull Request時は、テスト結果をコメント

**所要時間**: 約3-5分

**成功基準**: すべての統合テストがパス（成功率100%）

### 2. Frontend Build and Test (`frontend-build.yml`)

**トリガー**:
- `main`ブランチへのpush（`frontend/miscat/`配下の変更時のみ）
- `develop`ブランチへのpush（`frontend/miscat/`配下の変更時のみ）
- `main`または`develop`ブランチへのPull Request（`frontend/miscat/`配下の変更時のみ）

**実行内容**:
1. Node.js 18環境をセットアップ
2. npmキャッシュを使用して依存パッケージをインストール
3. ESLintを実行（コード品質チェック）
4. TypeScriptの型チェックを実行（`tsc --noEmit`）
5. テストを実行（テストスクリプトが存在する場合）
6. Next.jsアプリケーションをビルド
7. ビルド成果物をアーティファクトとしてアップロード
8. ビルドサイズレポートを生成
9. Pull Request時は、ビルド結果をコメント

**所要時間**: 約2-4分

**成功基準**: ビルドが成功し、型エラーがないこと

**最適化機能**:
- **Path Filter**: `frontend/miscat/`配下のファイル変更時のみ実行
- **npm cache**: 依存パッケージのキャッシュによる高速化
- **Build Size Report**: ビルドサイズの可視化

## ワークフローの使い分け

### Backend Integration Tests vs Frontend Build and Test

| 項目 | Backend Integration Tests | Frontend Build and Test |
|------|---------------------------|------------------------|
| **目的** | APIの動作確認 | フロントエンドのビルド確認 |
| **トリガー** | backend/配下の変更 | frontend/miscat/配下の変更 |
| **実行時間** | 3-5分 | 2-4分 |
| **依存関係** | PostgreSQL必須 | 依存関係なし（単独実行可能） |
| **テスト内容** | API統合テスト | lint、型チェック、ビルド |
| **成功基準** | 全テストパス | ビルド成功、型エラーなし |

### 並行実行の最適化

両方のワークフローは独立しており、以下のような並行実行が可能です：

```
フロントエンド変更のみ → Frontend Build and Test のみ実行
バックエンド変更のみ → Backend Integration Tests のみ実行
両方の変更 → 両ワークフローを並行実行
```

**効率**: 変更に応じて必要なワークフローのみが実行されるため、CI/CD時間とコストを最適化

## ワークフローの詳細

### integration-test.yml

#### 環境構成

| コンポーネント | 設定 | 説明 |
|--------------|------|------|
| OS | ubuntu-latest | GitHub Actions標準のUbuntu環境 |
| Python | 3.11 | バックエンドの実行環境 |
| PostgreSQL | 15-alpine | GitHub Actions services使用 |
| ポート | 5432（DB）、8000（API） | デフォルトポート |

#### 環境変数

以下の環境変数がワークフロー内で設定されます：

```bash
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=fastapi_password
POSTGRES_DB=commu_db
DATABASE_URL=postgresql+psycopg2://fastapi_user:fastapi_password@localhost:5432/commu_db
SECRET_KEY=test_secret_key_for_github_actions_ci_cd
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
BACKEND_URL=http://localhost:8000
```

#### ステップ詳細

1. **Checkout code**: リポジトリのコードをチェックアウト
2. **Set up Python**: Python 3.11をセットアップ
3. **Cache Python dependencies**: pipキャッシュを使用して高速化
4. **Install backend dependencies**: 必要なパッケージをインストール
5. **Set up environment variables**: .envファイルを作成
6. **Run Alembic migrations**: DBマイグレーションを実行
7. **Start backend server**: バックエンドを起動し、ヘルスチェックで確認
8. **Run integration tests**: 統合テストを実行
9. **Stop backend server**: テスト後にサーバーを停止
10. **Upload test results**: テスト結果をアーティファクトとして保存
11. **Comment test results on PR**: PRにテスト結果をコメント

#### 失敗時の挙動

- テスト失敗時は、ワークフローが失敗ステータスになります（exit code 1）
- PRのマージがブロックされます（ブランチ保護ルールが設定されている場合）
- テスト結果のログがアーティファクトとして保存されます（7日間）

### frontend-build.yml

#### 環境構成

| コンポーネント | 設定 | 説明 |
|--------------|------|------|
| OS | ubuntu-latest | GitHub Actions標準のUbuntu環境 |
| Node.js | 18 | フロントエンドの実行環境 |
| Next.js | 16.0.1 | フロントエンドフレームワーク |
| パッケージマネージャー | npm | 依存パッケージの管理 |

#### ステップ詳細

1. **Checkout code**: リポジトリのコードをチェックアウト
2. **Set up Node.js**: Node.js 18をセットアップし、npmキャッシュを有効化
3. **Install dependencies**: `npm ci`で依存パッケージを正確にインストール
4. **Run ESLint**: コード品質チェック（エラー時も継続）
5. **Run type check**: TypeScript型チェック（`tsc --noEmit`）
6. **Run tests**: テストスクリプトが存在する場合のみ実行
7. **Build Next.js application**: `next build`でプロダクションビルド
8. **Upload build artifacts**: `.next/`と`out/`をアーティファクトとして保存
9. **Check build size**: ビルドサイズレポートを生成
10. **Comment build results on PR**: PRにビルド結果をコメント

#### 環境変数

以下の環境変数がビルド時に設定されます：

```bash
NEXT_PUBLIC_API_URL_SERVER=http://backend:8000
NEXT_PUBLIC_API_URL_CLIENT=/api
```

**注意**: 本番環境では、これらの環境変数を適切な値に設定してください。

#### 失敗時の挙動

- ビルド失敗時は、ワークフローが失敗ステータスになります（exit code 1）
- 型チェックエラー時も失敗します
- ESLintエラーは警告のみ（`continue-on-error: true`）
- PRのマージがブロックされます（ブランチ保護ルールが設定されている場合）
- ビルド成果物のログがアーティファクトとして保存されます（7日間）

## ローカルでの動作確認

### 方法1: actを使用したローカル実行

[act](https://github.com/nektos/act)を使用すると、GitHub Actionsをローカルで実行できます。

#### インストール

```bash
# macOS
brew install act

# Linux
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Windows (Chocolatey)
choco install act-cli
```

#### 実行

```bash
# integration-testワークフローを実行
act -W .github/workflows/integration-test.yml

# 特定のジョブを実行
act -j integration-test

# プルリクエストイベントをシミュレート
act pull_request
```

**注意**: actはDocker環境が必要です。

### 方法2: 手動での動作確認

ローカル環境で同等のステップを実行して確認：

```bash
# 1. PostgreSQLを起動（Docker）
docker run -d --name postgres-test \
  -e POSTGRES_USER=fastapi_user \
  -e POSTGRES_PASSWORD=fastapi_password \
  -e POSTGRES_DB=commu_db \
  -p 5432:5432 \
  postgres:15-alpine

# 2. 環境変数を設定
cd backend
cat > .env << EOF
POSTGRES_USER=fastapi_user
POSTGRES_PASSWORD=fastapi_password
POSTGRES_DB=commu_db
DATABASE_URL=postgresql+psycopg2://fastapi_user:fastapi_password@localhost:5432/commu_db
SECRET_KEY=test_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
EOF

# 3. 依存パッケージをインストール
pip install -r requirements.txt

# 4. マイグレーションを実行
alembic upgrade head

# 5. バックエンドを起動
uvicorn main:app --host 0.0.0.0 --port 8000 &

# 6. 統合テストを実行
cd tests
python3 integration_test.py

# 7. クリーンアップ
kill $(jobs -p)
docker stop postgres-test
docker rm postgres-test
```

## トラブルシューティング

### ワークフローが失敗する

#### 1. データベース接続エラー

**症状**: `FATAL: password authentication failed for user "fastapi_user"`

**原因**: 環境変数の設定ミス

**解決策**:
- `.github/workflows/integration-test.yml`の環境変数を確認
- PostgreSQL servicesの設定を確認

#### 2. バックエンドの起動失敗

**症状**: `Failed to start backend server`

**原因**: 依存パッケージのインストール失敗、またはポート競合

**解決策**:
```yaml
# requirements.txtが存在しない場合の対応を追加
- name: Install backend dependencies
  run: |
    cd backend
    pip install --upgrade pip
    if [ -f "requirements.txt" ]; then
      pip install -r requirements.txt
    else
      pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-jose passlib bcrypt requests
    fi
```

#### 3. 統合テストの失敗

**症状**: テストケースが失敗する

**原因**: API実装の変更、データベーススキーマの不一致

**解決策**:
1. ローカルでテストを実行して確認
2. Alembicマイグレーションが正しく実行されているか確認
3. `backend/tests/integration_test.py`を更新

### キャッシュの問題

**症状**: 依存パッケージのインストールが遅い

**解決策**:
- キャッシュキーを変更して強制的に再キャッシュ:
  ```yaml
  key: ${{ runner.os }}-pip-v2-${{ hashFiles('backend/pyproject.toml') }}
  ```

## 今後の拡張案

### 1. フロントエンドビルド・テストワークフロー

**ファイル**: `frontend-build-test.yml`

**内容**:
```yaml
name: Frontend Build and Test

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  build-test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/miscat/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend/miscat
          npm ci

      - name: Run linter
        run: |
          cd frontend/miscat
          npm run lint

      - name: Run type check
        run: |
          cd frontend/miscat
          npm run type-check || npx tsc --noEmit

      - name: Run tests
        run: |
          cd frontend/miscat
          npm test

      - name: Build
        run: |
          cd frontend/miscat
          npm run build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: frontend-build
          path: frontend/miscat/.next/
```

**推定工数**: 1h

### 2. コードカバレッジレポート

**内容**:
- Pythonの`coverage`パッケージを使用
- カバレッジレポートをPRにコメント
- Codecovまたは Coveralls と統合

**推定工数**: 1.5h

### 3. デプロイ自動化ワークフロー

**ファイル**: `deploy-production.yml`

**内容**:
```yaml
name: Deploy to Production

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker images
        run: |
          docker-compose build

      - name: Push to registry
        run: |
          # Docker Hub or GitHub Container Registry
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker-compose push

      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.DEPLOY_HOST }}
          username: ${{ secrets.DEPLOY_USER }}
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            cd /path/to/app
            docker-compose pull
            docker-compose up -d
```

**推定工数**: 2h

### 4. セキュリティスキャン

**内容**:
- Dependabotによる依存パッケージの脆弱性スキャン
- CodeQLによるコード品質・セキュリティ分析
- SAST（Static Application Security Testing）

**推定工数**: 1h

### 5. パフォーマンステスト

**内容**:
- APIのレスポンスタイム測定
- 負荷テスト（Locust等）
- ベンチマーク結果の可視化

**推定工数**: 3h

## README.mdへのバッジ追加案

プロジェクトルートの`README.md`に以下のバッジを追加することを推奨します：

```markdown
# 大学向けコミュニケーションツール

[![Backend Integration Tests](https://github.com/{username}/{repo}/actions/workflows/integration-test.yml/badge.svg)](https://github.com/{username}/{repo}/actions/workflows/integration-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192.svg)](https://www.postgresql.org/)

...（既存の内容）
```

**注意**: `{username}`と`{repo}`を実際のGitHubユーザー名とリポジトリ名に置き換えてください。

## 関連ドキュメント

- **統合テストドキュメント**: `backend/tests/README.md`
- **バックエンドアーキテクチャ**: `backend/docs/backend-architecture.md`
- **デプロイメントガイド**: `backend/docs/deployment.md`
- **GitHub Actions公式ドキュメント**: https://docs.github.com/en/actions

---

**作成日**: 2025-11-13
**作成者**: Worker3 (インフラ・統合担当)
**バージョン**: 1.0
