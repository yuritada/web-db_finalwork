# Miscat フロントエンド

Next.js 16 (App Router) + TypeScript + shadcn/ui + Tailwind CSSで構築された、大学向けコミュニケーションプラットフォームのフロントエンドアプリケーション。

## 技術スタック

- **Next.js**: 16.0.1 (App Router, Turbopack)
- **TypeScript**: 5.x (strict mode)
- **UI Library**: shadcn/ui
- **Styling**: Tailwind CSS 3.x
- **State Management**: React hooks (useState, useEffect, useContext)
- **API Client**: axios 1.x
- **WebSocket**: Native WebSocket API
- **Notifications**: sonner (toast)

## 開発環境セットアップ

### Docker Composeを使用（推奨）

```bash
# リポジトリルートから
docker compose up frontend
```

### ローカル開発

```bash
# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev

# プロダクションビルド
npm run build

# プロダクションサーバー起動
npm start
```

ブラウザで [http://localhost:3000](http://localhost:3000) を開いてください。

## プロジェクト構造

```
frontend/miscat/
├── app/                      # Next.js App Router
│   ├── (main)/              # 認証後のメインレイアウト
│   │   ├── layout.tsx       # メインレイアウト（ヘッダー、サイドバー）
│   │   ├── page.tsx         # ダッシュボード
│   │   ├── channels/        # チャンネル機能
│   │   │   ├── page.tsx    # チャンネル一覧
│   │   │   └── [channel_id]/page.tsx  # チャンネル詳細
│   │   ├── dm/              # DM機能
│   │   │   ├── page.tsx    # DM一覧
│   │   │   └── [dm_id]/page.tsx       # DM詳細
│   │   ├── wiki/            # Wiki機能
│   │   ├── tags/            # タグ機能
│   │   └── search/          # 検索機能
│   ├── login/               # ログインページ
│   ├── signup/              # サインアップページ
│   ├── layout.tsx           # ルートレイアウト
│   └── globals.css          # グローバルスタイル
├── components/
│   ├── ui/                  # shadcn/uiコンポーネント
│   ├── channel/             # チャンネル関連コンポーネント
│   │   ├── MessageCard.tsx
│   │   ├── MessageInput.tsx
│   │   ├── MessageList.tsx
│   │   └── ChannelCard.tsx
│   └── dm/                  # DM関連コンポーネント
│       └── DMCard.tsx
├── context/
│   ├── AuthContext.tsx      # 認証コンテキスト
│   └── WebSocketContext.tsx # WebSocket接続管理
├── lib/
│   ├── api.ts               # APIクライアント（axios）
│   └── utils.ts             # ユーティリティ関数
└── docs/
    ├── phase4_ui_design.md  # Phase 4 UI設計書
    └── implementation_status.md  # 実装状況

```

## 実装状況（Phase 4）

### ✅ Phase 1完了: コンポーネント骨格実装
- WebSocketContext骨格
- MessageCard, MessageInput, MessageList
- ChannelCard, DMCard
- 全ページ骨格（channels, dm）
- ビルド成功（15/15ページ）

### ✅ Phase 2完了: Channels API統合
- lib/api.ts Channels API関数実装
  - getChannels(), createChannel()
  - getChannelMessages(), sendChannelMessage()
- channels/page.tsx API統合（一覧取得、作成）
- channels/[channel_id]/page.tsx API統合（詳細、メッセージ送受信）
- ビルド成功、TypeScriptエラー0件

### ✅ Phase 3完了: DM API統合
- lib/api.ts DM API関数実装
  - getDMConversations(), getDMMessages(), sendDMMessage()
- dm/page.tsx API統合（会話一覧取得）
- dm/[dm_id]/page.tsx API統合（メッセージ履歴、送信）
- ビルド成功、TypeScriptエラー0件

### ⏳ Phase 4予定: WebSocket統合
- WebSocketContext完成実装
- リアルタイムメッセージ受信
- チャンネル参加/退出通知
- 再接続ロジック完成

## 主要機能

### 認証
- ログイン/サインアップ
- JWT認証（HttpOnly Cookie）
- AuthContext（グローバル認証状態管理）

### チャンネル
- チャンネル一覧表示
- チャンネル作成
- メッセージ送受信
- リアルタイム更新（Phase 4予定）

### DM
- DM会話一覧表示
- DM履歴表示
- メッセージ送信
- リアルタイム更新（Phase 4予定）

### Wiki
- Wiki一覧表示
- Wiki作成・編集
- 権限管理

### タグ
- タグ一覧表示
- タグ作成
- ユーザー割り当て

### 検索
- Wiki/タグ/ユーザー統合検索

## APIエンドポイント

バックエンドAPI: `http://localhost:8000/api`

詳細は `/backend/docs/` を参照。

## ドキュメント

- [UI/UXデザインガイド](/docs/ui-design.md)
- [Phase 4 UI設計書](docs/phase4_ui_design.md)
- [実装状況](docs/implementation_status.md)

## ビルド・デプロイ

```bash
# プロダクションビルド
npm run build

# ビルド結果確認
npm run start
```

## 開発者

**Worker1** - フロントエンド実装担当

## ライセンス

本プロジェクトは教育目的で作成されています。
