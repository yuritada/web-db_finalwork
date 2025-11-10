# コンポーネント一覧

**最終更新**: 2025-11-10
**作成者**: Worker1

本ドキュメントでは、Phase 4で実装した全コンポーネントの詳細を記載します。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 目次

1. [Channel関連コンポーネント](#channel関連コンポーネント)
2. [DM関連コンポーネント](#dm関連コンポーネント)
3. [Context](#context)
4. [ページコンポーネント](#ページコンポーネント)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Channel関連コンポーネント

### MessageCard

**ファイル**: `components/channel/MessageCard.tsx`

**説明**: 個別メッセージを表示するカードコンポーネント。自分のメッセージと他人のメッセージで異なるスタイルを適用。

**Props**:
```typescript
interface MessageCardProps {
  message: {
    id: number;
    sender_id: string;
    sender_username: string;
    content: string;
    created_at: string;
  };
  isOwnMessage: boolean; // 自分のメッセージか
}
```

**機能**:
- 送信者名表示
- タイムスタンプ表示（日本語フォーマット）
- メッセージ内容表示
- 自分のメッセージは右寄せ、背景色変更
- 改行対応（whitespace-pre-wrap）

**使用例**:
```tsx
<MessageCard
  message={{
    id: 1,
    sender_id: 'user123',
    sender_username: 'John Doe',
    content: 'こんにちは！',
    created_at: '2025-11-10T15:30:00Z'
  }}
  isOwnMessage={false}
/>
```

---

### MessageInput

**ファイル**: `components/channel/MessageInput.tsx`

**説明**: メッセージ入力フォーム。Enter送信、文字数制限、送信中状態管理をサポート。

**Props**:
```typescript
interface MessageInputProps {
  onSend: (content: string) => Promise<void>;
  placeholder?: string;
  maxLength?: number; // デフォルト: 1000
}
```

**機能**:
- Textarea入力（複数行対応）
- Enter送信（Shift+Enterで改行）
- 文字数制限（デフォルト1000文字）
- 文字数カウンター表示
- 送信中状態表示
- エラーハンドリング（toast通知）
- 送信後の入力欄クリア

**使用例**:
```tsx
<MessageInput
  onSend={async (content) => {
    await sendChannelMessage(channelId, { content });
  }}
  placeholder="メッセージを入力..."
  maxLength={500}
/>
```

---

### MessageList

**ファイル**: `components/channel/MessageList.tsx`

**説明**: メッセージ一覧を表示し、自動スクロールを管理するコンポーネント。

**Props**:
```typescript
interface MessageListProps {
  messages: Message[];
  currentUserId: string;
  onLoadMore?: () => void; // 古いメッセージ読み込み（将来実装）
}
```

**機能**:
- メッセージ一覧表示
- スクロール管理
- 新着メッセージ時の自動スクロール
- 空状態表示
- MessageCardを利用した表示

**使用例**:
```tsx
<MessageList
  messages={messages}
  currentUserId={user.id}
  onLoadMore={() => loadMoreMessages()}
/>
```

---

### ChannelCard

**ファイル**: `components/channel/ChannelCard.tsx`

**説明**: チャンネル一覧ページで使用するチャンネルカード。

**Props**:
```typescript
interface ChannelCardProps {
  channel: {
    id: number;
    name: string;
    description?: string;
    is_private: boolean;
  };
  onClick: () => void;
}
```

**機能**:
- チャンネル名表示（#prefix）
- 説明表示
- プライベートチャンネルバッジ（🔒）
- ホバー時のシャドウエフェクト
- クリック時のルーティング

**使用例**:
```tsx
<ChannelCard
  channel={{
    id: 1,
    name: 'プロジェクトA',
    description: 'プロジェクトAに関する議論',
    is_private: false
  }}
  onClick={() => router.push('/main/channels/1')}
/>
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## DM関連コンポーネント

### DMCard

**ファイル**: `components/dm/DMCard.tsx`

**説明**: DM一覧ページで使用するDMカード。

**Props**:
```typescript
interface DMCardProps {
  dm: {
    partner_id: string;
    partner_username: string;
    last_message?: string;
    last_message_at?: string;
  };
  onClick: () => void;
}
```

**機能**:
- 相手ユーザー名表示
- 相手ユーザーID表示
- 最終メッセージプレビュー
- 相対時刻表示（"たった今", "3分前", "2時間前", "5日前"）
- ホバー時のシャドウエフェクト
- クリック時のルーティング

**使用例**:
```tsx
<DMCard
  dm={{
    partner_id: 'user123',
    partner_username: 'John Doe',
    last_message: 'ありがとうございます',
    last_message_at: '2025-11-10T15:30:00Z'
  }}
  onClick={() => router.push('/main/dm/user123')}
/>
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Context

### AuthContext

**ファイル**: `context/AuthContext.tsx`

**説明**: 認証状態をグローバルに管理するコンテキスト。

**提供する値**:
```typescript
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  signup: (data: SignupRequest) => Promise<void>;
}
```

**機能**:
- ユーザー情報管理
- 認証状態管理
- ログイン/ログアウト/サインアップ処理
- 自動認証チェック（初回ロード時）

---

### WebSocketContext

**ファイル**: `context/WebSocketContext.tsx`

**説明**: WebSocket接続を管理するコンテキスト。Phase 4で完成予定。

**提供する値**:
```typescript
interface WebSocketContextType {
  socket: WebSocket | null;
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
}
```

**機能**（Phase 1骨格実装）:
- WebSocket接続管理
- 再接続ロジック（最大5回、指数バックオフ）
- 接続状態管理
- メッセージ受信ハンドラー登録（Phase 4予定）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ページコンポーネント

### Channels一覧ページ

**ファイル**: `app/(main)/channels/page.tsx`

**説明**: ユーザーが参加しているチャンネル一覧を表示。

**機能**:
- チャンネル一覧取得（getChannels API）
- チャンネル作成Dialog
- チャンネルカードグリッド表示
- ローディング状態表示
- エラーハンドリング
- 空状態メッセージ

**API呼び出し**:
- `GET /channels` - チャンネル一覧取得
- `POST /channels` - チャンネル作成

---

### Channels詳細ページ

**ファイル**: `app/(main)/channels/[channel_id]/page.tsx`

**説明**: 特定チャンネルの詳細とメッセージ履歴を表示。

**機能**:
- チャンネル情報取得（getChannel API）
- メッセージ一覧取得（getChannelMessages API）
- メッセージ送信（sendChannelMessage API）
- パンくず表示
- ローディング状態表示
- エラーハンドリング
- リアルタイムメッセージ受信（Phase 4予定）

**API呼び出し**:
- `GET /channels` - チャンネル情報取得（現在はgetChannelsから抽出）
- `GET /channels/{id}/messages` - メッセージ履歴取得
- `POST /channels/{id}/messages` - メッセージ送信

---

### DM一覧ページ

**ファイル**: `app/(main)/dm/page.tsx`

**説明**: DM会話一覧を表示。

**機能**:
- DM会話一覧取得（getDMConversations API）
- DMカードグリッド表示
- ローディング状態表示
- エラーハンドリング
- 空状態メッセージ

**API呼び出し**:
- `GET /messages/dm` - DM会話一覧取得

---

### DM詳細ページ

**ファイル**: `app/(main)/dm/[dm_id]/page.tsx`

**説明**: 特定ユーザーとのDM履歴を表示。dm_idはpartner_idとして扱う。

**機能**:
- DMメッセージ履歴取得（getDMMessages API）
- メッセージ送信（sendDMMessage API）
- 相手情報表示
- パンくず表示
- ローディング状態表示
- エラーハンドリング
- パートナー名の自動推測（メッセージから取得）
- リアルタイムメッセージ受信（Phase 4予定）

**API呼び出し**:
- `GET /messages/dm/{user_id}` - DM履歴取得
- `POST /messages/dm` - DM送信

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 共通パターン

### エラーハンドリング

全コンポーネントで統一されたエラーハンドリング：

```typescript
try {
  const data = await apiCall();
  setState(data);
} catch (err: unknown) {
  if (err instanceof Error) {
    toast.error('エラーメッセージ: ' + err.message);
  } else {
    toast.error('エラーメッセージ');
  }
}
```

### ローディング状態

```typescript
const [isLoading, setIsLoading] = useState(true);

if (isLoading) {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="text-center">
        <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-sky-500 border-r-transparent"></div>
        <p className="mt-2 text-sm text-gray-600">読み込み中...</p>
      </div>
    </div>
  );
}
```

### 空状態

```typescript
{items.length === 0 ? (
  <Card>
    <CardContent className="pt-6">
      <div className="text-center py-12">
        <p className="text-gray-500">まだアイテムがありません。</p>
        <p className="text-sm text-gray-400 mt-2">
          追加してみましょう。
        </p>
      </div>
    </CardContent>
  </Card>
) : (
  // アイテム表示
)}
```

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## スタイリング規則

### shadcn/ui使用

全コンポーネントでshadcn/uiを使用：
- Card, CardHeader, CardTitle, CardContent
- Button（variant: default, outline, ghost）
- Input, Textarea
- Dialog（モーダル表示）

### Tailwind CSSクラス

一貫したスタイリング：
- Primary: `bg-sky-500`, `text-sky-600`
- Gray: `text-gray-600`, `bg-gray-50`
- Spacing: `space-y-4`, `p-4`, `px-6`
- Hover: `hover:bg-gray-100`, `hover:shadow-md`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 今後の拡張

### Phase 4（WebSocket統合）
- MessageList: リアルタイムメッセージ受信
- Channels/DMページ: WebSocketContext統合
- オンライン状態表示

### Phase 5以降
- ファイルアップロード
- メッセージ編集・削除
- リアクション（絵文字）
- スレッド機能
- メンション機能

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**作成日**: 2025-11-10
**最終更新**: 2025-11-10
**作成者**: Worker1
**バージョン**: 1.0
