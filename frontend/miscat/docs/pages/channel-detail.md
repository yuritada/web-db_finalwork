# チャンネル詳細ページ

**パス**: `/channels/[channel_id]`
**ファイル**: `app/(main)/channels/[channel_id]/page.tsx`
**認証**: 必須（ログインユーザーのみアクセス可能）

---

## 📋 概要

特定のチャンネルの詳細を表示し、メッセージの送受信ができるページです。リアルタイムでメッセージが更新されます。

---

## 🎯 主な機能

### 1. チャンネル情報表示
- **チャンネル名表示**: チャンネルの名前（#付き）
- **説明表示**: チャンネルの説明文
- **プライベートバッジ**: プライベートチャンネルには鍵アイコン表示
- **チャンネルID表示**: チャンネルの一意識別子
- **パンくずナビゲーション**: チャンネル一覧へのリンク

### 2. メッセージ一覧表示
- **MessageListコンポーネント**: メッセージをリスト形式で表示
- **送信者情報**: 送信者のユーザー名
- **メッセージ内容**: メッセージ本文
- **タイムスタンプ**: 送信日時
- **自分のメッセージ**: 右側に表示、青色背景
- **他者のメッセージ**: 左側に表示、グレー背景

### 3. メッセージ送信
- **MessageInputコンポーネント**: メッセージ入力欄と送信ボタン
- **リアルタイム送信**: 送信後、即座にメッセージリストに追加
- **トースト通知**: エラー発生時にメッセージ表示

### 4. エラー・ローディング表示
- **ローディングスピナー**: データ取得中の表示
- **トースト通知**: エラー発生時にメッセージ表示
- **エラー時リダイレクト**: チャンネルが存在しない場合、一覧へ戻る

---

## 🔒 制限事項

### アクセス制限
- **認証必須**: 未認証ユーザーはアクセス不可

### 機能制限
- **メッセージ編集なし**: 送信後の編集は未実装
- **メッセージ削除なし**: 送信後の削除は未実装
- **ファイル添付なし**: テキストメッセージのみ
- **リアルタイム更新なし**: WebSocket未実装（手動更新が必要）

---

## 🔌 接続先API

### 使用API

#### 1. チャンネル詳細取得API
- **エンドポイント**: `GET /channels/{channel_id}`
- **レスポンス**:
  ```typescript
  ChannelDetail = {
    id: number;
    name: string;
    description?: string;
    is_private: boolean;
    created_at: string;
    member_count: number;
    members: UserInfo[];
  }
  ```

#### 2. チャンネルメッセージ取得API
- **エンドポイント**: `GET /channels/{channel_id}/messages`
- **レスポンス**:
  ```typescript
  Message[] = [
    {
      id: number;
      sender_id: string;
      sender_username: string;
      content: string;
      created_at: string;
    },
    ...
  ]
  ```

#### 3. メッセージ送信API
- **エンドポイント**: `POST /channels/{channel_id}/messages`
- **リクエスト**:
  ```typescript
  {
    content: string;  // 必須
  }
  ```
- **レスポンス**: 送信されたメッセージ情報

### API関数
```typescript
// lib/api.ts
const channelData = await getChannel(channelId);
const messagesData = await getChannelMessages(channelId);
const newMessage = await sendChannelMessage(channelId, { content });
```

---

## 📝 備考

### 開発時の注意
- MessageListとMessageInputコンポーネントを再利用
- エラー時は自動的にチャンネル一覧へリダイレクト
- メッセージ送信後、ローカルステートに即座に追加

### テスト方法
1. **詳細表示**: チャンネル一覧から任意のチャンネルをクリック
2. **メッセージ送信**: メッセージを入力して送信ボタンをクリック
3. **リアルタイム**: 複数のブラウザでアクセスして動作確認

### 今後の拡張予定
- WebSocketによるリアルタイム更新
- メッセージ編集・削除機能
- ファイル添付機能
- メンバー管理機能

### 関連ページ
- [チャンネル一覧ページ](./channel-list.md)
- [メインダッシュボード](./main-dashboard.md)
