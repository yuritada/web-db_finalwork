# Claude Code プロジェクト運用ルール

**最終更新**: 2025-11-09
**管理者**: boss1

---

## 🚨 重要: 連絡プロトコル

### エージェント間通信の正しい方法

**必須ルール**: エージェント間の連絡は **必ず `agent-send.sh` スクリプトを使用すること**

#### 正しい連絡方法

```bash
# PRESIDENTへの連絡
./Claude-Code-Communication/agent-send.sh president "メッセージ内容"

# Worker1への連絡
./Claude-Code-Communication/agent-send.sh worker1 "メッセージ内容"

# Worker2への連絡
./Claude-Code-Communication/agent-send.sh worker2 "メッセージ内容"

# Worker3への連絡
./Claude-Code-Communication/agent-send.sh worker3 "メッセージ内容"

# boss1への連絡
./Claude-Code-Communication/agent-send.sh boss1 "メッセージ内容"
```

**スクリプトの場所**: `./Claude-Code-Communication/agent-send.sh`

#### ❌ 誤った方法

```bash
# 単なるテキスト出力やecho、catコマンドは送信されない
echo "報告内容"
cat > report.txt
```

**重要**: 単なるテキスト出力では、相手に送信されません。
必ず `agent-send.sh` を使用してください。

---

## プロジェクト構成

### エージェント役割分担

- **PRESIDENT**: 全体統括、タスク指示
- **boss1**: プロジェクトマネージャー、進捗管理
- **worker1**: フロントエンド開発
- **worker2**: バックエンド開発
- **worker3**: インフラ・統合・ドキュメント

---

## 報告プロトコル

### 進捗報告

**報告先**: boss1 および PRESIDENT（タスクによる）

**報告タイミング**:
- タスク完了時
- ブロッカー発生時
- 緊急進捗確認要求時

**報告形式**:
```bash
./agent-send.sh boss1 "
【進捗報告】worker3

完了タスク:
- タスク1
- タスク2

進行中タスク:
- タスク3 (進捗50%)

ブロッカー:
- なし

質問:
- 次のタスク指示をお願いします
"
```

---

## 変更履歴

### 2025-11-09
- **追加**: 連絡プロトコルルールの明文化
- **修正**: agent-send.sh使用の必須化
- **理由**: これまでの報告方法では送信されていなかったことが判明

---

**このルールは全エージェント必読です。**
