# Wiki一覧ページ

**パス**: `/wiki`
**ファイル**: `app/(main)/wiki/page.tsx`
**認証**: 必須（ログインユーザーのみアクセス可能）

---

## 📋 概要

全てのWikiページを一覧表示し、新規Wikiページの作成が可能なページです。各Wikiページのタイトル、作成者、更新日時、コンテンツのプレビューなどが表示されます。

---

## 🎯 主な機能

### 1. Wikiページ一覧表示
- **カード形式表示**: 各Wikiページをカードで表示
- **タイトル表示**: Wikiページのタイトル
- **作成者表示**: ページを作成したユーザーID
- **コンテンツプレビュー**: 本文の最初の2行を表示
- **作成日時**: ページが作成された日時
- **最終更新日時**: ページが最後に更新された日時
- **クリック遷移**: カードをクリックすると詳細ページへ遷移

### 2. 新規Wikiページ作成
- **新規作成ボタン**: ヘッダーに配置された作成ボタン
- **作成モーダル**: ダイアログ形式で新規作成フォームを表示
- **タイトル入力**: 必須項目（例: "プロジェクト概要"）
- **初期コンテンツ入力**: 任意項目（後から編集可能）
- **作成完了**: 作成後、自動的に詳細ページへ遷移

### 3. エラー・ローディング表示
- **ローディングスピナー**: データ取得中の表示
- **エラーメッセージ**: 読み込み失敗時の表示
- **空状態**: Wikiページが1つもない場合の案内メッセージ

### 4. 日時フォーマット
- **日本語形式**: `YYYY/MM/DD HH:MM` 形式で表示

---

## 🔒 制限事項

### アクセス制限
- **認証必須**: 未認証ユーザーはアクセス不可
- **自動リダイレクト**: 未認証状態でアクセスした場合、ログインページへリダイレクト

### 機能制限
- **削除機能なし**: 一覧ページからの削除は不可（詳細ページで実施）
- **検索・フィルタリングなし**: 現時点では全ページを表示のみ
- **ページネーションなし**: 全ページを一度に表示

---

## 🔌 接続先API

### 使用API

#### 1. Wikiページ一覧取得API
- **エンドポイント**: `GET /wiki/pages`
- **レスポンス**:
  ```typescript
  WikiPagePublic[] = [
    {
      id: number;
      title: string;
      content: string;
      creator_id: string;
      created_at: string;
      updated_at: string;
    },
    ...
  ]
  ```

#### 2. Wikiページ作成API
- **エンドポイント**: `POST /wiki/pages`
- **リクエスト**:
  ```typescript
  {
    title: string;          // 必須
    content?: string;       // 任意
  }
  ```
- **レスポンス**:
  ```typescript
  {
    id: number;
    title: string;
    content: string;
    creator_id: string;
    created_at: string;
    updated_at: string;
  }
  ```

### API関数
```typescript
// lib/api.ts
const data = await getWikiPages();
const newPage = await createWikiPage({ title, content });
```

---

## 🖼️ ページコンテンツ

### レイアウト
```
┌─────────────────────────────────────────────────┐
│ ヘッダー（サイドバー付きレイアウト）            │
├─────────────┬───────────────────────────────────┤
│             │  Wiki                [新規作成]   │
│             │  説明文                           │
│ サイドバー  │                                   │
│             │  ┌─────────────────────────────┐  │
│ - メイン    │  │ Wikiカード1                 │  │
│ - Wiki      │  │ タイトル                    │  │
│ - タグ      │  │ 作成者: user_id             │  │
│ - 検索      │  │ コンテンツプレビュー...     │  │
│ - チャンネル│  │ 作成: 2024/01/01 12:00      │  │
│ - DM        │  │ 更新: 2024/01/02 15:30      │  │
│             │  └─────────────────────────────┘  │
│             │                                   │
│             │  ┌─────────────────────────────┐  │
│             │  │ Wikiカード2                 │  │
│             │  │ ...                         │  │
│             │  └─────────────────────────────┘  │
│             │                                   │
│             │  ┌─────────────────────────────┐  │
│             │  │ Wikiカード3                 │  │
│             │  │ ...                         │  │
│             │  └─────────────────────────────┘  │
└─────────────┴───────────────────────────────────┘

【新規作成モーダル】
┌───────────────────────────┐
│ 新しいWikiページを作成     │
│ タイトルと初期コンテンツ... │
│                           │
│ タイトル *                │
│ [入力欄]                  │
│                           │
│ 初期コンテンツ（任意）    │
│ [テキストエリア]          │
│                           │
│ [キャンセル] [作成する]    │
└───────────────────────────┘
```

### UIコンポーネント

#### 1. ヘッダーセクション
- **タイトル**: "Wiki"（3xl、太字）
- **説明文**: "知識を共有するためのWikiページを作成・閲覧できます。"
- **新規作成ボタン**: プライマリボタン

#### 2. Wikiカード
- **使用コンポーネント**: `@/components/ui/card`
- **ホバー効果**: シャドウが濃くなる（`hover:shadow-md`）
- **クリッカブル**: カード全体がリンク
- **内容**:
  - タイトル（CardTitle、text-lg）
  - 作成者（CardDescription）
  - コンテンツプレビュー（2行まで、`line-clamp-2`）
  - メタ情報（作成日時、更新日時）

#### 3. 新規作成モーダル
- **使用コンポーネント**: `@/components/ui/dialog`
- **タイトル**: "新しいWikiページを作成"
- **説明**: "タイトルと初期コンテンツを入力してください。"
- **フォーム要素**:
  - タイトル入力欄（必須）
  - 初期コンテンツ入力欄（任意、Textarea、6行）
  - エラーメッセージ表示エリア
  - キャンセルボタン（アウトライン）
  - 作成ボタン（プライマリ）

#### 4. 空状態
- **表示条件**: Wikiページが0件の場合
- **メッセージ**: "まだWikiページがありません。"
- **補足**: "「新規作成」ボタンから最初のページを作成してみましょう。"

#### 5. ローディング表示
- **スピナー**: 回転するボーダー（sky-500）
- **テキスト**: "読み込み中..."

#### 6. エラー表示
- **スタイル**: 赤色の背景、赤色の枠線、赤色のテキスト

---

## 🧭 ナビゲーション

### 遷移先ページ

| アクション | 遷移先 | パス | 説明 |
|-----------|--------|------|------|
| カードクリック | Wiki詳細 | `/wiki/{page_id}` | 該当Wikiページの詳細表示 |
| 新規作成成功 | Wiki詳細 | `/wiki/{page_id}` | 作成したWikiページの詳細表示 |

### 遷移元ページ

| 遷移元 | パス | 説明 |
|--------|------|------|
| メインダッシュボード | `/main` | サイドバー「Wiki」リンク |
| Wiki詳細ページ | `/wiki/{page_id}` | パンくずリンク |

---

## 🎨 デザイン仕様

### カラーパレット
- **背景**: White（カード）、Gray-50（ページ背景）
- **テキスト**: Gray-900（タイトル）、Gray-600（本文）、Gray-500（メタ情報）
- **プライマリ**: Sky-500（ローディングスピナー）
- **エラー**: Red-600（テキスト）、Red-50（背景）

### レスポンシブデザイン
- **デスクトップ**: 1列グリッド、カード幅は自動調整
- **モバイル**: 1列グリッド、全幅表示

---

## 🔧 実装詳細

### 状態管理
```typescript
const [pages, setPages] = useState<WikiPagePublic[]>([]);
const [isLoading, setIsLoading] = useState(true);
const [error, setError] = useState('');

// 新規作成用
const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
const [newTitle, setNewTitle] = useState('');
const [newContent, setNewContent] = useState('');
const [isCreating, setIsCreating] = useState(false);
const [createError, setCreateError] = useState('');
```

### ページ一覧取得
```typescript
const fetchPages = async () => {
  try {
    setIsLoading(true);
    setError('');
    const data = await getWikiPages();
    setPages(data);
  } catch (err: unknown) {
    if (err instanceof Error) {
      setError(err.message || 'ページの読み込みに失敗しました');
    } else {
      setError('ページの読み込みに失敗しました');
    }
  } finally {
    setIsLoading(false);
  }
};

useEffect(() => {
  fetchPages();
}, []);
```

### 新規作成処理
```typescript
const handleCreate = async (e: React.FormEvent) => {
  e.preventDefault();
  setCreateError('');
  setIsCreating(true);

  try {
    if (!newTitle.trim()) {
      setCreateError('タイトルを入力してください');
      setIsCreating(false);
      return;
    }

    const newPage = await createWikiPage({
      title: newTitle.trim(),
      content: newContent.trim() || undefined,
    });

    // 作成成功
    setIsCreateModalOpen(false);
    setNewTitle('');
    setNewContent('');

    // 詳細ページへ遷移
    router.push(`/main/wiki/${newPage.id}`);
  } catch (err: unknown) {
    // エラーハンドリング
  } finally {
    setIsCreating(false);
  }
};
```

---

## 📝 備考

### 開発時の注意
- ページ一覧は最新順に表示されることを推奨（APIで実装）
- コンテンツプレビューは`line-clamp-2`で2行に制限
- カード全体をリンクにするため、`<Link>`で囲む

### テスト方法
1. **一覧表示**: ログイン後、Wiki一覧ページにアクセス
2. **新規作成**: 「新規作成」ボタンをクリックし、フォーム入力後作成
3. **空状態**: Wikiページが0件の状態で表示確認
4. **エラー**: APIを停止して、エラーメッセージ表示確認

### 今後の拡張予定
- 検索・フィルタリング機能
- ページネーション（大量のページ対応）
- ソート機能（タイトル順、更新日時順など）
- お気に入り機能

### 関連ページ
- [Wiki詳細ページ](./wiki-detail.md)
- [メインダッシュボード](./main-dashboard.md)
