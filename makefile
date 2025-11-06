.PHONY: help up down logs logs-be logs-fe ps build restart migrate-be sh-be sh-fe sh-db install-be install-fe

help:
	@echo "----------------------------------------------------"
	@echo " Makefile for Your Project (uv version) / プロジェクト用 Makefile（uv版）"
	@echo "----------------------------------------------------"
	@echo " up           - Start all services in detached mode / すべてのサービスをデタッチモードで起動"
	@echo " down         - Stop and remove all services / すべてのサービスを停止・削除"
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
	@echo " install-be   - Install backend dependencies (uv pip install) / バックエンドの依存関係をインストール（uv pip install）"
	@echo " install-fe   - Install frontend dependencies (npm install) / フロントエンドの依存関係をインストール（npm install）"
	@echo "----------------------------------------------------"

up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-be:
	docker-compose logs -f backend

logs-fe:
	docker-compose logs -f frontend

build:
	docker-compose build

restart: down up

ps:
	docker-compose ps

# --- Service Specific Commands ---

sh-be:
	docker-compose exec backend /bin/sh

sh-fe:
	docker-compose exec frontend /bin/sh

sh-db:
	# .env ファイルから変数を読み込んでpsqlに接続 (awkで=の右側を取得)
	docker-compose exec db psql -U $$(awk -F= '/^POSTGRES_USER=/{print $2}' .env) -d $$(awk -F= '/^POSTGRES_DB=/{print $2}' .env)

migrate-be:
	@echo "Running DB migrations (assuming alembic)..."
	# poetry run を削除し、直接 alembic を実行
	docker-compose exec backend alembic upgrade head

install-be:
	# uv pip install に変更。--group dev を追加して開発用依存もインストール
	@echo "Installing/Updating backend dependencies (with dev) using uv..."
	docker-compose exec backend uv pip install . --system --no-cache --group dev

install-fe:
	@echo "Installing/Updating frontend dependencies using npm..."
	docker-compose exec frontend npm install