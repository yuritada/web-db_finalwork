# チャンネルAPI (`/channels`)

## 概要

チャンネルAPIは、チャンネルの作成、取得、メッセージ履歴の取得機能を提供します。Phase 4で実装されました。

## エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| POST | `/channels` | チャンネル作成 | 必須 |
| GET | `/channels` | チャンネル一覧取得 | 必須 |
| GET | `/channels/{channel_id}` | チャンネル詳細取得 | 必須 |
| GET | `/channels/{channel_id}/messages` | メッセージ履歴取得 | 必須 |

---

## POST /channels

チャンネルを作成します。

### エンドポイント情報

- **URL**: `/channels`
- **メソッド**: `POST`
- **認証**: 必須（JWT Bearer トークン）
- **Content-Type**: `application/json`

### リクエストボディ

**スキーマ**: `ChannelCreate`

```json
{
  "name": "string",
  "description": "string (optional)",
  "is_private": false
}
```

**フィールド詳細**:

| フィールド | 型 | 必須 | 説明 | 制約 |
|-----------|-----|------|------|------|
| name | string | ✅ | チャンネル名 | 1-100文字、一意 |
| description | string | ❌ | チャンネル説明 | 0-500文字 |
| is_private | boolean | ❌ | プライベートチャンネルか | デフォルト: false |

### レスポンス

#### 201 Created

**スキーマ**: `ChannelPublic`

```json
{
  "id": 1,
  "name": "general",
  "description": "General discussion channel",
  "is_private": false,
  "created_at": "2025-01-10T10:00:00"
}
```

#### 400 Bad Request

チャンネル名が既に存在する場合。

```json
{
  "detail": "Channel name 'general' already exists"
}
```

#### 401 Unauthorized

トークンが無効または欠落している場合。

```json
{
  "detail": "Could not validate credentials"
}
```

### 使用例

```bash
curl -X POST http://localhost:8000/channels \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "tech-discussion",
    "description": "Technology discussion channel",
    "is_private": false
  }'
```

---

## GET /channels

全チャンネルの一覧を取得します。

### エンドポイント情報

- **URL**: `/channels`
- **メソッド**: `GET`
- **認証**: 必須（JWT Bearer トークン）

### レスポンス

#### 200 OK

**スキーマ**: `List[ChannelPublic]`

```json
[
  {
    "id": 1,
    "name": "general",
    "description": "General discussion",
    "is_private": false,
    "created_at": "2025-01-10T10:00:00"
  },
  {
    "id": 2,
    "name": "tech-discussion",
    "description": "Technology discussion channel",
    "is_private": false,
    "created_at": "2025-01-10T11:00:00"
  }
]
```

### 使用例

```bash
curl -X GET http://localhost:8000/channels \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## GET /channels/{channel_id}

特定のチャンネルの詳細情報を取得します。

### エンドポイント情報

- **URL**: `/channels/{channel_id}`
- **メソッド**: `GET`
- **認証**: 必須（JWT Bearer トークン）

### パスパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| channel_id | integer | チャンネルID |

### レスポンス

#### 200 OK

**スキーマ**: `ChannelPublic`

```json
{
  "id": 1,
  "name": "general",
  "description": "General discussion",
  "is_private": false,
  "created_at": "2025-01-10T10:00:00"
}
```

#### 404 Not Found

チャンネルが存在しない場合。

```json
{
  "detail": "Channel with id 999 not found"
}
```

### 使用例

```bash
curl -X GET http://localhost:8000/channels/1 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## GET /channels/{channel_id}/messages

チャンネルのメッセージ履歴を取得します。送信者情報を含みます。

### エンドポイント情報

- **URL**: `/channels/{channel_id}/messages`
- **メソッド**: `GET`
- **認証**: 必須（JWT Bearer トークン）

### パスパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| channel_id | integer | チャンネルID |

### クエリパラメータ

| パラメータ | 型 | デフォルト | 説明 | 制約 |
|-----------|-----|-----------|------|------|
| limit | integer | 100 | 取得件数 | 1-500 |
| offset | integer | 0 | スキップ件数 | 0以上 |

### レスポンス

#### 200 OK

**スキーマ**: `List[MessageWithSender]`

```json
[
  {
    "id": 123,
    "content": "Hello, everyone!",
    "sender_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "sender_username": "student01",
    "channel_id": 1,
    "receiver_id": null,
    "created_at": "2025-01-10T14:30:00"
  },
  {
    "id": 122,
    "content": "Welcome to the channel!",
    "sender_id": "7b3c5f89-1234-5678-90ab-cdef12345678",
    "sender_username": "professor_tanaka",
    "channel_id": 1,
    "receiver_id": null,
    "created_at": "2025-01-10T14:25:00"
  }
]
```

**特徴**:
- メッセージは新しい順にソートされています
- `sender_username`が含まれるため、N+1問題を回避したJOINクエリを使用
- `receiver_id`はチャンネルメッセージの場合は常に`null`

#### 404 Not Found

チャンネルが存在しない場合。

```json
{
  "detail": "Channel with id 999 not found"
}
```

### 使用例

```bash
# デフォルト（最新100件）
curl -X GET "http://localhost:8000/channels/1/messages" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ページネーション
curl -X GET "http://localhost:8000/channels/1/messages?limit=50&offset=100" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## データモデル

### ChannelCreate

```typescript
{
  name: string;          // 1-100文字、必須
  description?: string;  // 0-500文字、オプション
  is_private?: boolean;  // デフォルト: false
}
```

### ChannelPublic

```typescript
{
  id: number;
  name: string;
  description: string | null;
  is_private: boolean;
  created_at: string;  // ISO 8601形式
}
```

### MessageWithSender

```typescript
{
  id: number;
  content: string;
  sender_id: string;        // UUID
  sender_username: string;  // JOIN結果
  channel_id: number | null;
  receiver_id: string | null;  // UUID
  created_at: string;       // ISO 8601形式
}
```

---

## 注意事項

### チャンネル名の一意性

チャンネル名は一意である必要があります。同じ名前のチャンネルを作成しようとすると、400 Bad Requestエラーが返されます。

### N+1問題の回避

`GET /channels/{channel_id}/messages`エンドポイントは、N+1問題を回避するため、メッセージとユーザーをJOINした単一のクエリを使用しています。

### WebSocketとの連携

メッセージの投稿は、REST API（POST /channels/{id}/messages）ではなく、WebSocket（WS /ws/channel/{channel_id}）を使用してリアルタイムに行うことが推奨されます。このエンドポイントは主に履歴取得に使用されます。

---

## エラーコード一覧

| ステータスコード | 説明 |
|----------------|------|
| 200 OK | リクエスト成功 |
| 201 Created | チャンネル作成成功 |
| 400 Bad Request | バリデーションエラー、チャンネル名重複 |
| 401 Unauthorized | 認証失敗 |
| 404 Not Found | チャンネルが存在しない |
| 422 Unprocessable Entity | リクエストボディのフォーマットエラー |
