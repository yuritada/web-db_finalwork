# Miscatページドキュメント

このディレクトリには、Miscatアプリケーションの全ページに関する詳細なドキュメントが含まれています。

**最終更新**: 2025-11-14
**管理者**: worker3 (ドキュメント担当)

---

## 📁 ドキュメント一覧

### 認証関連ページ（3ページ）

| ファイル | ページ名 | パス | 認証 |
|---------|---------|------|------|
| [index.md](./index.md) | トップページ | `/` | 不要 |
| [login.md](./login.md) | ログインページ | `/login` | 不要 |
| [signup.md](./signup.md) | サインアップページ | `/signup` | 不要 |

### メイン機能ページ（10ページ）

| ファイル | ページ名 | パス | 認証 |
|---------|---------|------|------|
| [main-dashboard.md](./main-dashboard.md) | メインダッシュボード | `/main` | 必須 |
| [wiki-list.md](./wiki-list.md) | Wiki一覧 | `/wiki` | 必須 |
| [wiki-detail.md](./wiki-detail.md) | Wiki詳細 | `/wiki/[page_id]` | 必須 |
| [tag-list.md](./tag-list.md) | タグ一覧 | `/tags` | 必須 |
| [tag-detail.md](./tag-detail.md) | タグ詳細 | `/tags/[tag_id]` | 必須 |
| [search.md](./search.md) | 検索 | `/search` | 必須 |
| [channel-list.md](./channel-list.md) | チャンネル一覧 | `/channels` | 必須 |
| [channel-detail.md](./channel-detail.md) | チャンネル詳細 | `/channels/[channel_id]` | 必須 |
| [dm-list.md](./dm-list.md) | DM一覧 | `/dm` | 必須 |
| [dm-detail.md](./dm-detail.md) | DM詳細 | `/dm/[dm_id]` | 必須 |

**合計**: 13ページ

---

## 📖 ドキュメントの読み方

### 統一フォーマット

各ページドキュメントは以下の統一フォーマットに従っています：

1. **基本情報**
   - ページ名
   - パス（ルート）
   - ファイルパス
   - 認証要否

2. **概要**
   - ページの目的と機能の説明

3. **主な機能**
   - 実装されている機能の詳細リスト

4. **制限事項**
   - アクセス制限
   - 機能制限
   - 権限による制限

5. **接続先API**
   - 使用しているバックエンドAPI
   - APIエンドポイント一覧

6. **ページコンテンツ**
   - レイアウト図
   - UIコンポーネント一覧
   - デザイン仕様

7. **ナビゲーション**
   - 遷移先ページ
   - 遷移元ページ

---

## 🗺️ ページマップ

### サイト構造

```
/（トップページ）
├── /login（ログイン）
└── /signup（サインアップ）
    ↓
/main（メインダッシュボード）
├── /wiki（Wiki一覧）
│   └── /wiki/[page_id]（Wiki詳細）
├── /tags（タグ一覧）
│   └── /tags/[tag_id]（タグ詳細）
├── /search（検索）
├── /channels（チャンネル一覧）
│   └── /channels/[channel_id]（チャンネル詳細）
└── /dm（DM一覧）
    └── /dm/[dm_id]（DM詳細）
```

### ページグループ

#### 公開ページ（認証不要）
- トップページ
- ログインページ
- サインアップページ

#### 保護ページ（認証必須）
- 上記以外の全ページ

---

## 🔌 API接続マップ

### 認証API (`/auth`)
- ログインページ: `POST /auth/token`
- サインアップページ: `POST /auth/signup`
- 全保護ページ: `GET /auth/me`（認証確認）

### Wiki API (`/wiki`)
- Wiki一覧ページ: `GET /wiki/pages`
- Wiki詳細ページ: `GET /wiki/pages/{page_id}`
- Wiki作成・編集: `POST /wiki/pages`, `PUT /wiki/pages/{page_id}`

### タグAPI (`/tags`)
- タグ一覧ページ: `GET /tags`
- タグ詳細ページ: `GET /tags/{tag_id}`

### 検索API (`/search`)
- 検索ページ: `GET /search`

### チャンネルAPI (`/channels`)
- チャンネル一覧ページ: `GET /channels`
- チャンネル詳細ページ: `GET /channels/{channel_id}`, `GET /channels/{channel_id}/messages`

### DM API (`/messages/dm`)
- DM一覧ページ: `GET /messages/dm`
- DM詳細ページ: `GET /messages/dm/{user_id}`

### WebSocket API (`/ws`)
- チャンネル詳細ページ: `WS /ws/channel/{channel_id}`

---

## 🎨 共通デザイン要素

### カラーパレット
- **プライマリ**: Sky-600 (`#0284c7`)
- **セカンダリ**: Indigo-500
- **背景**: Gray-50
- **テキスト**: Gray-900, Gray-600

### UIコンポーネントライブラリ
- Button (`@/components/ui/button`)
- Input (`@/components/ui/input`)
- Card (`@/components/ui/card`)
- Dialog (`@/components/ui/dialog`)
- Select (`@/components/ui/select`)
- Table (`@/components/ui/table`)
- Textarea (`@/components/ui/textarea`)

### レイアウトパターン
- **認証ページ**: 中央配置カード
- **メインページ**: サイドバー + コンテンツエリア
- **一覧ページ**: ヘッダー + リスト/グリッド
- **詳細ページ**: ヘッダー + コンテンツ + サイドバー

---

## 🔒 認証フロー

### 未認証ユーザー
1. トップページ（`/`）にアクセス
2. ログイン（`/login`）またはサインアップ（`/signup`）を選択
3. 認証成功後、メインダッシュボード（`/main`）へリダイレクト

### 認証済みユーザー
- トップページ（`/`）にアクセスすると自動的に `/main` へリダイレクト
- 保護ページに直接アクセス可能

### 認証エラー
- 保護ページへの未認証アクセス → ログインページへリダイレクト

---

## 📱 レスポンシブデザイン

### ブレークポイント
- **モバイル**: `< 768px`
- **タブレット**: `768px - 1024px`
- **デスクトップ**: `> 1024px`

### 対応
- 全ページでレスポンシブデザイン対応
- モバイルではサイドバーがハンバーガーメニューに変化（メインページ）

---

## 🧪 テスト方法

### 各ページのテスト

1. **認証不要ページ**
   - ブラウザで直接URLにアクセス
   - 表示確認、ボタン動作確認

2. **認証必須ページ**
   - ログイン後にアクセス
   - 機能確認、API接続確認

### テストアカウント

テストアカウントは`backend/tests/seed_test_accounts.py`で作成できます：

```bash
docker exec finalwork-backend-1 python tests/seed_test_accounts.py
```

**テストアカウント例**:
- Email: `test.student1@example.com`
- Password: `test1234`

---

## 📚 関連ドキュメント

- [API仕様書](../../backend/docs/API.md)
- [フロントエンドアーキテクチャ](../../docs/architecture.md)
- [バックエンドアーキテクチャ](../../backend/docs/backend-architecture.md)
- [データベーススキーマ](../../backend/docs/database_schema.md)

---

## ✏️ ドキュメントの更新

### 更新ルール

1. **ページ実装変更時**: 対応するドキュメントを同時に更新
2. **API変更時**: 「接続先API」セクションを更新
3. **デザイン変更時**: 「ページコンテンツ」セクションを更新

### 更新履歴

- 2025-11-14: 初版作成（13ページすべて）

---

## 📞 サポート

ドキュメントに関する質問や修正依頼は、プロジェクト管理者（boss1）に連絡してください。
