# プロジェクト: API問題修正とドキュメント整理

**作成日**: 2025-11-14
**boss1**: プロジェクトマネージャー
**納期**: 最速
**進捗**: 0/10タスク完了

---

## 📊 全体進捗

- **完了**: 0個
- **進行中**: 0個
- **残タスク**: 10個
- **進捗率**: 0%

---

## フェーズ1: API問題修正（並行実施） (0/5)

### worker2（バックエンド） - API実装 (0/2)

- [ ] [W2-1] **GET /channels/{channel_id} エンドポイント実装**
  - 担当: worker2
  - 優先度: Critical
  - 工数見積: 1-2h
  - 依存: なし
  - 成果物:
    - `backend/app/routers/channels.py` に新エンドポイント追加
    - `backend/app/schemas/channel.py` に ChannelDetail スキーマ追加
    - `backend/app/db/read.py` に必要な関数追加（既存get_channel_by_id活用）
  - テスト: curlまたはPythonでエンドポイント動作確認

- [ ] [W2-2] **channels.md 仕様書更新**
  - 担当: worker2
  - 優先度: High
  - 工数見積: 30min
  - 依存: W2-1完了後
  - 成果物:
    - `backend/docs/api/channels.md` の「未実装機能」セクション更新
    - GET /channels/{channel_id} の詳細仕様を追加

### worker1（フロントエンド） - 型定義修正 (0/2)

- [ ] [W1-1] **DMConversation型修正（partner_id → user_id）**
  - 担当: worker1
  - 優先度: Critical
  - 工数見積: 15min
  - 依存: なし
  - 成果物:
    - `frontend/miscat/lib/api.ts` の DMConversation型定義修正（359-364行）
    - partner_id → user_id
    - partner_username → そのまま（互換性のため）
  - テスト: TypeScriptコンパイル確認、DM一覧画面動作確認

- [ ] [W1-2] **getChannel関数の効率化**
  - 担当: worker1
  - 優先度: Medium
  - 工数見積: 15min
  - 依存: W2-1完了後
  - 成果物:
    - `frontend/miscat/lib/api.ts` の getChannel関数を修正（312-319行）
    - 全件取得→フィルタリング から GET /api/channels/{channel_id} への変更
  - テスト: チャンネル詳細取得の動作確認

### worker3（ドキュメント） - 初期調査 (0/1)

- [ ] [W3-1] **ドキュメント調査・分類**
  - 担当: worker3
  - 優先度: High
  - 工数見積: 30min
  - 依存: なし
  - 成果物:
    - ドキュメント一覧（削除候補・統合候補・保持候補）
    - 統合計画案
  - 提出先: boss1に報告

---

## フェーズ2: ドキュメント整理 (0/3)

### worker3（ドキュメント統合） (0/3)

- [ ] [W3-2] **Phase 4関連ドキュメント削除**
  - 担当: worker3
  - 優先度: Medium
  - 工数見積: 10min
  - 依存: W3-1完了後
  - 削除対象:
    - `backend/docs/phase4_technical_proposal.md`
    - `backend/docs/phase4_implementation_plan.md`
    - `backend/docs/phase4_test_plan.md`
    - `frontend/miscat/docs/phase4_ui_design.md`
  - 理由: Phase 4完了済み、歴史的文書として不要

- [ ] [W3-3] **アーキテクチャドキュメント統合**
  - 担当: worker3
  - 優先度: High
  - 工数見積: 1h
  - 依存: W3-2完了後
  - 統合内容:
    - `docs/architecture.md` + `docs/frontend-architecture.md` + `backend/docs/backend-architecture.md`
    - → `docs/ARCHITECTURE.md`（全体アーキテクチャ）
    - `docs/setup.md` + `backend/docs/deployment.md`
    - → `docs/DEPLOYMENT.md`（環境構築・デプロイ）
  - 削除: 統合元ファイル

- [ ] [W3-4] **API仕様書統合**
  - 担当: worker3
  - 優先度: High
  - 工数見積: 1.5h
  - 依存: W2-2完了後（channels.md更新後）
  - 統合内容:
    - `backend/docs/api/*.md`（8個） → `backend/docs/API.md`
    - 目次セクション追加
    - 各APIセクションごとに整理
  - 保持: `backend/docs/api/README.md`（目次管理ガイド）

---

## フェーズ3: 統合テスト・確認 (0/2)

- [ ] [W1+W2] **API統合テスト**
  - 担当: worker1, worker2（共同）
  - 優先度: Critical
  - 工数見積: 30min
  - 依存: W1-2, W2-1完了後
  - テスト項目:
    - フロントエンドからGET /api/channels/{channel_id}を呼び出し
    - DMConversation型のレスポンス確認
    - 既存機能の回帰テスト

- [ ] [boss1] **最終確認とPRESIDENTへの報告**
  - 担当: boss1
  - 優先度: Critical
  - 工数見積: 15min
  - 依存: 全タスク完了後
  - 確認項目:
    - フロントエンドとバックエンドのAPI仕様一致
    - ドキュメント数が半分以下（48個 → 15個程度）
    - 既存機能が正常動作

---

## 🎯 成功基準チェックリスト

- [ ] フロントエンドとバックエンドのAPI仕様が一致している
- [ ] ドキュメントが半分以下になっている（48個 → 15個程度）
- [ ] 既存機能が正常動作する
- [ ] GET /channels/{channel_id} が実装され動作する
- [ ] DMConversation型が統一されている（user_id）

---

## 📝 報告スケジュール

- **30分ごと**: 各workerからboss1への進捗報告
- **フェーズ完了時**: boss1からPRESIDENTへの統合報告
- **プロジェクト完了時**: boss1からPRESIDENTへの最終報告

---

## 🔄 依存関係グラフ

```
W3-1 (調査)
  └─> W3-2 (Phase4削除)
      └─> W3-3 (アーキ統合)

W2-1 (API実装)
  ├─> W2-2 (仕様書更新)
  │   └─> W3-4 (API仕様書統合)
  └─> W1-2 (getChannel効率化)
      └─> 統合テスト

W1-1 (DM型修正)
  └─> 統合テスト
```

---

## 📊 リアルタイム進捗

| Worker | 現在のタスク | ステータス | 完了数 | 残数 |
|--------|------------|----------|-------|------|
| worker1 | - | 待機中 | 0/2 | 2 |
| worker2 | - | 待機中 | 0/2 | 2 |
| worker3 | - | 待機中 | 0/4 | 4 |

最終更新: 未開始
