# テストアカウント管理

このディレクトリには、開発・テスト用のユーザーアカウントを作成するスクリプトが含まれています。

## 📁 ファイル構成

```
backend/tests/
├── README.md                    # このファイル
├── seed_test_accounts.py        # テストアカウント登録スクリプト
└── (その他のテストファイル)
```

---

## 🔧 テストアカウント登録スクリプト

### seed_test_accounts.py

開発環境でテスト用のユーザーアカウントをデータベースに登録するスクリプトです。

#### 作成されるアカウント（合計6名）

| 種別 | ユーザー名 | メールアドレス | パスワード | 学籍番号 | 学部・学科 |
|------|-----------|---------------|-----------|---------|-----------|
| 学生 | student1 | student1@test.com | test1234 | 2024001 | 工学部 |
| 学生 | student2 | student2@test.com | test1234 | 2024002 | 情報学部 |
| 教授 | professor1 | professor1@test.com | test1234 | 自動生成 | 情報工学科 |
| 准教授 | associate_prof1 | associate_prof1@test.com | test1234 | 自動生成 | 数学科 |
| 講師 | lecturer1 | lecturer1@test.com | test1234 | 自動生成 | 物理学科 |
| 事務 | staff1 | staff1@test.com | test1234 | 自動生成 | - |

**共通パスワード**: `test1234`

---

## 🚀 使用方法

### 1. Dockerコンテナ内で実行（推奨）

```bash
# バックエンドコンテナ内でスクリプトを実行
docker exec finalwork-backend-1 python tests/seed_test_accounts.py
```

### 2. ローカルで実行

```bash
# 仮想環境を有効化
cd backend
source .venv/bin/activate  # Linuxmacは/Mac
# または
.venv\Scripts\activate  # Windows

# スクリプトを実行
python tests/seed_test_accounts.py
```

---

## ⚠️ 注意事項

### 開発環境専用

このスクリプトは**開発環境でのみ使用**してください。

- ✅ **OK**: ローカル開発環境、Docker開発環境
- ❌ **NG**: 本番環境、ステージング環境

### 既存アカウントの扱い

- 既に同じメールアドレスのアカウントが存在する場合、スキップされます
- エラーは発生せず、警告メッセージが表示されます

### パスワードについて

- テストアカウントのパスワードは`test1234`で統一されています
- 本番環境では使用しないでください

---

## 📝 ログイン情報

### フロントエンドでのログイン

フロントエンド（http://localhost:3000）で以下の情報を使用してログインできます：

#### 学生アカウント
```
Email: student1@test.com
Password: test1234
```

#### 教授アカウント
```
Email: professor1@test.com
Password: test1234
```

#### 事務アカウント
```
Email: staff1@test.com
Password: test1234
```

### APIでのテスト

Swagger UI（http://localhost:8000/docs）で各エンドポイントをテストできます：

1. `/auth/token` エンドポイントでログイン
2. 取得したトークンを使用して認証が必要なエンドポイントをテスト

---

## 🔄 アカウントの削除

テストアカウントを削除する場合は、データベースから直接削除してください：

```sql
-- メールアドレスで削除
DELETE FROM users WHERE email LIKE '%@test.com';

-- または、特定のユーザーを削除
DELETE FROM users WHERE username = 'student1';
```

---

## 🛠️ トラブルシューティング

### エラー: "データベースに接続できません"

データベースが起動しているか確認してください：

```bash
docker ps | grep postgres
```

### エラー: "モジュールが見つかりません"

Pythonパスが正しく設定されているか確認してください：

```bash
# 仮想環境を有効化
cd backend
source .venv/bin/activate
```

### アカウントが作成されない

1. データベースが正常に動作しているか確認
2. マイグレーションが適用されているか確認：
   ```bash
   docker exec finalwork-backend-1 alembic current
   ```

---

## 📚 関連ドキュメント

- [バックエンドREADME](../README.md)
- [データベーススキーマ](../docs/database_schema.md)
- [認証API仕様](../docs/API.md#認証api-auth)

---

## 📞 サポート

問題が発生した場合は、以下を確認してください：

1. データベースが起動しているか
2. マイグレーションが適用されているか
3. 環境変数が正しく設定されているか

それでも解決しない場合は、プロジェクト管理者に連絡してください。
