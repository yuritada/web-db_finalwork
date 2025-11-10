"""
FastAPI Application Main Entry Point (v3)
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import json
from datetime import datetime

from app.routers import auth, users, wiki, tags, search, channels, dm
from app.core.websocket import manager
from app.db.connect import get_session
from app.db.read import get_channel_by_id

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
app.include_router(channels.router)
app.include_router(dm.router)

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


# ===== WebSocketエンドポイント =====

@app.websocket("/ws/channel/{channel_id}")
async def websocket_channel_endpoint(
    websocket: WebSocket,
    channel_id: int,
    db: Session = Depends(get_session)
):
    """
    チャンネルのWebSocket接続エンドポイント

    v3仕様書: WS /ws/channel/{channel_id}

    **接続フロー:**
        1. クライアントが接続
        2. サーバーが接続を受け入れ、チャンネルに登録
        3. JOIN通知を全員にブロードキャスト
        4. クライアントからメッセージ受信時、チャンネル全員にブロードキャスト
        5. 切断時、LEAVE通知を全員にブロードキャスト

    **メッセージフォーマット（JSON）:**
        クライアント→サーバー:
        ```json
        {
            "type": "message",
            "content": "Hello!",
            "sender_username": "user123"
        }
        ```

        サーバー→クライアント:
        ```json
        {
            "type": "message",  // "message" | "system" | "error"
            "content": "Hello!",
            "sender_username": "user123",
            "timestamp": "2025-01-10T14:30:00"
        }
        ```

    **Args:**
        websocket: WebSocketインスタンス
        channel_id: チャンネルID
        db: データベースセッション

    **Raises:**
        WebSocketDisconnect: クライアントが切断した場合
    """
    # チャンネル存在チェック
    channel = get_channel_by_id(db, channel_id)
    if not channel:
        await websocket.close(code=1008, reason=f"Channel {channel_id} not found")
        return

    # 接続受け入れ
    await manager.connect(websocket, channel_id)

    try:
        # JOIN通知を全員に送信
        await manager.broadcast(channel_id, {
            "type": "system",
            "content": f"A user joined channel '{channel.name}'",
            "timestamp": datetime.utcnow().isoformat()
        })

        while True:
            # クライアントからメッセージ受信
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)

                # メッセージタイプチェック
                msg_type = message_data.get("type", "message")

                if msg_type == "message":
                    # 通常メッセージをブロードキャスト
                    await manager.broadcast(channel_id, {
                        "type": "message",
                        "content": message_data.get("content"),
                        "sender_username": message_data.get("sender_username"),
                        "timestamp": datetime.utcnow().isoformat()
                    })

                    # Note: DBへのメッセージ保存は、REST APIの
                    # POST /channels/{id}/messages を使用してください
                    # WebSocketは一時的なリアルタイム通信のみを担当

            except json.JSONDecodeError:
                # 不正なJSON
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "content": "Invalid JSON format"
                    },
                    websocket
                )

    except WebSocketDisconnect:
        # 切断処理
        manager.disconnect(websocket, channel_id)

        # LEAVE通知を全員に送信
        await manager.broadcast(channel_id, {
            "type": "system",
            "content": f"A user left channel '{channel.name}'",
            "timestamp": datetime.utcnow().isoformat()
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
