# README.mdバッジ追加案

このドキュメントは、プロジェクトルートの`README.md`に追加することを推奨するバッジの提案です。

## 📋 提案するバッジ

### 1. CI/CDステータスバッジ

GitHub ActionsのワークフローステータスをREADMEに表示します。

#### Backend Integration Tests

```markdown
[![Backend Integration Tests](https://github.com/{username}/{repo}/actions/workflows/integration-test.yml/badge.svg)](https://github.com/{username}/{repo}/actions/workflows/integration-test.yml)
```

**表示例**:
- ✅ 緑色（成功）: すべてのテストがパス
- ❌ 赤色（失敗）: テストが失敗
- ⚪ グレー（実行中）: テスト実行中

### 2. 技術スタックバッジ

プロジェクトで使用している技術スタックを表示します。

#### バックエンド

```markdown
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192.svg)](https://www.postgresql.org/)
```

#### フロントエンド

```markdown
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.3-38B2AC)](https://tailwindcss.com/)
```

### 3. ライセンスバッジ

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

または、別のライセンスを使用している場合：

```markdown
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
```

### 4. コードカバレッジバッジ（将来実装時）

Codecovを使用する場合：

```markdown
[![codecov](https://codecov.io/gh/{username}/{repo}/branch/main/graph/badge.svg)](https://codecov.io/gh/{username}/{repo})
```

### 5. コードスタイル・品質バッジ

```markdown
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](https://img.shields.io/badge/mypy-checked-blue)](https://mypy-lang.org/)
```

## 📝 完全なバッジセクション例

README.mdの冒頭に以下のように追加することを推奨します：

```markdown
# 大学向けコミュニケーションツール

[![Backend Integration Tests](https://github.com/{username}/{repo}/actions/workflows/integration-test.yml/badge.svg)](https://github.com/{username}/{repo}/actions/workflows/integration-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🛠️ 技術スタック

### バックエンド
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192.svg)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)

### フロントエンド
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.3-38B2AC)](https://tailwindcss.com/)
[![shadcn/ui](https://img.shields.io/badge/shadcn%2Fui-latest-black)](https://ui.shadcn.com/)

### インフラ
[![Docker](https://img.shields.io/badge/Docker-24-2496ED.svg)](https://www.docker.com/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF.svg)](https://github.com/features/actions)

...（既存の内容）
```

## 🔧 設定手順

### 1. GitHubリポジトリの確認

まず、GitHubリポジトリのユーザー名とリポジトリ名を確認します：

```
https://github.com/{username}/{repo}
                    ^^^^^^^^  ^^^^^^
                    ユーザー名 リポジトリ名
```

### 2. バッジURLの置き換え

上記の`{username}`と`{repo}`を実際の値に置き換えます。

例：
- ユーザー名: `tadayuri`
- リポジトリ名: `commu-tool`

```markdown
[![Backend Integration Tests](https://github.com/tadayuri/commu-tool/actions/workflows/integration-test.yml/badge.svg)](https://github.com/tadayuri/commu-tool/actions/workflows/integration-test.yml)
```

### 3. README.mdに追加

プロジェクトルートの`README.md`の冒頭（プロジェクト名の下）に追加します。

### 4. 確認

GitHubにpushした後、README.mdを確認してバッジが正しく表示されていることを確認します。

## 📊 バッジのカスタマイズ

[shields.io](https://shields.io/)を使用すると、カスタムバッジを作成できます。

### カスタムバッジの例

```markdown
[![API Status](https://img.shields.io/badge/API-Online-success)](http://localhost:8000/docs)
[![Docs](https://img.shields.io/badge/docs-available-informational)](./docs/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)
```

## 🎨 バッジのスタイル

shields.ioは複数のスタイルをサポートしています：

```markdown
<!-- Flat (default) -->
![style: flat](https://img.shields.io/badge/style-flat-green?style=flat)

<!-- Flat Square -->
![style: flat-square](https://img.shields.io/badge/style-flat--square-green?style=flat-square)

<!-- Plastic -->
![style: plastic](https://img.shields.io/badge/style-plastic-green?style=plastic)

<!-- For the Badge -->
![style: for-the-badge](https://img.shields.io/badge/style-for--the--badge-green?style=for-the-badge)

<!-- Social -->
![style: social](https://img.shields.io/badge/style-social-green?style=social)
```

## 🚀 今後の追加候補

プロジェクトの成長に合わせて、以下のバッジを追加することを検討してください：

1. **デプロイステータス**
   ```markdown
   [![Deploy Status](https://img.shields.io/badge/deploy-success-green)](https://your-production-url.com)
   ```

2. **セキュリティスキャン**
   ```markdown
   [![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
   ```

3. **依存関係の状態**
   ```markdown
   [![Dependencies](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen)](https://github.com/{username}/{repo}/network/dependencies)
   ```

4. **コントリビューター数**
   ```markdown
   [![Contributors](https://img.shields.io/github/contributors/{username}/{repo})](https://github.com/{username}/{repo}/graphs/contributors)
   ```

5. **最終更新日**
   ```markdown
   [![Last Commit](https://img.shields.io/github/last-commit/{username}/{repo})](https://github.com/{username}/{repo}/commits/main)
   ```

## 📚 参考リンク

- [shields.io - バッジ生成サービス](https://shields.io/)
- [GitHub Actions バッジ公式ドキュメント](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge)
- [Markdown Badges - 一覧](https://github.com/Ileriayo/markdown-badges)

---

**作成日**: 2025-11-13
**作成者**: Worker3 (インフラ・統合担当)
**目的**: README.mdの視認性と情報量の向上
