# Miscat API仕様書

**最終更新**: 2025-11-14
**管理者**: worker1 (フロントエンド担当)
**バージョン**: 1.0


---

## API仕様書一覧

このドキュメントには、Miscatプロジェクトの全APIの仕様が統合されています。

### 仕様書一覧表

| API | エンドポイント数 | Phase | ステータス | 最終更新 |
|-----|----------------|-------|-----------|---------|
| 認証 (auth) | 2 | Phase 1 | ✅ 完成 | 2025-11-09 |
| ユーザー (users) | 1 | Phase 1 | ✅ 完成 | 2025-11-09 |
| Wiki (wiki) | 5 | Phase 2 | ✅ 完成 | 2025-11-14 |
| タグ (tags) | 5 | Phase 3 | ✅ 完成 | 2025-11-14 |
| 検索 (search) | 1 | Phase 3 | ✅ 完成 | 2025-11-14 |
| チャンネル (channels) | 5 | Phase 4 | ✅ 完成 | 2025-11-14 |
| DM (dm) | 3 | Phase 4 | ⚠️ 要更新 | 2025-11-10 |
| WebSocket (websocket) | 1 | Phase 4 | ⚠️ 要確認 | 2025-11-10 |

**合計エンドポイント数**: 23個

---

## API仕様書の読み方

### 基本構成

各API仕様は以下の構成になっています：

1. **概要セクション**
   - APIの目的と機能の説明
   - Phase情報

2. **エンドポイント一覧**
   - 表形式でのエンドポイント一覧
   - メソッド、パス、説明、認証要否

3. **各エンドポイントの詳細**
   - エンドポイント情報（URL、メソッド、認証、Content-Type）
   - パスパラメータ / クエリパラメータ
   - リクエストボディ（JSON schema）
   - フィールド詳細（表形式）
   - レスポンス（成功時・エラー時）
   - 備考・注意事項

4. **型定義セクション**
   - Pydantic（Python）またはTypeScript形式
   - リクエスト・レスポンスで使用する型の定義

5. **備考セクション**
   - Phase情報
   - 制約事項
   - セキュリティ考慮事項
   - パフォーマンス考慮事項
   - フロントエンド連携メモ

---

## 仕様書のフォーマット

### 表記規則

#### エンドポイントパス

- **バックエンド**: `/path/to/resource` （FastAPI実装）
- **フロントエンド**: `/api/path/to/resource` （Next.js API Routes経由）

仕様書では**バックエンドのパス**を記載しています。

#### パスパラメータ

- `{param_name}` 形式（例: `/wiki/pages/{page_id}`）
- または `:param_name` 形式（例: `/wiki/pages/:page_id`）

両方の表記が混在している場合がありますが、意味は同じです。

#### 認証

- **必須**: Bearer Token（JWT）が必要
- **不要**: 認証なしでアクセス可能

#### ステータス

- ✅ **完成**: 実装済み、仕様書完備
- ⚠️ **要更新**: 実装済みだが、仕様書が不完全または古い
- 🚧 **実装中**: 現在実装中
- ❌ **未実装**: 仕様のみ、未実装

---

## バージョン管理方針

### 現在の管理方法

- **場所**: Gitリポジトリ（`backend/docs/API.md`）
- **バージョン管理**: Gitコミットによる履歴管理
- **更新者**: 各workerが担当範囲を更新

### 更新時のルール

1. **実装変更時は必ず仕様書も更新**
   - 実装とドキュメントの乖離を防ぐ
   - コミットに仕様書の更新を含める

2. **更新内容の記録**
   - 各仕様書の「備考セクション」に変更履歴を追加（推奨）
   - Gitコミットメッセージに変更内容を明記

3. **レビュー**
   - 仕様書の変更はPRレビューで確認
   - 実装とドキュメントの整合性を確認

---

## 実装とドキュメントの同期ルール

### 基本原則

**実装とドキュメントは常に同期させる**

- 実装が変わったら、仕様書を即座に更新
- 仕様書が更新されたら、実装を確認

### 同期フロー

#### 新機能追加時

1. **仕様書作成（設計フェーズ）**
2. **実装（開発フェーズ）**
3. **仕様書レビュー（レビューフェーズ）**
4. **コミット**: 実装コードと仕様書を同一PRに含める

---

## 未実装API一覧

### Critical（早急な対応が必要）

#### 1. チャンネルメンバー管理API

- **エンドポイント**: `POST /channels/{channel_id}/members`
- **ステータス**: Phase 5実装予定

### Medium（改善が望ましい）

#### 2. Wiki共有解除API

- **エンドポイント**: `DELETE /wiki/pages/{page_id}/share/{user_id}`
- **ステータス**: 未実装

#### 3. タグ割り当て解除API

- **エンドポイント**: `DELETE /tags/{tag_id}/assign/{user_id}`
- **ステータス**: 未実装

---

# API詳細

---

## 認証API (`/auth`)

### 概要

認証APIは、ユーザー登録とログイン機能を提供します。OAuth2準拠のJWT（JSON Web Token）認証を使用しています。

### エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| POST | `/auth/signup` | ユーザー登録 | 不要 |
| POST | `/auth/token` | ログイン（JWT発行） | 不要 |

---

### POST /auth/signup

ユーザー登録エンドポイント。v3仕様に従い、学生以外の場合は`gakuseki_bango`を自動生成します。

#### エンドポイント情報

- **URL**: `/auth/signup`
- **メソッド**: `POST`
- **認証**: 不要
- **Content-Type**: `application/json`

#### リクエストボディ

**スキーマ**: `UserCreate`

```json
{
  "username": "string",
  "email": "user@example.com",
  "password": "string",
  "kategori": "学生" | "教授" | "准教授" | "講師" | "事務",
  "gakuseki_bango": "string (optional)",
  "faculty": "string (optional)"
}
```

**フィールド詳細**:

| フィールド | 型 | 必須 | 説明 | 制約 |
|-----------|-----|------|------|------|
| username | string | ✅ | ユーザー名 | 3-100文字、一意 |
| email | string | ✅ | メールアドレス | Email形式、一意 |
| password | string | ✅ | パスワード | 8文字以上 |
| kategori | enum | ✅ | ユーザーカテゴリー | 5種類から選択 |
| gakuseki_bango | string | ❌ | 学籍番号 | 学生の場合は必須、教員/事務は自動生成 |
| faculty | string | ❌ | 学部・所属 | 最大100文字 |

#### レスポンス

**成功 (201 Created)**:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "johndoe",
  "email": "johndoe@example.com",
  "kategori": "学生",
  "gakuseki_bango": "S12345678",
  "faculty": "情報学部",
  "icon_path": null
}
```

---

### POST /auth/token

ログインエンドポイント。ユーザー名とパスワードを検証し、JWTアクセストークンを発行します。

#### エンドポイント情報

- **URL**: `/auth/token`
- **メソッド**: `POST`
- **認証**: 不要
- **Content-Type**: `application/x-www-form-urlencoded`（OAuth2準拠）

#### リクエストボディ

**フォーマット**: `application/x-www-form-urlencoded`

```
username=student01&password=securepass123
```

#### レスポンス

**成功 (200 OK)**:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## ユーザーAPI (`/users`)

### 概要

ユーザーAPIは、認証済みユーザーの情報取得・更新機能を提供します。全エンドポイントでJWT認証が必須です。

### エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| GET | `/users/me` | 現在のユーザー情報取得 | ✅ 必須 |

---

### GET /users/me

現在認証されているユーザーの情報とタグ情報を取得します。

#### エンドポイント情報

- **URL**: `/users/me`
- **メソッド**: `GET`
- **認証**: ✅ Bearer Token必須
- **Content-Type**: `application/json`

#### レスポンス

**成功 (200 OK)**:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "student01",
  "email": "student01@example.com",
  "kategori": "学生",
  "gakuseki_bango": "S12345678",
  "faculty": "情報学部",
  "icon_path": null,
  "tags": [
    {
      "id": 1,
      "name": "プログラミング初心者",
      "creator_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
  ]
}
```

---

## Wiki API (`/wiki`)

### 概要

Wiki APIは、知識共有のためのWikiページの作成、閲覧、編集、共有機能を提供します。各Wikiページには高度な権限管理機能があり、閲覧のみ（VIEW_ONLY）または編集可能（EDIT）の2段階で他のユーザーと共有できます。

**Phase情報**: Phase 2で実装済み

### エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| GET | `/wiki/pages` | Wikiページ一覧取得 | 必須 |
| POST | `/wiki/pages` | Wikiページ作成 | 必須 |
| GET | `/wiki/pages/{page_id}` | Wikiページ詳細取得 | 必須 |
| PUT | `/wiki/pages/{page_id}` | Wikiページ更新 | 必須 |
| POST | `/wiki/pages/{page_id}/share` | Wikiページ共有（権限付与） | 必須 |

---

### GET /wiki/pages

現在のユーザーが閲覧権限を持つWikiページの一覧を取得します。

#### エンドポイント情報

- **URL**: `/wiki/pages`
- **メソッド**: `GET`
- **認証**: 必須（Bearer Token）

#### レスポンス

**成功時（200 OK）**:

```json
[
  {
    "id": 1,
    "title": "プロジェクト概要",
    "content": "このプロジェクトは...",
    "creator_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "created_at": "2025-01-10T12:00:00Z",
    "updated_at": "2025-01-10T15:30:00Z"
  }
]
```

---

### POST /wiki/pages

新しいWikiページを作成します。

#### リクエストボディ

```json
{
  "title": "プロジェクト概要",
  "content": "このプロジェクトは学内コミュニケーションツールです..."
}
```

---

### GET /wiki/pages/{page_id}

指定されたWikiページの詳細情報を取得します（権限情報含む）。

---

### PUT /wiki/pages/{page_id}

指定されたWikiページを更新します（EDIT権限が必要）。

---

### POST /wiki/pages/{page_id}/share

Wikiページを他のユーザーと共有します（権限を付与・更新）。

#### リクエストボディ

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "permission_level": "VIEW_ONLY"
}
```

**権限レベル**:
- `VIEW_ONLY`: 閲覧のみ可能
- `EDIT`: 閲覧と編集が可能

---

## タグAPI (`/tags`)

### 概要

Tags APIは、ユーザーにタグを割り当てる機能を提供します。タグは学生・教員・事務などのカテゴリを柔軟に設定するためのラベルです。

**Phase情報**: Phase 2で実装済み

### エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| GET | `/tags` | タグ一覧取得 | 必須 |
| POST | `/tags` | タグ作成 | 必須 |
| GET | `/tags/{tag_id}` | タグ詳細取得 | 必須 |
| POST | `/tags/{tag_id}/assign` | タグ割り当て | 必須 |
| DELETE | `/tags/{tag_id}` | タグ削除 | 必須 |

---

### GET /tags

現在のユーザーに割り当てられたタグ一覧を取得します。

---

### POST /tags

新しいタグを作成します。

#### リクエストボディ

```json
{
  "name": "情報学部"
}
```

---

### GET /tags/{tag_id}

指定されたタグの詳細情報を取得します（割り当てられたユーザーリスト含む）。

---

### POST /tags/{tag_id}/assign

ユーザーにタグを割り当てます。

#### リクエストボディ

```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 権限チェック（v3仕様準拠）

1. **学生の場合**: 誰にでもタグ割り当て可能
2. **教員の場合**: 自分が作成したタグのみ割り当て可能

---

### DELETE /tags/{tag_id}

タグを削除します（作成者のみ）。

---

## 検索API (`/search`)

### 概要

Search APIは、Wiki、タグ、ユーザーを横断的に検索する統合検索機能を提供します。

**Phase情報**: Phase 2で実装済み

### エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| GET | `/search` | 統合検索（wiki/tag/user/all） | 必須 |

---

### GET /search

Wikiページ、タグ、ユーザーを横断的に検索します。

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 | デフォルト |
|-----------|-----|------|------|----------|
| q | string | ✅ | 検索キーワード | - |
| type | enum | ❌ | 検索対象タイプ | "all" |

**type の値**:
- `wiki`: Wikiページのみ検索
- `tag`: タグのみ検索
- `user`: ユーザーのみ検索
- `all`: 全て検索（デフォルト）

#### レスポンス

```json
{
  "results": [
    {
      "type": "wiki",
      "id": 1,
      "title": "プロジェクト概要",
      "snippet": "このプロジェクトは..."
    },
    {
      "type": "tag",
      "id": 2,
      "name": "情報学部"
    }
  ],
  "total": 2
}
```

---

## チャンネルAPI (`/channels`)

### 概要

Channel APIは、チャンネルの作成、一覧取得、メッセージの投稿・取得機能を提供します。

**Phase情報**: Phase 4で実装済み

### エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| POST | `/channels` | チャンネル作成 | 必須 |
| GET | `/channels` | チャンネル一覧取得 | 必須 |
| GET | `/channels/{channel_id}` | チャンネル詳細取得 | 必須 |
| POST | `/channels/{channel_id}/messages` | メッセージ投稿 | 必須 |
| GET | `/channels/{channel_id}/messages` | メッセージ履歴取得 | 必須 |

---

### POST /channels

チャンネルを作成します。

#### リクエストボディ

```json
{
  "name": "general",
  "description": "General discussion channel",
  "is_private": false
}
```

---

### GET /channels

全チャンネルの一覧を取得します。

---

### GET /channels/{channel_id}

チャンネルの詳細情報を取得します。

#### エンドポイント情報

- **URL**: `/channels/{channel_id}`
- **メソッド**: `GET`
- **認証**: 必須（Bearer Token）
- **Content-Type**: `application/json`

#### パスパラメータ

| パラメータ | 型 | 説明 |
|-----------|-----|------|
| channel_id | number | チャンネルID |

#### レスポンス

**成功時（200 OK）**:

```json
{
  "id": 1,
  "name": "general",
  "description": "General discussion channel",
  "is_private": false
}
```

**エラー時**:

| ステータス | 説明 | レスポンス例 |
|-----------|------|-------------|
| 404 | チャンネルが存在しない | `{"detail": "Channel not found"}` |
| 401 | 認証エラー | `{"detail": "Not authenticated"}` |

---

### POST /channels/{channel_id}/messages

チャンネルにメッセージを投稿します。

#### リクエストボディ

```json
{
  "content": "Hello, everyone!"
}
```

---

### GET /channels/{channel_id}/messages

チャンネルのメッセージ履歴を取得します。

#### クエリパラメータ

| パラメータ | 型 | 必須 | 説明 | デフォルト | 制約 |
|-----------|-----|------|------|-----------|------|
| limit | number | ❌ | 取得件数 | 100 | 1-500 |
| offset | number | ❌ | オフセット | 0 | 0以上 |

---

## Direct Message API (`/messages/dm`)

### 概要

Direct Message APIは、ユーザー間の1対1メッセージング機能を提供します。

**Phase情報**: Phase 4で実装済み

### エンドポイント一覧

| メソッド | パス | 説明 | 認証 |
|---------|------|------|------|
| POST | `/messages/dm` | DM送信 | 必須 |
| GET | `/messages/dm/{user_id}` | DM履歴取得 | 必須 |
| GET | `/messages/dm` | DM会話一覧取得 | 必須 |

---

### POST /messages/dm

ダイレクトメッセージを送信します。

#### リクエストボディ

```json
{
  "receiver_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "content": "Hello!"
}
```

---

### GET /messages/dm/{user_id}

特定のユーザーとのDM履歴を取得します（双方向）。

---

### GET /messages/dm

現在のユーザーがDMをやり取りしたユーザーの一覧を取得します。

#### レスポンス

```json
[
  {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "alice",
    "last_message": "See you tomorrow!",
    "last_message_at": "2025-01-10T14:30:00",
    "unread_count": 0
  }
]
```

---

## WebSocket API (`/ws`)

### 概要

WebSocket APIは、チャンネルのリアルタイム通信機能を提供します。

**Phase情報**: Phase 4で実装済み

### エンドポイント一覧

| プロトコル | パス | 説明 | 認証 |
|-----------|------|------|------|
| WS | `/ws/channel/{channel_id}` | チャンネルリアルタイム通信 | 不要（将来的に実装予定） |

---

### WS /ws/channel/{channel_id}

チャンネルのリアルタイム通信WebSocket接続。

#### エンドポイント情報

- **URL**: `ws://localhost:8000/ws/channel/{channel_id}`
- **プロトコル**: WebSocket
- **認証**: 不要（Phase 4実装、将来的にJWT認証追加予定）

#### メッセージフォーマット

**クライアント→サーバー**:

```json
{
  "type": "message",
  "content": "Hello, everyone!",
  "sender_username": "student01"
}
```

**サーバー→クライアント**:

```json
{
  "type": "message",
  "content": "Hello, everyone!",
  "sender_username": "student01",
  "timestamp": "2025-01-10T14:30:00"
}
```

---

## 変更履歴

### 2025-11-14 (v1.0)

#### 追加

- API仕様書を統合（backend/docs/api/*.md → backend/docs/API.md）
- Wiki API、タグAPI、検索APIの仕様を統合
- GET /channels/{channel_id} エンドポイント詳細を追加（チャンネル詳細取得）

#### 変更

- channels APIのステータスを「⚠️ 要更新」→「✅ 完成」に更新
- エンドポイント数を22個 → 23個に更新

#### 削除

- 未実装API一覧からGET /channels/{channel_id}を削除（実装完了のため）

---

## 関連ドキュメント

- **バックエンドアーキテクチャ**: `backend/docs/backend-architecture.md`
- **データベーススキーマ**: `backend/docs/database_schema.md`
- **認証フロー**: `backend/docs/auth-flow.md`
- **デプロイメント**: `backend/docs/deployment.md`

---

**Note**: この統合API仕様書は、worker3がドキュメント統合タスクの一環として作成しました。
