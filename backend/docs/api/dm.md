# ダイレクトメッセージAPI (`/messages/dm`)

## 概要

ダイレクトメッセージAPIは、ユーザー間の1対1メッセージ機能を提供します。Phase 4で実装されました。

## エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| POST | `/messages/dm` | DM送信 | 必須 |
| GET | `/messages/dm/{user_id}` | DM履歴取得 | 必須 |
| GET | `/messages/dm/conversations` | DM会話一覧取得 | 必須 |

---

## POST /messages/dm

ダイレクトメッセージを送信します。

### エンドポイント情報

- **URL**: `/messages/dm`
- **メソッド**: `POST`
- **認証**: 必須（JWT Bearer トークン）
- **Content-Type**: `application/json`

### リクエストボディ

**スキーマ**: `DMCreate`

```json
{
  "receiver_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "content": "Hello!"
}
```

**フィールド詳細**:

| フィールド | 型 | 必須 | 説明 | 制約 |
|-----------|-----|------|------|------|
| receiver_id | string (UUID) | ✅ | 受信者のユーザーID | 有効なUUID |
| content | string | ✅ | メッセージ内容 | 1文字以上 |

### レスポンス

#### 201 Created

**スキーマ**: `MessagePublic`

```json
{
  "id": 456,
  "content": "Hello!",
  "sender_id": "7b3c5f89-1234-5678-90ab-cdef12345678",
  "channel_id": null,
  "receiver_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "created_at": "2025-01-10T15:30:00"
}
```

#### 400 Bad Request

自分自身にDMを送信しようとした場合。

```json
{
  "detail": "Cannot send DM to yourself"
}
```

#### 404 Not Found

受信者が存在しない場合。

```json
{
  "detail": "User with id 3fa85f64-5717-4562-b3fc-2c963f66afa6 not found"
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
curl -X POST http://localhost:8000/messages/dm \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "content": "Hello, how are you?"
  }'
```

---

## GET /messages/dm/{user_id}

特定のユーザーとのDM履歴を取得します（双方向）。

### エンドポイント情報

- **URL**: `/messages/dm/{user_id}`
- **メソッド**: `GET`
- **認証**: 必須（JWT Bearer トークン）

### パスパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| user_id | string (UUID) | 相手のユーザーID |

### クエリパラメータ

| パラメータ | 型 | デフォルト | 説明 | 制約 |
|-----------|-----|-----------|------|------|
| limit | integer | 100 | 取得件数 | 1-500 |
| offset | integer | 0 | スキップ件数 | 0以上 |

### レスポンス

#### 200 OK

**スキーマ**: `List[MessagePublic]`

```json
[
  {
    "id": 458,
    "content": "Yes, I'm doing well!",
    "sender_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "channel_id": null,
    "receiver_id": "7b3c5f89-1234-5678-90ab-cdef12345678",
    "created_at": "2025-01-10T15:35:00"
  },
  {
    "id": 456,
    "content": "Hello, how are you?",
    "sender_id": "7b3c5f89-1234-5678-90ab-cdef12345678",
    "channel_id": null,
    "receiver_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "created_at": "2025-01-10T15:30:00"
  }
]
```

**特徴**:
- 送信したメッセージと受信したメッセージの両方を取得
- メッセージは新しい順にソート
- `channel_id`はDMの場合は常に`null`

### 使用例

```bash
# デフォルト（最新100件）
curl -X GET "http://localhost:8000/messages/dm/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# ページネーション
curl -X GET "http://localhost:8000/messages/dm/3fa85f64-5717-4562-b3fc-2c963f66afa6?limit=50&offset=100" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## GET /messages/dm/conversations

現在のユーザーがDMをやり取りしたユーザーの一覧を取得します（Phase 4拡張機能）。

### エンドポイント情報

- **URL**: `/messages/dm/conversations`
- **メソッド**: `GET`
- **認証**: 必須（JWT Bearer トークン）

### レスポンス

#### 200 OK

**スキーマ**: `List[DMConversation]`

```json
[
  {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "student01",
    "last_message": {
      "id": 458,
      "content": "Yes, I'm doing well!",
      "sender_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "created_at": "2025-01-10T15:35:00"
    },
    "unread_count": 2
  },
  {
    "user_id": "8c4d6f90-2345-6789-01bc-def234567890",
    "username": "professor_tanaka",
    "last_message": {
      "id": 420,
      "content": "See you tomorrow!",
      "sender_id": "7b3c5f89-1234-5678-90ab-cdef12345678",
      "created_at": "2025-01-09T18:00:00"
    },
    "unread_count": 0
  }
]
```

**特徴**:
- DMをやり取りしたユーザーの一覧
- 各会話の最新メッセージを含む
- 未読カウント機能（Phase 4拡張）

### 使用例

```bash
curl -X GET "http://localhost:8000/messages/dm/conversations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

## データモデル

### DMCreate

```typescript
{
  receiver_id: string;  // UUID、必須
  content: string;      // 1文字以上、必須
}
```

### MessagePublic

```typescript
{
  id: number;
  content: string;
  sender_id: string;        // UUID
  channel_id: number | null;  // DMの場合はnull
  receiver_id: string | null; // UUID、DMの場合は受信者ID
  created_at: string;       // ISO 8601形式
}
```

### DMConversation

```typescript
{
  user_id: string;      // UUID
  username: string;
  last_message: {
    id: number;
    content: string;
    sender_id: string;
    created_at: string;
  };
  unread_count: number;
}
```

---

## データベース設計

### DM判定ロジック

メッセージがDMかチャンネルメッセージかは、以下のフィールドで判定します：

```python
# DM
if message.channel_id is None and message.receiver_id is not None:
    # ダイレクトメッセージ
    pass

# チャンネルメッセージ
if message.channel_id is not None and message.receiver_id is None:
    # チャンネルメッセージ
    pass
```

### 双方向検索クエリ

DM履歴取得では、送信したメッセージと受信したメッセージの両方を取得するため、以下のようなORクエリを使用します：

```sql
SELECT * FROM messages
WHERE channel_id IS NULL AND (
  (sender_id = :user1 AND receiver_id = :user2) OR
  (sender_id = :user2 AND receiver_id = :user1)
)
ORDER BY created_at DESC
LIMIT :limit OFFSET :offset;
```

---

## 注意事項

### 自分自身へのDM送信の禁止

自分自身にDMを送信しようとすると、400 Bad Requestエラーが返されます。

### 既存Messageモデルの活用

Phase 4では、既存の`Message`モデルの`receiver_id`フィールドを活用してDM機能を実装しました。これにより、追加のテーブルを作成することなく、DMとチャンネルメッセージを統一的に管理しています。

### リアルタイム通信

DMのリアルタイム通信は、将来的にWebSocketの拡張（例: `/ws/dm/{user_id}`）で実装される可能性があります。現在はREST APIのみでポーリングベースの通信となります。

---

## エラーコード一覧

| ステータスコード | 説明 |
|----------------|------|
| 200 OK | リクエスト成功 |
| 201 Created | DM送信成功 |
| 400 Bad Request | 自分自身へのDM送信 |
| 401 Unauthorized | 認証失敗 |
| 404 Not Found | 受信者が存在しない |
| 422 Unprocessable Entity | リクエストボディのフォーマットエラー |
