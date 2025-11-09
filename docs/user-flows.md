# ユーザー操作フロー図

## 概要

本ドキュメントでは、Miscatフロントエンドアプリケーションにおけるユーザー操作フローを説明します。主要な画面遷移、認証フロー、およびユーザーストーリーをMermaid記法で視覚化しています。


---

## 認証フロー

### 1. 基本認証フロー

未認証ユーザーがログインして認証済みになるまでの流れです。

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant Browser as ブラウザ
    participant FE as フロントエンド(Next.js)
    participant BFF as BFF(/api/auth/*)
    participant Backend as バックエンド(FastAPI)

    User->>Browser: アプリケーションにアクセス
    Browser->>FE: GET /
    FE->>Browser: ページを表示

    Note over FE: AuthContextが初期化
    FE->>BFF: GET /api/auth/me
    BFF-->>FE: 401 Unauthorized

    Note over User: 未認証のためログインページへ

    User->>Browser: ログインページにアクセス
    Browser->>FE: GET /login
    FE->>Browser: ログインフォーム表示

    User->>Browser: ユーザー名・パスワード入力
    Browser->>FE: フォーム送信

    FE->>BFF: POST /api/auth/login<br/>{username, password}
    BFF->>Backend: POST /auth/token<br/>(form-urlencoded)
    Backend-->>BFF: {access_token, token_type}

    Note over BFF: HttpOnly Cookieに<br/>access_tokenを設定

    BFF-->>FE: {access_token, token_type}

    FE->>BFF: GET /api/auth/me
    BFF->>Backend: GET /users/me<br/>Authorization: Bearer {token}
    Backend-->>BFF: {user_id, username, ...}
    BFF-->>FE: ユーザー情報

    Note over FE: AuthContextに<br/>ユーザー情報を保存

    FE->>Browser: ホームページにリダイレクト
    Browser->>User: 認証済みページ表示
```

### 2. 認証状態の確認フロー

アプリケーション起動時やページリロード時の認証確認です。

```mermaid
flowchart TD
    A[アプリケーション起動] --> B[AuthProvider初期化]
    B --> C{Cookie に<br/>access_token<br/>が存在？}

    C -->|Yes| D[GET /api/auth/me]
    C -->|No| E[未認証状態に設定]

    D --> F{レスポンス<br/>ステータス}

    F -->|200 OK| G[ユーザー情報を取得]
    F -->|401 Unauthorized| E
    F -->|500 Error| H[エラー状態に設定]

    G --> I[認証済み状態に設定]
    E --> J[ログインページへリダイレクト]
    I --> K[ホームページ表示]
    H --> L[エラーメッセージ表示]
```

### 3. ログアウトフロー

認証済みユーザーがログアウトする流れです。

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant FE as フロントエンド
    participant BFF as BFF(/api/auth/logout)
    participant Browser as ブラウザ

    User->>FE: ログアウトボタンをクリック
    FE->>BFF: POST /api/auth/logout

    Note over BFF: HttpOnly Cookieを削除

    BFF-->>FE: {message: "Logged out successfully"}

    Note over FE: AuthContextから<br/>ユーザー情報を削除

    FE->>Browser: ログインページにリダイレクト
    Browser->>User: ログインページ表示
```

---

## 画面遷移図

### 全体画面遷移

```mermaid
graph LR
    A[/ ルートページ] --> B{認証済み？}
    B -->|No| C[/login ログインページ]
    B -->|Yes| D[/ ホームページ<br/>認証済み]

    C --> E[ログインフォーム入力]
    E --> F{認証成功？}

    F -->|Yes| D
    F -->|No| G[エラーメッセージ表示]
    G --> C

    D --> H[メイン機能]
    D --> I[ログアウト]

    I --> C

    style C fill:#e1f5ff
    style D fill:#d4edda
    style G fill:#f8d7da
```

### 認証前後の画面状態

```mermaid
stateDiagram-v2
    [*] --> 未認証

    未認証 --> ログインページ: /loginにアクセス
    ログインページ --> 認証処理中: フォーム送信

    認証処理中 --> 認証済み: ログイン成功
    認証処理中 --> ログインエラー: ログイン失敗

    ログインエラー --> ログインページ: エラー表示

    認証済み --> ホームページ: リダイレクト
    ホームページ --> メイン機能: 各機能へ遷移

    メイン機能 --> ホームページ: 戻る
    ホームページ --> ログアウト処理: ログアウト
    メイン機能 --> ログアウト処理: ログアウト

    ログアウト処理 --> 未認証: Cookie削除
    未認証 --> [*]
```

---

## 主要なユーザーストーリー

### Story 1: 初回ログイン

**ユーザー:** 新規ユーザー
**目的:** アプリケーションにログインする

```mermaid
journey
    title 初回ログインのユーザージャーニー
    section アクセス
      アプリケーションURL入力: 5: ユーザー
      ルートページ表示: 3: システム
      ログインページへリダイレクト: 4: システム
    section ログイン
      ログインフォーム表示: 5: システム
      ユーザー名入力: 4: ユーザー
      パスワード入力: 4: ユーザー
      送信ボタンクリック: 5: ユーザー
    section 認証
      認証処理: 3: システム
      Cookie設定: 3: システム
      ユーザー情報取得: 4: システム
    section 完了
      ホームページへリダイレクト: 5: システム
      認証済みページ表示: 5: ユーザー
```

**ステップ詳細:**

1. ユーザーがアプリケーションにアクセス (`http://localhost:3000`)
2. AuthContextがユーザー情報取得を試みる → 未認証
3. ログインページ (`/login`) にリダイレクト
4. ユーザー名とパスワードを入力
5. 「ログイン」ボタンをクリック
6. BFFがバックエンドに認証リクエスト
7. 認証成功 → HttpOnly Cookieにトークン保存
8. ユーザー情報を取得してAuthContextに保存
9. ホームページ (`/`) にリダイレクト
10. 認証済みコンテンツを表示

### Story 2: ログインエラー処理

**ユーザー:** 既存ユーザー
**シナリオ:** パスワードを間違えた場合

```mermaid
sequenceDiagram
    participant User as ユーザー
    participant LoginPage as ログインページ
    participant API as BFF API

    User->>LoginPage: ユーザー名・パスワード入力
    LoginPage->>API: POST /api/auth/login
    API-->>LoginPage: 401 Unauthorized<br/>{error: "Invalid credentials"}

    Note over LoginPage: エラーメッセージ表示<br/>"ログインに失敗しました"

    LoginPage->>User: エラー表示（赤枠）
    User->>LoginPage: 正しいパスワードで再入力
    LoginPage->>API: POST /api/auth/login
    API-->>LoginPage: 200 OK
    LoginPage->>User: ホームページへリダイレクト
```

### Story 3: セッション復元

**ユーザー:** 既存ユーザー
**シナリオ:** ブラウザをリロードした場合

```mermaid
flowchart TD
    A[ページリロード] --> B[AuthProvider初期化]
    B --> C[GET /api/auth/me]
    C --> D{Cookie確認}

    D -->|有効なトークン| E[ユーザー情報取得成功]
    D -->|無効/期限切れ| F[401 Unauthorized]

    E --> G[認証済み状態を復元]
    F --> H[未認証状態に設定]

    G --> I[現在のページを維持]
    H --> J[ログインページへリダイレクト]
```

---

## エラーハンドリングフロー

### 1. ログイン時のエラーハンドリング

```mermaid
flowchart TD
    A[ログインフォーム送信] --> B{バリデーション}

    B -->|OK| C[POST /api/auth/login]
    B -->|NG| D[クライアントエラー表示]

    C --> E{HTTPステータス}

    E -->|200 OK| F[ログイン成功]
    E -->|400 Bad Request| G[入力エラー表示]
    E -->|401 Unauthorized| H[認証エラー表示]
    E -->|500 Server Error| I[サーバーエラー表示]
    E -->|Network Error| J[接続エラー表示]

    D --> K[フォームに残る]
    G --> K
    H --> K
    I --> K
    J --> K

    F --> L[ホームページへ]
```

**エラーメッセージ例:**

| エラー種別 | メッセージ | 対応 |
|-----------|----------|------|
| バリデーションエラー | "ユーザー名とパスワードを入力してください" | フォーム入力を促す |
| 認証エラー | "ログインに失敗しました" | 再入力を促す |
| サーバーエラー | "サーバーエラーが発生しました" | 時間をおいて再試行 |
| ネットワークエラー | "接続に失敗しました" | 接続状態を確認 |

### 2. 認証状態確認時のエラーハンドリング

```mermaid
flowchart TD
    A[GET /api/auth/me] --> B{レスポンス}

    B -->|200 OK| C[ユーザー情報取得]
    B -->|401 Unauthorized| D[トークン無効/期限切れ]
    B -->|500 Server Error| E[サーバーエラー]
    B -->|Network Error| F[ネットワークエラー]

    C --> G[認証済み状態に設定]
    D --> H[未認証状態に設定]
    E --> I[エラー状態<br/>リトライ可能]
    F --> I

    G --> J[コンテンツ表示]
    H --> K[ログインページへ]
    I --> L[エラーバナー表示]
```

---

## API呼び出しフロー詳細

### POST /api/auth/login

```mermaid
sequenceDiagram
    participant Client as クライアント<br/>(LoginPage)
    participant BFF as BFF<br/>(/api/auth/login)
    participant Backend as バックエンド<br/>(FastAPI)

    Client->>BFF: POST /api/auth/login<br/>Content-Type: application/json<br/>{username, password}

    Note over BFF: リクエストボディを<br/>form-urlencodedに変換

    BFF->>Backend: POST /auth/token<br/>Content-Type: application/x-www-form-urlencoded<br/>username=xxx&password=yyy

    alt 認証成功
        Backend-->>BFF: 200 OK<br/>{access_token, token_type}

        Note over BFF: HttpOnly Cookie設定<br/>access_token=xxx<br/>httpOnly=true<br/>secure=true(production)

        BFF-->>Client: 200 OK<br/>{access_token, token_type}

        Client->>Client: ユーザー情報取得
    else 認証失敗
        Backend-->>BFF: 401 Unauthorized<br/>{detail: "Invalid credentials"}
        BFF-->>Client: 401 Unauthorized<br/>{error: "Authentication failed"}
        Client->>Client: エラー表示
    else サーバーエラー
        Backend-->>BFF: 500 Internal Server Error
        BFF-->>Client: 500 Internal Server Error<br/>{error: "Internal server error"}
        Client->>Client: エラー表示
    end
```

### GET /api/auth/me

```mermaid
sequenceDiagram
    participant Client as クライアント<br/>(AuthContext)
    participant BFF as BFF<br/>(/api/auth/me)
    participant Backend as バックエンド<br/>(FastAPI)

    Client->>BFF: GET /api/auth/me<br/>Cookie: access_token=xxx

    alt Cookieが存在
        Note over BFF: CookieからTokenを取得

        BFF->>Backend: GET /users/me<br/>Authorization: Bearer xxx

        alt トークン有効
            Backend-->>BFF: 200 OK<br/>{user_id, username, display_name, ...}
            BFF-->>Client: 200 OK<br/>ユーザー情報
            Client->>Client: 認証済み状態に設定
        else トークン無効/期限切れ
            Backend-->>BFF: 401 Unauthorized
            BFF-->>Client: 401 Unauthorized<br/>{error: "Invalid or expired token"}
            Client->>Client: 未認証状態に設定
        end
    else Cookieが存在しない
        BFF-->>Client: 401 Unauthorized<br/>{error: "Not authenticated"}
        Client->>Client: 未認証状態に設定
    end
```

---

## まとめ

本ドキュメントでは、Miscatフロントエンドアプリケーションの主要なユーザー操作フローを視覚化しました。

**主要なポイント:**

1. **認証フロー**: HttpOnly Cookieベースのセキュアな認証
2. **画面遷移**: シンプルで直感的な遷移設計
3. **エラーハンドリング**: ユーザーフレンドリーなエラー表示
4. **セッション管理**: ページリロード時の自動セッション復元

次のドキュメント:
- [フロントエンド関数リファレンス](./functions/frontend.md)
- [フロントエンドアーキテクチャ](./frontend-architecture.md)
