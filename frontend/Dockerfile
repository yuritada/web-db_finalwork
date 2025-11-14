# ベースイメージ
FROM node:20-slim

# 作業ディレクトリ
WORKDIR /app

# 'frontend/miscat' ディレクトリから package.json などをコピー
COPY miscat/package.json miscat/package-lock.json* ./

# 依存関係をインストール
RUN npm install

# 'frontend/miscat' の残りのファイルをコピー
COPY miscat/ .

# Next.jsが使用するポート
EXPOSE 3000

# 開発サーバー起動 (docker-compose.ymlで上書き可能)
CMD ["npm", "run", "dev"]