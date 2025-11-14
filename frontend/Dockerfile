# 1. Builder Stage
FROM node:20-slim AS builder 
WORKDIR /app

# 修正: package.json と Tailwind/PostCSS の設定ファイルのみを先にコピー
# (package-lock.json をコピーしないことで、Linux環境用の依存関係を強制インストール)
COPY miscat/package.json ./
COPY miscat/postcss.config.mjs ./
# (↑もし tailwind.config.ts が存在しない場合は、この行は削除しても構いません)

# 修正: Render(Linux)環境で依存関係をクリーンインストール
RUN npm install

# 修正: 残りのすべてのアプリケーションコードをコピー
COPY miscat/ .

# ビルドを実行
RUN npm run build

# 2. Production Stage
FROM node:20-slim AS production 
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]