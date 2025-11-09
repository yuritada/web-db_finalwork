# データフロー図

---

## 認証フロー

### 1. ユーザー登録フロー

```mermaid
sequenceDiagram
    autonumber
    participant Browser
    participant Next.js
    participant FastAPI
    participant Database

    Browser->>Next.js: ユーザー登録フォーム送信
    Note over Browser,Next.js: POST /api/auth/signup<br/>{username, email, password, kategori, ...}

    Next.js->>Next.js: クライアント側バリデーション
    Next.js->>FastAPI: POST /auth/signup
    Note over Next.js,FastAPI: Request Body:<br/>{<br/>  "username": "testuser",<br/>  "email": "test@example.com",<br/>  "password": "password123",<br/>  "kategori": "学生",<br/>  "gakuseki_bango": "B2024001",<br/>  "faculty": "工学部"<br/>}

    FastAPI->>FastAPI: Pydanticバリデーション
    Note over FastAPI: UserCreateスキーマ検証<br/>- username: 3-100文字<br/>- email: メール形式<br/>- password: 8文字以上<br/>- kategori: Enum検証

    alt バリデーションエラー
        FastAPI-->>Next.js: 422 Validation Error
        Next.js-->>Browser: エラーメッセージ表示
    end

    FastAPI->>Database: ユーザー名・メール重複チェック
    Database-->>FastAPI: 検索結果

    alt 重複あり
        FastAPI-->>Next.js: 400 Bad Request<br/>"Username already exists"
        Next.js-->>Browser: エラーメッセージ表示
    end

    FastAPI->>FastAPI: パスワードハッシュ化（bcrypt）
    Note over FastAPI: passlib.hash.bcrypt.hash(password)

    alt kategori = "教員" or "事務"
        FastAPI->>FastAPI: gakuseki_bango自動生成
        Note over FastAPI: f"AUTO_{kategori}_{uuid}"
    end

    FastAPI->>Database: INSERT INTO users
    Note over Database: id: UUID生成<br/>hashed_password: bcrypt hash<br/>created_at: 現在時刻

    Database-->>FastAPI: ユーザーレコード
    FastAPI-->>Next.js: 201 Created<br/>UserPublic
    Note over Next.js,FastAPI: Response:<br/>{<br/>  "id": "uuid",<br/>  "username": "testuser",<br/>  "email": "test@example.com",<br/>  "kategori": "学生",<br/>  "gakuseki_bango": "B2024001",<br/>  "faculty": "工学部"<br/>}

    Next.js-->>Browser: 登録成功メッセージ
    Next.js->>Browser: ログインページへリダイレクト
```

### 2. ログインフロー（JWT発行）

```mermaid
sequenceDiagram
    autonumber
    participant Browser
    participant Next.js
    participant FastAPI
    participant Database

    Browser->>Next.js: ログインフォーム送信
    Note over Browser,Next.js: POST /api/auth/login<br/>{username, password}

    Next.js->>FastAPI: POST /auth/token
    Note over Next.js,FastAPI: Content-Type: application/x-www-form-urlencoded<br/>username=testuser&password=password123

    FastAPI->>Database: SELECT * FROM users WHERE username = ?
    Database-->>FastAPI: ユーザーレコード

    alt ユーザーが存在しない
        FastAPI-->>Next.js: 401 Unauthorized<br/>"Incorrect username or password"
        Next.js-->>Browser: エラーメッセージ表示
    end

    FastAPI->>FastAPI: パスワード検証
    Note over FastAPI: passlib.verify(<br/>  plain_password,<br/>  hashed_password<br/>)

    alt パスワード不一致
        FastAPI-->>Next.js: 401 Unauthorized<br/>"Incorrect username or password"
        Next.js-->>Browser: エラーメッセージ表示
    end

    FastAPI->>FastAPI: JWT生成
    Note over FastAPI: Payload:<br/>{<br/>  "sub": user.email,<br/>  "exp": now + 30 minutes<br/>}<br/><br/>Algorithm: HS256<br/>Secret: SECRET_KEY

    FastAPI-->>Next.js: 200 OK
    Note over Next.js,FastAPI: Response:<br/>{<br/>  "access_token": "eyJ...",<br/>  "token_type": "bearer"<br/>}

    Next.js->>Next.js: HttpOnly Cookieに保存
    Note over Next.js: Set-Cookie:<br/>access_token=eyJ...;<br/>HttpOnly; Secure; SameSite=Strict

    Next.js-->>Browser: ログイン成功
    Next.js->>Browser: ダッシュボードへリダイレクト
```

### 3. 認証チェックフロー

```mermaid
sequenceDiagram
    autonumber
    participant Browser
    participant Next.js
    participant FastAPI
    participant Database

    Browser->>Next.js: 認証が必要なページアクセス
    Note over Browser,Next.js: GET /dashboard

    Next.js->>Next.js: Cookieからトークン取得
    alt トークンなし
        Next.js-->>Browser: ログインページへリダイレクト
    end

    Next.js->>FastAPI: GET /users/me
    Note over Next.js,FastAPI: Authorization: Bearer eyJ...

    FastAPI->>FastAPI: JWT検証
    Note over FastAPI: 1. 署名検証（SECRET_KEY）<br/>2. 有効期限チェック<br/>3. Payload抽出

    alt JWT無効または期限切れ
        FastAPI-->>Next.js: 401 Unauthorized<br/>"Could not validate credentials"
        Next.js-->>Browser: ログインページへリダイレクト
    end

    FastAPI->>Database: SELECT * FROM users WHERE email = ?
    Note over Database: email = JWT.sub

    Database-->>FastAPI: ユーザーレコード

    alt ユーザーが存在しない
        FastAPI-->>Next.js: 401 Unauthorized
        Next.js-->>Browser: ログインページへリダイレクト
    end

    FastAPI->>Database: タグ情報取得
    Note over Database: SELECT tags.*<br/>FROM tags<br/>JOIN user_tags ON tags.id = user_tags.tag_id<br/>WHERE user_tags.user_id = ?

    Database-->>FastAPI: タグ一覧

    FastAPI-->>Next.js: 200 OK<br/>UserPublicWithTags
    Note over Next.js,FastAPI: Response:<br/>{<br/>  "id": "uuid",<br/>  "username": "testuser",<br/>  "email": "test@example.com",<br/>  "kategori": "学生",<br/>  "tags": [<br/>    {"id": 1, "name": "Python"},<br/>    {"id": 2, "name": "React"}<br/>  ]<br/>}

    Next.js-->>Browser: ダッシュボード表示
```

---

## ユーザー情報取得フロー

### 現在のユーザー情報取得（/users/me）

```mermaid
graph TB
    Start([HTTPリクエスト]) --> ExtractToken[Authorizationヘッダーからトークン抽出]
    ExtractToken --> ValidateJWT{JWT検証}

    ValidateJWT -->|無効| Err401[401 Unauthorized]
    ValidateJWT -->|有効| ExtractEmail[Payloadからemail抽出]

    ExtractEmail --> QueryUser[DBからユーザー検索]
    QueryUser --> UserExists{ユーザー存在?}

    UserExists -->|なし| Err401
    UserExists -->|あり| QueryTags[ユーザーのタグ取得]

    QueryTags --> BuildResponse[レスポンス構築]
    BuildResponse --> Return200[200 OK + UserPublicWithTags]

    Err401 --> End([HTTPレスポンス])
    Return200 --> End

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Err401 fill:#FF6B6B
    style Return200 fill:#4CAF50
```

### データ取得クエリ

**ユーザー情報取得**
```sql
SELECT
    id, username, email, kategori,
    gakuseki_bango, faculty, icon_path
FROM users
WHERE email = :email;
```

**タグ情報取得**
```sql
SELECT
    t.id, t.name, t.creator_id
FROM tags t
INNER JOIN user_tags ut ON t.id = ut.tag_id
WHERE ut.user_id = :user_id;
```

---

## エラーハンドリングフロー

### HTTPステータスコードマッピング

```mermaid
graph TB
    Request[HTTPリクエスト] --> Validation{バリデーション}

    Validation -->|成功| Business{ビジネスロジック}
    Validation -->|失敗| Err422[422 Unprocessable Entity<br/>Pydanticバリデーションエラー]

    Business -->|成功| Success[2xx Success]
    Business -->|認証エラー| Err401[401 Unauthorized<br/>認証失敗]
    Business -->|権限エラー| Err403[403 Forbidden<br/>権限不足]
    Business -->|リソース未発見| Err404[404 Not Found<br/>リソースなし]
    Business -->|重複エラー| Err400[400 Bad Request<br/>ビジネスルール違反]
    Business -->|サーバーエラー| Err500[500 Internal Server Error<br/>予期せぬエラー]

    Success --> Response[クライアントへレスポンス]
    Err422 --> Response
    Err401 --> Response
    Err403 --> Response
    Err404 --> Response
    Err400 --> Response
    Err500 --> Response

    style Success fill:#4CAF50
    style Err422 fill:#FFC107
    style Err401 fill:#FF6B6B
    style Err403 fill:#FF6B6B
    style Err404 fill:#FF9800
    style Err400 fill:#FF6B6B
    style Err500 fill:#9C27B0
```

### エラーレスポンス形式

#### 422 Validation Error（Pydantic）

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "username"],
      "msg": "String should have at least 3 characters",
      "input": "ab",
      "ctx": {
        "min_length": 3
      }
    }
  ]
}
```

#### 401 Unauthorized（認証エラー）

```json
{
  "detail": "Could not validate credentials"
}
```

#### 400 Bad Request（重複エラー）

```json
{
  "detail": "Username already exists"
}
```

---

## データ形式

### リクエストスキーマ

#### UserCreate（ユーザー登録）

```json
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "kategori": "学生",
  "gakuseki_bango": "B2024001",
  "faculty": "工学部"
}
```

**バリデーションルール**
- `username`: 3-100文字、必須
- `email`: メール形式、必須
- `password`: 8文字以上、必須
- `kategori`: Enum値（学生, 教授, 准教授, 講師, 事務）、必須
- `gakuseki_bango`: 最大50文字、教員/事務の場合はオプション
- `faculty`: 最大100文字、オプション

#### OAuth2 Login Form

```
Content-Type: application/x-www-form-urlencoded

username=testuser&password=password123
```

### レスポンススキーマ

#### UserPublic（ユーザー情報）

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "testuser",
  "email": "test@example.com",
  "kategori": "学生",
  "gakuseki_bango": "B2024001",
  "faculty": "工学部",
  "icon_path": null
}
```

#### UserPublicWithTags（タグ付きユーザー情報）

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "testuser",
  "email": "test@example.com",
  "kategori": "学生",
  "gakuseki_bango": "B2024001",
  "faculty": "工学部",
  "icon_path": null,
  "tags": [
    {
      "id": 1,
      "name": "Python",
      "creator_id": "550e8400-e29b-41d4-a716-446655440000"
    },
    {
      "id": 2,
      "name": "React",
      "creator_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ]
}
```

#### Token（JWT）

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwiZXhwIjoxNzMxMTQwNDAwfQ.signature",
  "token_type": "bearer"
}
```

### JWTペイロード構造

```json
{
  "sub": "test@example.com",
  "exp": 1731140400
}
```

**フィールド説明**
- `sub`: Subject（ユーザーのemail）
- `exp`: Expiration Time（有効期限、UNIX timestamp）

---

## セキュリティフロー

### パスワードハッシュ化フロー

```mermaid
graph LR
    PlainPassword[平文パスワード] --> Bcrypt[bcrypt.hash]
    Bcrypt --> Salt[ソルト自動生成]
    Salt --> Hash[ハッシュ化]
    Hash --> HashedPassword[ハッシュ済みパスワード]
    HashedPassword --> Database[(Database)]

    style PlainPassword fill:#FF6B6B
    style HashedPassword fill:#4CAF50
    style Database fill:#2196F3
```

**bcrypt特性**
- ソルトは自動生成
- ラウンド数: デフォルト（12）
- 同じパスワードでも毎回異なるハッシュ値

**例**
```python
# 入力
password = "password123"

# 出力（bcrypt hash）
hashed = "$2b$12$abc123...xyz789"
```

### JWT署名フロー

```mermaid
graph TB
    Header[Header<br/>{alg: HS256, typ: JWT}] --> Base64H[Base64URLエンコード]
    Payload[Payload<br/>{sub: email, exp: timestamp}] --> Base64P[Base64URLエンコード]

    Base64H --> Concat[ヘッダー.ペイロード]
    Base64P --> Concat

    Concat --> HMAC[HMAC-SHA256]
    SecretKey[SECRET_KEY] --> HMAC

    HMAC --> Signature[署名]
    Concat --> Final[JWT = ヘッダー.ペイロード.署名]
    Signature --> Final

    style SecretKey fill:#FF6B6B
    style Final fill:#4CAF50
```

**JWT検証プロセス**
1. JWTを `.` で分割（ヘッダー、ペイロード、署名）
2. ヘッダーとペイロードを再度HMAC-SHA256で署名
3. 計算した署名と受信した署名を比較
4. 一致すれば改ざんなし
5. 有効期限（exp）をチェック

---

**作成日**: 2025-11-09
**作成者**: worker3
**バージョン**: 1.0.0
