# 1. Builder Stage
# alpine (musl) から slim (glibc) に変更
FROM node:20-slim AS builder 
WORKDIR /app

# 修正: 'frontend/miscat' -> 'miscat'
COPY miscat/package.json miscat/package-lock.json* ./
RUN npm install

# 修正: 'frontend/miscat' -> 'miscat'
COPY miscat/ .
RUN npm run build

# 2. Production Stage
# alpine (musl) から slim (glibc) に変更
FROM node:20-slim AS production 
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]