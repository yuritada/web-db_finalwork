# .PHONY に clean を追加
.PHONY: help up down clean logs logs-be logs-fe ps build restart migrate-be init setup sh-be sh-fe sh-db install-be install-fe

help:
	@echo "----------------------------------------------------"
	@echo " Makefile for Your Project (uv version) / プロジェクト用 Makefile（uv版）"
	@echo "----------------------------------------------------"
	@echo " up           - Start all services in detached mode / すべてのサービスをデタッチモードで起動"
	@echo " down         - Stop and remove all services / すべてのサービスを停止・削除"
	@echo " clean        - Remove containers, local images, volumes and networks created by compose / composeで作成されたコンテナ・ローカルイメージ・ボリューム・ネットワークを削除"
	@echo " setup        - Clean setup: up + migrate + init database / クリーンセットアップ: 起動+マイグレーション+DB初期化"
	@echo " logs         - View logs from all services / 全サービスのログを表示"
	@echo " logs-be      - View backend logs / バックエンドのログを表示"
	@echo " logs-fe      - View frontend logs / フロントエンドのログを表示"
	@echo " build        - Build or rebuild services / サービスをビルド／再ビルド"
	@echo " restart      - Restart all services / すべてのサービスを再起動"
	@echo " ps           - List running containers / 実行中のコンテナ一覧を表示"
	@echo " sh-be        - Enter backend container shell (/bin/sh) / バックエンドコンテナのシェルに入る (/bin/sh)"
	@echo " sh-fe        - Enter frontend container shell (/bin/sh) / フロントエンドコンテナのシェルに入る (/bin/sh)"
	@echo " sh-db        - Enter database container (psql) / データベースコンテナに接続（psql）"
	@echo " migrate-be   - Run backend DB migrations (e.g., alembic) / バックエンドのDBマイグレーションを実行（例: alembic）"
	@echo " init         - Initialize database with test data / データベースにテストデータを投入"
	@echo " install-be   - Install backend dependencies (uv pip install) / バックエンドの依存関係をインストール（uv pip install）"
	@echo " install-fe   - Install frontend dependencies (npm install) / フロントエンドの依存関係をインストール（npm install）"
	@echo "----------------------------------------------------"

up:
	docker compose up -d --build

down:
	docker compose down
	 
clean:
	docker compose down --volumes --rmi local --remove-orphans

logs:
	docker compose logs -f

logs-be:
	docker compose logs -f backend

logs-fe:
	docker compose logs -f frontend

build:
	docker compose build

restart: down up

ps:
	docker compose ps

# --- Service Specific Commands ---

sh-be:
	docker compose exec backend /bin/sh

sh-fe:
	docker compose exec frontend /bin/sh

sh-db:
	# .env ファイルから変数を読み込んでpsqlに接続 (awkで=の右側を取得)
	docker compose exec db psql -U $$(awk -F= '/^POSTGRES_USER=/{print $$2}' .env) -d $$(awk -F= '/^POSTGRES_DB=/{print $$2}' .env)
# 	docker compose exec db psql -U admin -d miscat_db

migrate-be:
	@echo "Running DB migrations (assuming alembic)..."
	docker compose exec backend alembic upgrade head

init:
	@echo "Initializing database with test data..."
	docker compose exec backend alembic upgrade head
	docker compose exec backend python scripts/init_db.py

setup: up
	@echo "Waiting for services to be ready..."
	@sleep 5
	@$(MAKE) migrate-be
	@$(MAKE) init
	@echo "----------------------------------------------------"
	@echo " Setup completed! / セットアップ完了！"
	@echo "----------------------------------------------------"
	@echo " Test credentials / テスト用認証情報:"
	@echo "   Username: student_test"
	@echo "   Password: password123"
	@echo "----------------------------------------------------"

install-be:
	@echo "Installing/Updating backend dependencies (with dev) using uv..."
	# エラーになる --group dev を ".[dev]" (extras構文) に修正
	docker compose exec backend uv pip install ".[dev]" --system --no-cache

install-fe:
	@echo "Installing/Updating frontend dependencies using npm..."
	docker compose exec frontend npm install