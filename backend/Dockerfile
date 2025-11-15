# ベースイメージ (Python 3.12)
FROM python:3.12-slim

# 環境変数
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# uv をインストール
# ベースイメージに pip が含まれているため、pip を使って uv をインストール
RUN pip install uv

# 作業ディレクトリ
WORKDIR /app

# 依存関係ファイルのみコピー
# uv は pyproject.toml と poetry.lock を読み取ることができます
COPY pyproject.toml poetry.lock* ./

# 依存関係をインストール
# --system: 仮想環境を作らず、コンテナのシステムPythonに直接インストール
# --no-dev は不要 (uv pip install . はデフォルトで dev 依存を除外するため)
RUN uv pip install . --system --no-cache

# プロジェクトのソースコードをコピー
COPY . .

# FastAPIサーバー起動コマンド
# サーバー起動前にAlembicマイグレーションを実行し、その後Uvicornを起動する
# docker-compose.yml と同様に、マイグレーション、DB初期化、シード投入を実行してからサーバーを起動する
CMD ["sh", "-c", "alembic upgrade head && python -m scripts.init_db && python -m scripts.seed_users && uvicorn main:app --host 0.0.0.0 --port 8000"]