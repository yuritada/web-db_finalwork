# システムアーキテクチャ

---

## システム全体構成

```mermaid
graph TB
    subgraph "Client"
        Browser[Web Browser]
    end

    subgraph "Docker Network: finalwork_default"
        subgraph "Frontend Container"
            NextJS[Next.js 15<br/>Port: 3000]
        end

        subgraph "Backend Container"
            FastAPI[FastAPI<br/>Uvicorn<br/>Port: 8000]
            Alembic[Alembic<br/>Migration Tool]
        end

        subgraph "Database Container"
            PostgreSQL[(PostgreSQL 15<br/>Port: 5432)]
        end
    end

    Browser -->|HTTP/3000| NextJS
    Browser -->|HTTP/8000<br/>API直接アクセス| FastAPI
    NextJS -->|HTTP/8000<br/>API呼び出し| FastAPI
    FastAPI -->|SQLAlchemy<br/>psycopg2| PostgreSQL
    Alembic -->|Schema Migration| PostgreSQL

    style NextJS fill:#61dafb,stroke:#333,stroke-width:2px
    style FastAPI fill:#009688,stroke:#333,stroke-width:2px
    style PostgreSQL fill:#336791,stroke:#333,stroke-width:2px
```

### レイヤー構成

```mermaid
graph LR
    subgraph "Presentation Layer"
        UI[Next.js UI Components]
    end

    subgraph "API Layer"
        Router[FastAPI Routers]
        Auth[Authentication]
        Validation[Pydantic Validation]
    end

    subgraph "Business Logic Layer"
        Services[Business Services]
        CRUD[CRUD Operations]
    end

    subgraph "Data Access Layer"
        ORM[SQLAlchemy ORM]
        Models[Database Models]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL)]
    end

    UI --> Router
    Router --> Auth
    Router --> Validation
    Validation --> Services
    Services --> CRUD
    CRUD --> ORM
    ORM --> Models
    Models --> DB
```

---

## コンテナ構成

### 1. Frontend Container (`finalwork-frontend-1`)

```mermaid
graph TB
    subgraph "Frontend Container"
        NodeJS[Node.js 22]
        NextApp[Next.js Application]
        ReactComp[React Components]

        NodeJS --> NextApp
        NextApp --> ReactComp
    end

    subgraph "Volumes"
        FESrc[./frontend → /app]
        NodeModules[node_modules]
    end

    FESrc -.-> NextApp
    NodeModules -.-> NextApp

    subgraph "Exposed Ports"
        Port3000[3000:3000]
    end

    NextApp --> Port3000
```

**仕様**
- **Base Image**: `node:22-alpine`
- **Working Directory**: `/app`
- **Port**: `3000`
- **Volume**: `./frontend:/app`, `node_modules`
- **Hot Reload**: 有効
- **Startup Command**: `npm run dev`

### 2. Backend Container (`finalwork-backend-1`)

```mermaid
graph TB
    subgraph "Backend Container"
        Python[Python 3.12]
        Uvicorn[Uvicorn ASGI Server]
        FastAPI[FastAPI Application]

        subgraph "FastAPI Components"
            Routers[Routers<br/>/auth, /users]
            Middleware[CORS Middleware]
            Dependencies[Dependencies<br/>get_current_user]
        end

        subgraph "Database Layer"
            SQLAlchemy[SQLAlchemy ORM]
            Alembic[Alembic Migrations]
        end

        Python --> Uvicorn
        Uvicorn --> FastAPI
        FastAPI --> Routers
        FastAPI --> Middleware
        FastAPI --> Dependencies
        FastAPI --> SQLAlchemy
        FastAPI --> Alembic
    end

    subgraph "Volumes"
        BESrc[./backend → /app]
    end

    BESrc -.-> FastAPI

    subgraph "Exposed Ports"
        Port8000[8000:8000]
    end

    FastAPI --> Port8000
```

**仕様**
- **Base Image**: `python:3.12-slim`
- **Package Manager**: `uv`
- **Working Directory**: `/app`
- **Port**: `8000`
- **Volume**: `./backend:/app`
- **Hot Reload**: 有効（Uvicorn `--reload`）
- **Startup Command**: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

### 3. Database Container (`finalwork-db-1`)

```mermaid
graph TB
    subgraph "Database Container"
        PostgreSQL[PostgreSQL 15 Alpine]

        subgraph "Databases"
            CommDB[(commu_db)]
        end

        subgraph "Users"
            FastAPIUser[fastapi_user]
        end

        PostgreSQL --> CommDB
        FastAPIUser --> CommDB
    end

    subgraph "Volumes"
        PGData[pg_data → /var/lib/postgresql/data]
    end

    CommDB -.-> PGData

    subgraph "Exposed Ports"
        Port5432[5432:5432]
    end

    PostgreSQL --> Port5432

    subgraph "Health Check"
        HealthCmd["pg_isready -U fastapi_user"]
    end

    PostgreSQL --> HealthCmd
```

**仕様**
- **Base Image**: `postgres:15-alpine`
- **Port**: `5432`
- **Volume**: `pg_data:/var/lib/postgresql/data`
- **Database**: `commu_db`
- **User**: `fastapi_user`
- **Password**: `fastapi_password`（開発環境）
- **Health Check**: `pg_isready -U fastapi_user`

---

## ネットワーク構成

### Docker Network

```mermaid
graph TB
    subgraph "Docker Network: finalwork_default"
        Frontend["finalwork-frontend-1<br/>IP: 172.x.x.2"]
        Backend["finalwork-backend-1<br/>IP: 172.x.x.3"]
        Database["finalwork-db-1<br/>IP: 172.x.x.4"]
    end

    Host[Host Machine<br/>localhost]

    Host -->|Port 3000| Frontend
    Host -->|Port 8000| Backend
    Host -->|Port 5432| Database

    Frontend -.->|DNS: backend:8000| Backend
    Backend -.->|DNS: db:5432| Database
```

### ポート番号一覧

| サービス | ホストポート | コンテナポート | プロトコル | 用途 |
|---------|------------|--------------|----------|------|
| Frontend | 3000 | 3000 | HTTP | Next.js開発サーバー |
| Backend | 8000 | 8000 | HTTP | FastAPI/Uvicorn |
| Database | 5432 | 5432 | PostgreSQL | PostgreSQLサーバー |

### 内部通信

**Frontend → Backend**
```
URL: http://backend:8000
DNS Resolution: Docker内部DNS
Protocol: HTTP
```

**Backend → Database**
```
URL: postgresql://fastapi_user:fastapi_password@db:5432/commu_db
DNS Resolution: Docker内部DNS
Protocol: PostgreSQL Wire Protocol
```

---

## データベーススキーマ

### ER図（全体）

```mermaid
erDiagram
    users ||--o{ tags : creates
    users ||--o{ wiki_pages : creates
    users ||--o{ user_tags : has
    users ||--o{ wiki_page_permissions : granted
    users ||--o{ messages : sends
    users ||--o{ messages : receives
    users ||--o{ files : uploads

    tags ||--o{ user_tags : tagged

    wiki_pages ||--o{ wiki_page_permissions : has
    wiki_pages ||--o{ files : attached

    channels ||--o{ messages : contains

    messages ||--o{ files : attached

    users {
        uuid id PK
        varchar username UK
        varchar email UK
        varchar hashed_password
        varchar kategori
        varchar gakuseki_bango UK
        varchar faculty
        varchar icon_path
    }

    tags {
        serial id PK
        varchar name UK
        uuid creator_id FK
    }

    user_tags {
        serial id PK
        uuid user_id FK
        int tag_id FK
    }

    wiki_pages {
        serial id PK
        varchar title
        text content
        uuid creator_id FK
        timestamp created_at
        timestamp updated_at
    }

    wiki_page_permissions {
        serial id PK
        int page_id FK
        uuid user_id FK
        varchar permission_level
    }

    channels {
        serial id PK
        varchar name UK
        varchar description
        boolean is_private
    }

    messages {
        serial id PK
        text content
        uuid sender_id FK
        int channel_id FK
        uuid receiver_id FK
        timestamp created_at
    }

    files {
        serial id PK
        varchar filename
        varchar file_path
        bigint file_size
        varchar mime_type
        uuid uploader_id FK
        int message_id FK
        int wiki_page_id FK
        timestamp uploaded_at
    }
```

### テーブル詳細

#### 1. users テーブル
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    kategori VARCHAR(19) NOT NULL,  -- '学生', '教授', '准教授', '講師', '事務'
    gakuseki_bango VARCHAR(50) UNIQUE,
    faculty VARCHAR(100),
    icon_path VARCHAR(255)
);
```

#### 2. tags テーブル
```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);
```

#### 3. wiki_pages テーブル
```sql
CREATE TABLE wiki_pages (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

---

## 技術スタック

### Frontend

```mermaid
graph LR
    subgraph "Frontend Stack"
        Next[Next.js 15]
        React[React 19]
        TS[TypeScript]
        Tailwind[Tailwind CSS]
    end

    Next --> React
    Next --> TS
    Next --> Tailwind
```

| 技術 | バージョン | 用途 |
|-----|----------|------|
| Next.js | 15.x | Reactフレームワーク |
| React | 19.x | UIライブラリ |
| TypeScript | 5.x | 型安全な開発 |
| Tailwind CSS | 3.x | CSSフレームワーク |

### Backend

```mermaid
graph LR
    subgraph "Backend Stack"
        FastAPI[FastAPI 0.121]
        Pydantic[Pydantic 2.12]
        SQLAlchemy[SQLAlchemy 2.0]
        Alembic[Alembic 1.17]
        JWT[python-jose]
        Bcrypt[passlib bcrypt]
    end

    FastAPI --> Pydantic
    FastAPI --> SQLAlchemy
    SQLAlchemy --> Alembic
    FastAPI --> JWT
    FastAPI --> Bcrypt
```

| 技術 | バージョン | 用途 |
|-----|----------|------|
| FastAPI | 0.121.x | Webフレームワーク |
| Uvicorn | 0.38.x | ASGIサーバー |
| Pydantic | 2.12.x | データバリデーション |
| SQLAlchemy | 2.0.x | ORM |
| Alembic | 1.17.x | データベースマイグレーション |
| python-jose | 3.5.x | JWT処理 |
| passlib | 1.7.x | パスワードハッシュ化 |
| psycopg2-binary | 2.9.x | PostgreSQLドライバ |

### Database

| 技術 | バージョン | 用途 |
|-----|----------|------|
| PostgreSQL | 15 Alpine | リレーショナルデータベース |

### Development Tools

| 技術 | バージョン | 用途 |
|-----|----------|------|
| Docker | 20.10+ | コンテナ化 |
| Docker Compose | 2.0+ | マルチコンテナ管理 |
| uv | latest | Python パッケージマネージャー |
| pytest | 9.0.x | テストフレームワーク |
| httpx | 0.28.x | HTTPクライアント（テスト用） |

---

## 環境変数

### Backend環境変数 (`backend/.env`)

| 変数名 | 説明 | デフォルト値 | 必須 |
|-------|-----|------------|-----|
| `DATABASE_URL` | PostgreSQL接続URL | `postgresql://...` | ✅ |
| `SECRET_KEY` | JWT署名鍵 | - | ✅ |
| `ALGORITHM` | JWT署名アルゴリズム | `HS256` | ✅ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | トークン有効期限（分） | `30` | ✅ |
| `ALLOWED_ORIGINS` | CORS許可オリジン | `http://localhost:3000` | ✅ |
| `ENVIRONMENT` | 実行環境 | `development` | ❌ |

### Frontend環境変数 (`frontend/.env.local`)

| 変数名 | 説明 | デフォルト値 | 必須 |
|-------|-----|------------|-----|
| `NEXT_PUBLIC_API_URL` | バックエンドAPI URL | `http://localhost:8000` | ✅ |

### Docker Compose環境変数

| 変数名 | 説明 | デフォルト値 |
|-------|-----|------------|
| `POSTGRES_USER` | PostgreSQLユーザー名 | `fastapi_user` |
| `POSTGRES_PASSWORD` | PostgreSQLパスワード | `fastapi_password` |
| `POSTGRES_DB` | データベース名 | `commu_db` |

---

## セキュリティ考慮事項

### 1. 認証・認可

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant Database

    Client->>FastAPI: POST /auth/token (username, password)
    FastAPI->>Database: ユーザー検証
    Database-->>FastAPI: ユーザー情報
    FastAPI->>FastAPI: パスワード検証（bcrypt）
    FastAPI->>FastAPI: JWT生成（SECRET_KEY）
    FastAPI-->>Client: access_token

    Client->>FastAPI: GET /users/me (Authorization: Bearer {token})
    FastAPI->>FastAPI: JWT検証
    FastAPI->>Database: ユーザー情報取得
    Database-->>FastAPI: ユーザー情報
    FastAPI-->>Client: ユーザー情報
```

### 2. パスワードハッシュ化

- **アルゴリズム**: bcrypt
- **ライブラリ**: passlib
- **ソルト**: 自動生成

### 3. CORS設定

```python
# 開発環境
ALLOWED_ORIGINS = ["http://localhost:3000"]

# 本番環境（例）
ALLOWED_ORIGINS = ["https://your-domain.com"]
```

---

## スケーラビリティ

### 水平スケーリング

```mermaid
graph TB
    LB[Load Balancer]

    subgraph "Backend Instances"
        BE1[Backend 1]
        BE2[Backend 2]
        BE3[Backend N]
    end

    subgraph "Database"
        Primary[(Primary DB)]
        Replica1[(Replica 1)]
        Replica2[(Replica 2)]
    end

    LB --> BE1
    LB --> BE2
    LB --> BE3

    BE1 --> Primary
    BE2 --> Primary
    BE3 --> Primary

    Primary -.-> Replica1
    Primary -.-> Replica2
```

### 推奨構成（本番環境）

1. **アプリケーション層**
   - Backend: 複数インスタンス（最低2台）
   - Frontend: CDN配信（Vercel, Cloudflare等）

2. **データベース層**
   - マネージドサービス（AWS RDS, Google Cloud SQL等）
   - レプリケーション有効化
   - 自動バックアップ

3. **キャッシュ層**
   - Redis（セッション管理、キャッシュ）

---

**作成日**: 2025-11-09
**作成者**: worker3
**バージョン**: 1.0.0
