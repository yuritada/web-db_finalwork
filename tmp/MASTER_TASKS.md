# プロジェクト: API問題修正とドキュメント整理

**開始日時**: 2025-11-14
**担当**: boss1
**ステータス**: 進行中

---

## 全体進捗

- ✅ 完了タスク: 0/15
- 🔄 進行中: 0/15
- 📋 残タスク: 15/15
- **進捗率**: 0%

---

## フェーズ1: ドキュメント統合（worker3担当） (0/6)

- [ ] [W3] 古いPhase4関連ドキュメント削除（7個）
- [ ] [W3] API仕様書統合（backend/docs/api/*.md → backend/docs/API.md）
- [ ] [W3] バックエンドアーキテクチャ統合（auth-flow, functions/* → backend-architecture.md）
- [ ] [W3] 全体アーキテクチャ統合（data-flow, user-flows, frontend-architecture → architecture.md）
- [ ] [W3] セットアップドキュメント統合（operations, deployment → setup.md）
- [ ] [W3] フロントエンドドキュメント統合（components.md → frontend/README.md）

## フェーズ2: バックエンドAPI修正（worker2担当） (0/5)

- [ ] [W2] API仕様書の確認（backend/docs/api/README.md）
- [ ] [W2] チャンネル詳細取得API実装（GET /channels/{channel_id}）
- [ ] [W2] get_channel_by_id関数の詳細情報追加
- [ ] [W2] ChannelDetailスキーマの作成
- [ ] [W2] バックエンドAPI動作確認

## フェーズ3: フロントエンドAPI修正（worker1担当） (0/4)

- [ ] [W1] DMConversation型修正（partner_id → user_id, partner_username → username）
- [ ] [W1] getChannel関数修正（全件取得回避、新しいAPI使用）
- [ ] [W1] frontend/miscat/lib/api.tsの型定義更新
- [ ] [W1] フロントエンドAPI動作確認

---

## 完了基準

- [ ] フロントエンドとバックエンドのAPI仕様が一致している
- [ ] ドキュメントが半分以下になっている（45個→22個以下）
- [ ] 既存機能が正常動作する
- [ ] 統合テストが通る

---

## 依存関係

- フェーズ1とフェーズ2は並行実行可能
- フェーズ3はフェーズ2完了後に実施（バックエンドAPI実装後）

---

## ブロッカー

なし

---

## 注意事項

- Claude-Code-Communication/内のファイルは変更禁止
- 既存のコードは壊さないこと
- API変更時は必ずフロントエンドとバックエンド両方を修正
