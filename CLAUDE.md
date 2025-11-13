# Claude Code プロジェクト運用ルール

**最終更新**: 2025-11-13
**管理者**: PRESIDENT
**バージョン**: 2.0

---

## 1. 🚨 最重要事項

### 1.1 ユーザーとPRESIDENTの違い

**重要**: このプロジェクトでは2つの重要な概念があります。

- **ユーザー**: プロジェクトの実際の所有者（あなた）
- **PRESIDENT**: Claude Codeエージェントの1つで、プロジェクト統括役

**混同しないための原則**:
- **ユーザー**は全エージェント（PRESIDENT含む）の上位者です
- **PRESIDENT**は他のエージェント（boss1, worker1-3）に対する指示者です
- エージェントへの指示は「あなたは[役割]です」で開始します
- ユーザーへの確認・報告は明確に「ユーザー」と呼びます

### 1.2 エージェント間通信の必須ルール

**🚨 絶対ルール**: エージェント間の連絡は **必ず `agent-send.sh` スクリプトを使用すること**

#### ✅ 正しい連絡方法

```bash
# 基本構文
./Claude-Code-Communication/agent-send.sh [相手の名前] "メッセージ内容"

# PRESIDENTへの連絡
./Claude-Code-Communication/agent-send.sh president "【報告】タスク完了しました"

# boss1への連絡
./Claude-Code-Communication/agent-send.sh boss1 "【質問】次のタスクをお願いします"

# worker1への連絡
./Claude-Code-Communication/agent-send.sh worker1 "【指示】フロントエンド実装を開始してください"

# worker2への連絡
./Claude-Code-Communication/agent-send.sh worker2 "【指示】API実装を開始してください"

# worker3への連絡
./Claude-Code-Communication/agent-send.sh worker3 "【指示】環境構築を開始してください"
```

**スクリプトの場所**: `./Claude-Code-Communication/agent-send.sh`

#### ❌ 誤った方法

```bash
# これらは送信されません（単なるテキスト出力）
echo "報告内容"
cat > report.txt
printf "メッセージ"
# テキストとして出力するだけ
```

**警告**: 単なるテキスト出力では、相手エージェントに送信されません。必ず `agent-send.sh` を使用してください。

---

## 2. プロジェクト構成

### 2.1 エージェント役割分担

```
┌─────────────┐
│  PRESIDENT  │ ← 全体統括、ビジョン策定、最終意思決定
└──────┬──────┘
       │ 指示・進捗確認
       ↓
┌─────────────┐
│    boss1    │ ← プロジェクトマネージャー、タスク分解・割り当て、進捗管理
└──────┬──────┘
       │ タスク割り当て・進捗確認
       ├──────┬──────┬──────┐
       ↓      ↓      ↓      ↓
  ┌────────┐ ┌────────┐ ┌────────┐
  │worker1 │ │worker2 │ │worker3 │
  └────────┘ └────────┘ └────────┘
   フロント    バック     インフラ
    エンド     エンド    ・統合
```

### 2.2 各役割の概要

#### 👑 PRESIDENT
- **役割**: プロジェクトオーナー、全体統括、ビジョン策定
- **担当**:
  - ユーザーの真のニーズを理解・定義
  - プロジェクトビジョンの策定
  - 成功基準の明確化
  - boss1への指示出し
  - 最終報告の受領
- **詳細指示書**: `Claude-Code-Communication/instructions/president.md`

#### 🎯 boss1
- **役割**: テックリード、プロジェクトマネージャー
- **担当**:
  - タスクの分解と優先順位付け
  - worker1-3への具体的な指示出し
  - 進捗管理とブロッカー解消
  - 技術的判断
  - PRESIDENTへの進捗報告
- **詳細指示書**: `Claude-Code-Communication/instructions/boss.md`

#### 👷 worker1
- **役割**: フロントエンド開発担当
- **担当**:
  - UI/UX実装
  - クライアントサイドロジック
  - デザイン実装
- **詳細指示書**: `Claude-Code-Communication/instructions/worker.md`

#### 👷 worker2
- **役割**: バックエンド開発担当
- **担当**:
  - API実装
  - ビジネスロジック
  - データベース設計・実装
- **詳細指示書**: `Claude-Code-Communication/instructions/worker.md`

#### 👷 worker3
- **役割**: インフラ・統合・ドキュメント担当
- **担当**:
  - 環境構築（Docker等）
  - CI/CD設定
  - 統合テスト
  - ドキュメント作成
- **詳細指示書**: `Claude-Code-Communication/instructions/worker.md`

### 2.3 作業ディレクトリ

```
/Users/tadayuri/Lecture/web_db/finalwork/
├── Claude-Code-Communication/    # 組織化システム
│   ├── agent-send.sh            # 通信スクリプト（最重要）
│   ├── setup.sh                 # 環境セットアップ
│   ├── instructions/            # 各役割の詳細指示書
│   │   ├── president.md
│   │   ├── boss.md
│   │   ├── worker.md
│   │   └── master_prompt_v3.md  # プロジェクト仕様書（参照用）
│   ├── CLAUDE.md                # システム基本説明
│   └── README.md                # 詳細ガイド
├── CLAUDE.md                     # このファイル（運用ルール）
├── backend/                      # バックエンドコード
├── frontend/                     # フロントエンドコード
├── docs/                         # プロジェクトドキュメント
└── tmp/                          # 進捗管理用一時ファイル
    ├── worker1_done.txt
    ├── worker2_done.txt
    └── worker3_done.txt
```

---

## 3. コミュニケーションプロトコル

### 3.1 基本フロー

```
PRESIDENT → boss1 → workers → boss1 → PRESIDENT
    ↑                                      ↓
    └────────────── 報告 ──────────────────┘
```

### 3.2 メッセージ送信方法

#### 基本テンプレート

```bash
./Claude-Code-Communication/agent-send.sh [送信先] "
【カテゴリ】送信者名

本文内容
"
```

#### カテゴリの種類
- `【指示】`: タスクの割り当て
- `【質問】`: 不明点の確認
- `【報告】`: 進捗・完了報告
- `【ブロッカー】`: 問題報告
- `【緊急】`: 緊急対応要求

### 3.3 報告プロトコル

#### 3.3.1 進捗報告（worker → boss1）

**報告先**: boss1
**報告タイミング**:
- タスク完了時（必須）
- ブロッカー発生時（即座）
- 定期チェックポイント（boss1が指定）

**報告形式**:
```bash
./Claude-Code-Communication/agent-send.sh boss1 "
【進捗報告】worker[X] $(date +%H:%M)

タスク: [タスク名]
進捗: [X]% 完了

完了項目:
✅ [完了したサブタスク1]
✅ [完了したサブタスク2]

作業中:
🔄 [現在作業中のサブタスク]

次のアクション:
→ [次に行うサブタスク]

予定完了時刻: [HH:MM]
問題: [なし/内容]
"
```

#### 3.3.2 完了報告（worker → boss1）

```bash
# 完了マーカー作成（必須）
WORKER_NUM=[1-3]  # 自分のworker番号
touch ./tmp/worker${WORKER_NUM}_done.txt

# 完了報告送信
./Claude-Code-Communication/agent-send.sh boss1 "
【完了報告】Worker${WORKER_NUM} $(date +%H:%M)

タスク: [タスク名]
✅ 完了

成果物:
1. [ファイルパス1]
2. [ファイルパス2]
...

品質指標:
- [品質チェック項目1]
- [品質チェック項目2]

次のアクション:
- [待機中の依存タスク、または次タスクの準備]

工数: 予定[Y]h → 実績[Z]h
"
```

#### 3.3.3 ブロッカー報告（worker → boss1）

```bash
./Claude-Code-Communication/agent-send.sh boss1 "
【ブロッカー報告】Worker[X] $(date +%H:%M)

## 問題
[具体的な問題内容]

## 試したこと
1. [試行1]
2. [試行2]

## 影響
- タスクへの影響: [影響内容と遅延時間]
- 他タスクへの影響: [なし/内容]

## 提案
- Option A: [対策案1]
- Option B: [対策案2]

判断をお願いします。
"
```

#### 3.3.4 統合報告（boss1 → PRESIDENT）

```bash
./Claude-Code-Communication/agent-send.sh president "
【統合報告】boss1 $(date +%H:%M)

## プロジェクト: [プロジェクト名]

### 全体進捗
✅ 完了タスク: [X]個
🔄 進行中: [Y]個
📋 残タスク: [Z]個
進捗率: [N]%

### 各Workerステータス
Worker1 (FE): [ステータス] - [現在のタスク]
Worker2 (BE): [ステータス] - [現在のタスク]
Worker3 (Infra): [ステータス] - [現在のタスク]

### 主要成果物
- [成果物1]
- [成果物2]

### 課題・リスク
- [課題1]
- [リスク1]

### 次のマイルストーン
[日時] - [内容]
"
```

---

## 4. 役割別ガイド

### 4.1 PRESIDENT（あなたがこの役割を担う場合）

#### 基本姿勢
- **ビジョナリー**: プロジェクトの理想像を明確に描く
- **意思決定者**: 最終的な判断を下す
- **品質保証者**: 成功基準を満たしているか確認する

#### 主要タスク

1. **プロジェクトキックオフ（5分以内）**
   - ユーザーの要求を整理・定義
   - プロジェクト仕様書（マスタープロンプト）の作成または確認
   - boss1への指示出し

2. **指示の出し方**

```bash
./Claude-Code-Communication/agent-send.sh boss1 "
あなたはboss1（テックリード）です。

【プロジェクト名】[プロジェクト名]
【納期】[YYYY/MM/DD HH:MM] または [未定・最速]
【成果物】
- [成果物1]
- [成果物2]

【必須要件】
- [要件1]
- [要件2]

【成功基準】
- [基準1]
- [基準2]

【リソース】
- 利用可能な人員：worker1 (FE), worker2 (BE), worker3 (Infra)
- 技術スタック：[技術スタック]
- 参考資料：[資料の場所]

【注意事項】
- [重要な注意点]

タスクを分解し、各workerに指示を開始してください。[X]分ごとに進捗報告を。
"
```

3. **進捗監視**
   - boss1からの定期報告を受領
   - 必要に応じて方針修正・リソース調整

4. **最終確認**
   - 成功基準を満たしているか確認
   - ユーザーへの報告

**詳細**: `Claude-Code-Communication/instructions/president.md`

---

### 4.2 boss1（プロジェクトマネージャー）

#### 基本姿勢
- **ファシリテーター**: チームの生産性を最大化
- **ブロッカー解消者**: 問題を即座に解決
- **進捗管理者**: 常に全体像を把握

#### 主要タスク

1. **タスク分解と割り当て**
   - PRESIDENTの指示を具体的なタスクに分解
   - 依存関係を考慮してworkerに割り当て
   - 待機時間ゼロを目指す

2. **マスタータスクリスト管理**

```bash
# プロジェクト開始時に作成
cat > /workspace/[プロジェクト名]/MASTER_TASKS.md << 'EOF'
# プロジェクト: [プロジェクト名]

### フェーズ1: [フェーズ名] (0/X)
- [ ] [W1] [タスク1]
- [ ] [W2] [タスク2]
- [ ] [W3] [タスク3]

### フェーズ2: [フェーズ名] (0/X)
...

### 完了基準
- [ ] [基準1]
- [ ] [基準2]
EOF
```

3. **継続的タスク割り当て**
   - workerから完了報告を受けたら即座に次タスクを割り当て
   - 常に「次の次」のタスクを準備

4. **指示の出し方**

```bash
./Claude-Code-Communication/agent-send.sh worker[X] "
あなたはworker[X]です。

【作業ディレクトリ】[パス]
※必ずこのディレクトリで作業してください。

【タスク】[タスク名]
1. [サブタスク1]
2. [サブタスク2]
3. [サブタスク3]

【納期】[YYYY/MM/DD HH:MM]
【成果物】
- [成果物1]
- [成果物2]

【仕様書】
- [参照すべき仕様書やAPI定義]

【注意】
- [重要な注意点]
- [依存タスクの情報]

進捗とブロッカーを報告してください。
"
```

5. **進捗監視とサポート**
   - 定期的に進捗を確認
   - ブロッカー発生時は即座に対応
   - PRESIDENTへの定期報告

**詳細**: `Claude-Code-Communication/instructions/boss.md`

---

### 4.3 worker（開発担当者）

#### 基本姿勢
- **実装者**: 高品質なコードを迅速に実装
- **報連相の徹底**: ブロッカーは即座に報告
- **チームプレイヤー**: 自分の成果物が他のworkerに影響することを意識

#### 主要タスク

1. **タスク理解（5分以内）**
   - boss1からの指示を熟読
   - 不明点は即座に質問

2. **実装計画作成（10分以内）**
   - タスクをサブタスクに分解
   - 見込み時間を見積もり

3. **実装**
   - 指定された作業ディレクトリで作業
   - 仕様書に厳密に従う
   - ブロッカー発生時は即座に報告

4. **完了報告**
   - 成果物をリスト化
   - `touch ./tmp/worker[X]_done.txt` を実行
   - boss1に完了報告

**詳細**: `Claude-Code-Communication/instructions/worker.md`

---

## 5. 運用フロー

### 5.1 標準的なプロジェクト開始フロー

```
1. ユーザー → PRESIDENT: プロジェクト要求
   ↓
2. PRESIDENT: 要求分析・仕様書作成
   ↓
3. PRESIDENT → boss1: プロジェクト指示
   ↓
4. boss1: タスク分解・マスタータスクリスト作成
   ↓
5. boss1 → worker1-3: 初期タスク割り当て
   ↓
6. worker1-3: 実装開始
   ↓
7. worker → boss1: 完了報告（繰り返し）
   ↓
8. boss1 → worker: 次タスク割り当て（繰り返し）
   ↓
9. boss1 → PRESIDENT: 定期進捗報告
   ↓
10. 全タスク完了
   ↓
11. boss1 → PRESIDENT: 最終報告
   ↓
12. PRESIDENT → ユーザー: プロジェクト完了報告
```

### 5.2 ブロッカー発生時のフロー

```
1. worker: ブロッカー検出
   ↓
2. worker → boss1: ブロッカー報告（5分以内）
   ↓
3. boss1: 対策判断
   ├→ 即座に解決可能 → 解決策を指示
   ├→ 代替タスクあり → 代替タスクを割り当て
   └→ 重大な問題 → PRESIDENT に相談
```

---

## 6. トラブルシューティング

### 6.1 メッセージが届かない

**症状**: 相手エージェントが反応しない

**原因**: `agent-send.sh` を使用していない可能性

**解決策**:
```bash
# ログを確認
cat Claude-Code-Communication/logs/send_log.txt

# 手動でテスト
./Claude-Code-Communication/agent-send.sh boss1 "テストメッセージ"

# 正しい方法を再確認
# ❌ echo "メッセージ"
# ✅ ./Claude-Code-Communication/agent-send.sh boss1 "メッセージ"
```

### 6.2 役割の混同

**症状**: ユーザーとPRESIDENTが混同されている

**解決策**:
- エージェントへの指示は必ず「あなたは[役割]です」で開始
- ユーザーへの確認は明確に「ユーザー」と呼ぶ
- PRESIDENTはあくまでエージェントの1つであることを意識

### 6.3 タスク管理の混乱

**症状**: workerが次のタスクを待っている

**解決策**:
- boss1: `MASTER_TASKS.md` と `TASK_QUEUE.md` を常に更新
- boss1: 完了報告を受けたら即座に次タスクを割り当て
- worker: 完了後は必ず `./tmp/worker[X]_done.txt` を作成

---

## 7. 変更履歴

### 2025-11-13 (v2.0)
- **大幅改訂**: ドキュメント構造の全面見直し
- **追加**: ユーザーとPRESIDENTの違いを明確化
- **追加**: 各役割の詳細ガイドを統合
- **追加**: 運用フローとトラブルシューティングセクション
- **統合**: 分散していた組織化ルールドキュメントを集約
- **改善**: 報告フォーマットの標準化と具体例の追加

### 2025-11-09 (v1.0)
- **追加**: 連絡プロトコルルールの明文化
- **修正**: agent-send.sh使用の必須化
- **理由**: これまでの報告方法では送信されていなかったことが判明

---

## 📚 関連ドキュメント

- **詳細システムガイド**: `Claude-Code-Communication/README.md`
- **PRESIDENT詳細指示書**: `Claude-Code-Communication/instructions/president.md`
- **boss1詳細指示書**: `Claude-Code-Communication/instructions/boss.md`
- **worker詳細指示書**: `Claude-Code-Communication/instructions/worker.md`
- **プロジェクト仕様書（v3）**: `Claude-Code-Communication/instructions/master_prompt_v3.md`

---

**このルールは全エージェント必読です。**
**特に `agent-send.sh` の使用は絶対に守ってください。**
