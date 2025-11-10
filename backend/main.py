"""
FastAPI Application Main Entry Point (v3)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, users, wiki, tags, search

app = FastAPI(
    title="大学向けコミュニケーションツール API",
    description="v3 仕様書に基づくバックエンドAPI",
    version="3.0.0"
)

# CORS設定（フロントエンドとの通信を許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js開発サーバー
        "http://frontend:3000",   # Dockerコンテナ名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターの登録
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(wiki.router)
app.include_router(tags.router)
app.include_router(search.router)

@app.get("/")
def root():
    """ルートエンドポイント"""
    return {
        "message": "大学向けコミュニケーションツール API v3",
        "docs": "/docs",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
