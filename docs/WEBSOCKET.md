# WebSocketリアルタイムメッセージング実装ドキュメント

## 📋 概要

このドキュメントは、チャンネルとDMでのWebSocketリアルタイムメッセージング機能の実装について説明します。

## 🏗️ アーキテクチャ

### バックエンド構成

```
backend/app/
├── websocket/
│   ├── __init__.py
│   └── connection_manager.py  # WebSocket接続管理
├── routers/
│   └── websocket.py           # WebSocketエンドポイント
├── auth/
│   └── dependencies.py        # WebSocket認証
└── main.py                     # WebSocketルーター登録
```

### フロントエンド構成

```
frontend/miscat/
├── hooks/
│   └── useWebSocket.ts        # WebSocketカスタムフック
└── app/(main)/
    ├── channels/[channel_id]/page.tsx  # チャンネルページ（WebSocket統合済み）
    └── dm/[dm_id]/page.tsx             # DMページ（WebSocket統合済み）
```

## 🔌 WebSocketエンドポイント

### チャンネル用WebSocket

**エンドポイント**: `ws://localhost:8000/ws/channels/{channel_id}?token={jwt_token}`

**接続フロー**:
1. クライアントがトークン付きで接続
2. サーバーがトークンを検証
3. 接続成功メッセージを送信
4. メッセージの受信・ブロードキャストを開始

**メッセージフォーマット**:

```typescript
// クライアント → サーバー
{
  "type": "ping" | "message",
  "message"?: {
    "id": number,
    "content": string,
    "sender_id": string,
    "sender_username": string,
    "created_at": string
  }
}

// サーバー → クライアント
{
  "type": "connection" | "new_message" | "pong" | "error",
  "status"?: "connected",
  "channel_id"?: number,
  "user_id"?: string,
  "username"?: string,
  "message"?: Message
}
```

### DM用WebSocket

**エンドポイント**: `ws://localhost:8000/ws/dm/{partner_id}?token={jwt_token}`

**接続フロー**: チャンネルと同様

**メッセージフォーマット**: チャンネルと同様（`channel_id`の代わりに`partner_id`を使用）

## 💻 実装詳細

### バックエンド: ConnectionManager

`backend/app/websocket/connection_manager.py`

**主要機能**:
- チャンネル/DMごとの接続管理
- 接続の追加・削除
- メッセージのブロードキャスト
- 切断された接続の自動クリーンアップ

**重要メソッド**:

```python
class ConnectionManager:
    async def connect_to_channel(websocket, channel_id, user_id)
    async def connect_to_dm(websocket, user_id1, user_id2)
    def disconnect_from_channel(channel_id, user_id)
    def disconnect_from_dm(user_id1, user_id2)
    async def broadcast_to_channel(channel_id, message)
    async def broadcast_to_dm(user_id1, user_id2, message)
```

### バックエンド: WebSocket認証

`backend/app/auth/dependencies.py`

**認証フロー**:
1. クエリパラメータから`token`を取得
2. JWTトークンをデコード
3. ユーザー情報を検証
4. 認証失敗時は接続を拒否（code 1008）

```python
async def get_current_user_ws(token: str, db: Session) -> Optional[User]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user = get_user_by_username(db, username)
        return user
    except JWTError:
        return None
```

### フロントエンド: useWebSocketフック

`frontend/miscat/hooks/useWebSocket.ts`

**主要機能**:
- WebSocket接続の確立・管理
- 自動再接続（最大5回、3秒間隔）
- Ping/Pong（30秒間隔で接続維持）
- メッセージ送受信
- 接続状態の管理

**使用例**:

```typescript
const { isConnected, lastMessage, sendMessage, disconnect, reconnect } = useWebSocket(
  wsUrl,
  {
    onMessage: (message) => {
      // メッセージ受信時の処理
    },
    onConnect: () => {
      // 接続成功時の処理
    },
    onDisconnect: () => {
      // 切断時の処理
    },
    onError: (error) => {
      // エラー発生時の処理
    }
  }
);
```

### フロントエンド: チャンネル/DMページ統合

**主要実装ポイント**:

1. **WebSocket URL構築**:
```typescript
const wsBaseUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
const wsUrl = user ? `${wsBaseUrl}/ws/channels/${channelId}` : null;
```

2. **メッセージ受信時の重複チェック**:
```typescript
const isDuplicate = prevMessages.some(
  m => m.id === message.message.id ||
  (m.content === message.message.content &&
   m.sender_id === message.message.sender_id &&
   Math.abs(new Date(m.created_at).getTime() - new Date(message.message.created_at).getTime()) < 1000)
);
```

3. **メッセージ送信（楽観的更新）**:
```typescript
// HTTP APIでメッセージを保存
const newMessage = await sendChannelMessage(channelId, { content });

// メッセージリストに即座に追加
setMessages([...messages, newMessage]);

// WebSocketで他の接続にブロードキャスト
if (isConnected) {
  wsSendMessage({
    type: 'message',
    message: newMessage
  });
}
```

4. **接続状態インジケーター**:
```tsx
<div className="flex items-center gap-1.5">
  {isConnected ? (
    <>
      <Wifi className="h-4 w-4 text-green-500" />
      <span className="text-xs text-green-600">リアルタイム</span>
    </>
  ) : (
    <>
      <WifiOff className="h-4 w-4 text-gray-400" />
      <span className="text-xs text-gray-500">オフライン</span>
    </>
  )}
</div>
```

## 🔐 セキュリティ

### 認証

- **JWT認証**: すべてのWebSocket接続でJWTトークンを検証
- **トークン検証失敗時**: 接続を即座に拒否（code 1008）

### 接続管理

- **ユーザーごとの接続制限**: 同一ユーザーが同じチャンネル/DMに複数接続した場合、古い接続を自動切断
- **タイムアウト処理**: 切断された接続を自動クリーンアップ

## 📊 パフォーマンス

### 最適化ポイント

1. **重複メッセージの防止**: フロントエンドで重複チェックを実装
2. **楽観的更新**: メッセージ送信時に即座にUIを更新
3. **自動再接続**: ネットワーク断絶時も自動的に復旧
4. **Ping/Pong**: 定期的なPingで接続を維持

### スケーラビリティ

- **チャンネル/DMごとの分離**: 各チャンネル/DMで独立した接続プールを管理
- **効率的なブロードキャスト**: 必要な接続にのみメッセージを送信

## 🧪 テスト方法

### 手動テスト

1. **2つのブラウザウィンドウを開く**
   - ウィンドウ1: student_testでログイン
   - ウィンドウ2: professor_testでログイン

2. **同じチャンネルに参加**
   - 両方のウィンドウで同じチャンネルを開く
   - 接続状態インジケーターが「リアルタイム」になることを確認

3. **メッセージ送信**
   - ウィンドウ1からメッセージを送信
   - ウィンドウ2にリアルタイムで表示されることを確認

4. **DM機能**
   - ウィンドウ1からウィンドウ2のユーザーにDMを送信
   - 両方のウィンドウでリアルタイム更新を確認

### デバッグ

**ブラウザコンソールで確認**:
```javascript
// WebSocket接続状態
console.log('WebSocket connected to channel:', channelId);

// メッセージ受信
console.log('Received message:', message);

// エラー
console.error('WebSocket error:', error);
```

**バックエンドログで確認**:
```bash
docker compose logs backend -f | grep WebSocket
```

## 🐛 トラブルシューティング

### 接続できない

**問題**: WebSocketが接続できない

**確認ポイント**:
1. トークンが正しく送信されているか
2. `NEXT_PUBLIC_WS_URL`環境変数が正しく設定されているか
3. バックエンドが起動しているか

**解決策**:
```bash
# バックエンドログを確認
docker compose logs backend -f

# フロントエンド環境変数を確認
echo $NEXT_PUBLIC_WS_URL
```

### メッセージが重複する

**問題**: 同じメッセージが複数回表示される

**原因**: 重複チェックロジックのバグ

**解決策**: メッセージIDと送信時刻で重複を判定

### 接続が頻繁に切れる

**問題**: WebSocket接続が頻繁に切断される

**原因**: Pingが送信されていない、またはネットワークタイムアウト

**解決策**:
- Ping間隔を調整（現在30秒）
- 再接続間隔を調整（現在3秒）

## 📝 環境変数

### バックエンド

```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@db:5432/dbname
```

### フロントエンド

```bash
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## 🚀 今後の拡張案

1. **オンラインユーザー表示**: 接続中のユーザーをリアルタイム表示
2. **既読機能**: メッセージの既読状態をWebSocketで同期
3. **タイピングインジケーター**: 入力中の状態をリアルタイム表示
4. **通知**: 新しいメッセージの通知
5. **ファイル共有**: WebSocketでファイルアップロード進捗を表示

## 📚 参考資料

- [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/)
- [WebSocket API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [React Hooks](https://react.dev/reference/react)
