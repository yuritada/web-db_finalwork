# 1. Builder Stage
FROM node:20-slim AS builder 
WORKDIR /app

# 修正: 先にすべてのファイルをコピーします
COPY miscat/ .

# 修正: 関連ファイルがすべて揃った状態で install を実行します
RUN npm install

# ビルドを実行します
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