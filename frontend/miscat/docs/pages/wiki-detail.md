# Wiki詳細ページ

**パス**: `/wiki/[page_id]`
**ファイル**: `app/(main)/wiki/[page_id]/page.tsx`
**認証**: 必須（ログインユーザーのみアクセス可能）

---

## 📋 概要

特定のWikiページの詳細を表示し、編集権限があれば内容を編集できるページです。ページの作成者は他のユーザーと共有したり、権限を管理できます。

---

## 🎯 主な機能

### 1. Wikiページ詳細表示
- **タイトル表示**: Wikiページのタイトル
- **コンテンツ表示**: Wikiページの本文（`<pre>`タグで整形表示）
- **作成者表示**: ページを作成したユーザーID
- **作成日時**: ページが作成された日時
- **最終更新日時**: ページが最後に更新された日時
- **パンくずナビゲーション**: Wiki一覧へのリンク

### 2. 編集機能
- **編集ボタン**: 編集権限がある場合のみ表示
- **編集モード**: タイトルとコンテンツをインライン編集
- **保存ボタン**: 変更を保存
- **キャンセルボタン**: 編集を破棄して元の内容に戻す
- **バリデーション**: タイトルが空の場合はエラー表示

### 3. 共有機能（作成者のみ）
- **共有ボタン**: ページ作成者のみ表示
- **共有モーダル**: ユーザーに閲覧・編集権限を付与
- **権限レベル**:
  - `VIEW_ONLY`: 閲覧のみ
  - `EDIT`: 編集可能
- **権限リスト表示**: 共有しているユーザーの一覧

### 4. 編集権限チェック
- **作成者**: 常に編集可能
- **共有ユーザー**: `EDIT`権限がある場合のみ編集可能
- **その他**: 閲覧のみ

---

## 🔒 制限事項

### アクセス制限
- **認証必須**: 未認証ユーザーはアクセス不可
- **権限による制限**:
  - 編集: 作成者または`EDIT`権限を持つユーザーのみ
  - 共有: 作成者のみ
  - 削除: 未実装（将来的に作成者のみ）

### 機能制限
- **削除機能なし**: 現時点では未実装
- **バージョン管理なし**: 編集履歴の管理は未実装
- **共有解除機能なし**: 一度共有した権限の解除は未実装
- **Markdown非対応**: プレーンテキストのみ

---

## 🔌 接続先API

### 使用API

#### 1. Wikiページ詳細取得API
- **エンドポイント**: `GET /wiki/pages/{page_id}`
- **レスポンス**:
  ```typescript
  WikiPageDetail = {
    id: number;
    title: string;
    content: string;
    creator_id: string;
    created_at: string;
    updated_at: string;
    permissions: WikiPermission[];  // 共有権限リスト
  }
  
  WikiPermission = {
    user_id: string;
    permission_level: PermissionLevel;  // "VIEW_ONLY" | "EDIT"
  }
  ```

#### 2. Wikiページ更新API
- **エンドポイント**: `PUT /wiki/pages/{page_id}`
- **リクエスト**:
  ```typescript
  {
    title: string;      // 必須
    content: string;    // 必須
  }
  ```
- **レスポンス**: 更新後のWikiページ詳細

#### 3. 共有API（作成者のみ）
- **エンドポイント**: `POST /wiki/pages/{page_id}/share`
- **リクエスト**:
  ```typescript
  {
    user_id: string;
    permission_level: PermissionLevel;
  }
  ```

### API関数
```typescript
// lib/api.ts
const data = await getWikiPage(pageId);
await updateWikiPage(pageId, { title, content });
```

---

## 🖼️ ページコンテンツ

### レイアウト
```
┌─────────────────────────────────────────────────┐
│ ヘッダー（サイドバー付きレイアウト）            │
├─────────────┬───────────────────────────────────┤
│             │  Wiki / {タイトル}                │
│             │                                   │
│ サイドバー  │  ┌─────────────────────────────┐  │
│             │  │ {タイトル}    [編集][共有]  │  │
│ - メイン    │  │ 作成者: user_id             │  │
│ - Wiki      │  │                             │  │
│ - タグ      │  │ {コンテンツ本文}            │  │
│ - 検索      │  │ ...                         │  │
│ - チャンネル│  │                             │  │
│ - DM        │  │ ─────────────────           │  │
│             │  │ 作成: 2024/01/01 12:00      │  │
│             │  │ 更新: 2024/01/02 15:30      │  │
│             │  └─────────────────────────────┘  │
│             │                                   │
│             │  ┌─────────────────────────────┐  │
│             │  │ 共有設定（作成者のみ）      │  │
│             │  │ このページを共有している...  │  │
│             │  │                             │  │
│             │  │ user_id_1  [編集可能]      │  │
│             │  │ user_id_2  [閲覧のみ]      │  │
│             │  └─────────────────────────────┘  │
└─────────────┴───────────────────────────────────┘

【編集モード】
┌─────────────────────────────┐
│ [タイトル入力欄]            │
│ 作成者: user_id             │
│                             │
│ [コンテンツテキストエリア]  │
│ ...                         │
│                             │
│ [キャンセル] [保存]         │
└─────────────────────────────┘
```

### UIコンポーネント

#### 1. パンくずナビゲーション
- **Wiki**: `/wiki` へのリンク
- **現在のページ**: タイトル表示（リンクなし）

#### 2. ページカード
- **使用コンポーネント**: `@/components/ui/card`
- **ヘッダー**:
  - タイトル（通常: CardTitle、編集中: Input）
  - 作成者（CardDescription）
  - アクションボタン（編集、共有）
- **コンテンツ**:
  - 本文（通常: `<pre>`、編集中: Textarea）
  - メタ情報（作成日時、更新日時）

#### 3. アクションボタン
- **編集ボタン**: 編集権限がある場合のみ表示
- **共有ボタン**: 作成者のみ表示、アウトライン
- **保存ボタン**: 編集モード中のみ表示
- **キャンセルボタン**: 編集モード中のみ表示、アウトライン

#### 4. 共有設定カード（作成者のみ）
- **表示条件**: 作成者かつ共有ユーザーが1人以上
- **タイトル**: "共有設定"
- **説明**: "このページを共有しているユーザーの一覧"
- **ユーザーリスト**:
  - ユーザーID
  - 権限レベルバッジ（編集可能: 緑、閲覧のみ: グレー）

#### 5. 共有モーダル
- **使用コンポーネント**: `ShareModal`（カスタムコンポーネント）
- **機能**: ユーザーIDを入力して権限を付与

---

## 🧭 ナビゲーション

### 遷移先ページ

| アクション | 遷移先 | パス | 説明 |
|-----------|--------|------|------|
| パンくず「Wiki」 | Wiki一覧 | `/wiki` | 一覧ページへ戻る |

### 遷移元ページ

| 遷移元 | パス | 説明 |
|--------|------|------|
| Wiki一覧ページ | `/wiki` | Wikiカードをクリック |
| Wiki一覧ページ | `/wiki` | 新規作成後、自動遷移 |

---

## 🎨 デザイン仕様

### カラーパレット
- **背景**: White（カード）、Gray-50（ページ背景）
- **テキスト**: Gray-900（タイトル）、Gray-700（本文）、Gray-500（メタ情報）
- **権限バッジ**:
  - 編集可能: Green-100（背景）、Green-800（テキスト）
  - 閲覧のみ: Gray-100（背景）、Gray-800（テキスト）
- **エラー**: Red-600（テキスト）、Red-50（背景）

### レスポンシブデザイン
- **デスクトップ**: 横並びボタン配置
- **モバイル**: ボタンが縦に並ぶ

---

## 🔧 実装詳細

### 状態管理
```typescript
const [page, setPage] = useState<WikiPageDetail | null>(null);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState('');

// 編集モード
const [isEditMode, setIsEditMode] = useState(false);
const [editTitle, setEditTitle] = useState('');
const [editContent, setEditContent] = useState('');
const [isSaving, setIsSaving] = useState(false);
const [saveError, setSaveError] = useState('');

// 共有モーダル
const [isShareModalOpen, setIsShareModalOpen] = useState(false);
```

### 編集権限チェック
```typescript
const canEdit = () => {
  if (!page || !user) return false;

  // 作成者は常に編集可能
  if (page.creator_id === user.id) return true;

  // 権限リストをチェック
  const userPermission = page.permissions.find(p => p.user_id === user.id);
  return userPermission?.permission_level === PermissionLevel.EDIT;
};
```

### 保存処理
```typescript
const handleSave = async () => {
  setSaveError('');
  setIsSaving(true);

  try {
    if (!editTitle.trim()) {
      setSaveError('タイトルを入力してください');
      setIsSaving(false);
      return;
    }

    await updateWikiPage(pageId, {
      title: editTitle.trim(),
      content: editContent.trim(),
    });

    // 再取得
    await fetchPage();
    setIsEditMode(false);
  } catch (err: unknown) {
    // エラーハンドリング
  } finally {
    setIsSaving(false);
  }
};
```

---

## 📝 備考

### 開発時の注意
- 編集権限チェックはクライアント側とサーバー側の両方で実施
- 編集モードをキャンセルした場合、元の値に戻す
- 共有モーダルは別コンポーネント（`ShareModal`）として実装

### テスト方法
1. **閲覧**: ログイン後、任意のWikiページにアクセス
2. **編集**: 編集権限があるページで「編集」ボタンをクリック
3. **共有**: 作成したページで「共有」ボタンをクリック
4. **権限確認**: 他のユーザーでログインし、共有されたページにアクセス

### 今後の拡張予定
- 削除機能の追加
- 共有解除機能の追加
- Markdownサポート
- バージョン管理（編集履歴）
- コメント機能

### 関連ページ
- [Wiki一覧ページ](./wiki-list.md)
- [メインダッシュボード](./main-dashboard.md)
