# ドキュメント管理

このディレクトリでは、プロジェクトのドキュメントをカテゴリ別に整理して管理しています。

## 📁 ディレクトリ構造

```
docs/
├── README.md                    # このファイル（ドキュメント索引）
├── deployment/                  # デプロイ関連
│   ├── DEPLOYMENT_GUIDE.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── DEPLOYMENT_PREPARATION.md
│   ├── DEPLOYMENT_STEPS.md
│   ├── ENV_VAR_SETUP_RENDER.md
│   └── WEBHOOK_VERIFICATION_TROUBLESHOOTING.md
├── site-management/             # サイト管理関連
│   ├── SITE_ADDITION_GUIDE.md
│   ├── SITE_ADDITION_SUMMARY.md
│   ├── SITE_CONFIGURATION_STATUS.md
│   ├── SITE_RESEARCH.md
│   ├── EMAIL_SAMPLE_ANALYSIS.md
│   └── GMAIL_ACCOUNT_SUGGESTIONS.md
├── channel-management/          # チャネル管理関連
│   ├── CHANNEL_NAMING_CONVENTION.md
│   └── LINE_CHANNEL_AUTO_MANAGEMENT_PROPOSAL.md
├── development/                 # 開発・運用関連
│   ├── SETUP_GUIDE.md
│   ├── TESTING_GUIDE.md
│   ├── WORKFLOW.md
│   ├── TODO.md
│   └── QUICK_START.md
├── proposals/                   # 提案・計画関連
│   ├── FUTURE_ROADMAP.md
│   ├── NEXT_IMPLEMENTATION.md
│   ├── NEXT_IMPLEMENTATION_OPTIONS.md
│   ├── NEXT_TASKS.md
│   └── SITE_BASED_SUBSCRIPTION_PROPOSAL.md
├── archive/                     # 完了済みサマリー
│   ├── PHASE1_COMPLETION_SUMMARY.md
│   └── PR_SUMMARY.md
└── YYYYMMDD/                    # 日付ごとのプロンプト/回答
    ├── 001-prompt.md
    ├── 002-prompt.md
    └── implementation-*.md
```

---

## 📚 カテゴリ別ドキュメント

### 🚀 デプロイ関連 (`deployment/`)

デプロイ手順、環境設定、トラブルシューティング

- **DEPLOYMENT_GUIDE.md** - デプロイ手順の詳細（Render.com, Railway.app, Fly.io）
- **DEPLOYMENT_CHECKLIST.md** - デプロイ前チェックリスト
- **DEPLOYMENT_PREPARATION.md** - デプロイ準備ガイド
- **DEPLOYMENT_STEPS.md** - 段階的なデプロイ手順（実作業手順）
- **ENV_VAR_SETUP_RENDER.md** - Render.com環境変数設定手順
- **WEBHOOK_VERIFICATION_TROUBLESHOOTING.md** - Webhook検証エラー対応

**用途**: Webhookサーバーを本番環境にデプロイする際の手順

---

### 📊 サイト管理関連 (`site-management/`)

サイト追加、設定、調査結果

- **SITE_ADDITION_GUIDE.md** - サイト追加ガイド
- **SITE_ADDITION_SUMMARY.md** - サイト追加サマリー
- **SITE_CONFIGURATION_STATUS.md** - サイト設定状況
- **SITE_RESEARCH.md** - サイト調査結果
- **EMAIL_SAMPLE_ANALYSIS.md** - メールサンプル分析
- **GMAIL_ACCOUNT_SUGGESTIONS.md** - Gmailアカウント名の提案

**用途**: 新しい情報サイトを追加・管理する際の手順

---

### 📱 チャネル管理関連 (`channel-management/`)

LINEチャネルの作成・管理

- **CHANNEL_NAMING_CONVENTION.md** - チャネル命名規則
- **LINE_CHANNEL_AUTO_MANAGEMENT_PROPOSAL.md** - チャネル自動管理の提案

**用途**: LINEチャネルの作成・管理に関する規則と提案

---

### 🛠️ 開発・運用関連 (`development/`)

開発環境セットアップ、テスト、ワークフロー

- **SETUP_GUIDE.md** - セットアップガイド
- **TESTING_GUIDE.md** - テストガイド
- **WORKFLOW.md** - 開発ワークフロー
- **TODO.md** - 残りのタスク一覧
- **QUICK_START.md** - クイックスタートガイド

**用途**: 開発環境のセットアップと開発プロセス

---

### 💡 提案・計画関連 (`proposals/`)

将来の実装計画、次のタスク

- **FUTURE_ROADMAP.md** - 今後の実装構想（管理画面システム）
- **NEXT_IMPLEMENTATION.md** - 次の実装内容
- **NEXT_IMPLEMENTATION_OPTIONS.md** - 次の実装オプション
- **NEXT_TASKS.md** - 次の作業タスク（優先順位順）
- **SITE_BASED_SUBSCRIPTION_PROPOSAL.md** - サイト単位購読機能の提案

**用途**: 将来の機能拡張や実装計画の検討

---

### 📦 アーカイブ (`archive/`)

完了済みのサマリーや過去のPR情報

- **PHASE1_COMPLETION_SUMMARY.md** - Phase 1完了サマリー
- **PR_SUMMARY.md** - PRサマリー（一時ファイル）

**用途**: 過去の作業記録の保存

---

### 📅 日付ディレクトリ (`YYYYMMDD/`)

要件定義や技術検証のプロンプト/回答

- **NNN-prompt.md** - プロンプトと回答
- **implementation-NNN.md** - 実装記録

**用途**: 要件定義や実装時の記録

---

## 🔍 ドキュメントの探し方

### デプロイしたい場合
→ `deployment/` ディレクトリを参照

### サイトを追加したい場合
→ `site-management/SITE_ADDITION_GUIDE.md` を参照

### チャネルを作成したい場合
→ `channel-management/CHANNEL_NAMING_CONVENTION.md` を参照

### 開発環境をセットアップしたい場合
→ `development/SETUP_GUIDE.md` を参照

### 次の実装タスクを確認したい場合
→ `proposals/NEXT_TASKS.md` を参照

---

## 📝 ドキュメント追加時のルール

### 新しいドキュメントを追加する場合

1. **カテゴリを決定**
   - デプロイ関連 → `deployment/`
   - サイト管理 → `site-management/`
   - チャネル管理 → `channel-management/`
   - 開発・運用 → `development/`
   - 提案・計画 → `proposals/`

2. **ファイル名の規則**
   - 大文字で始める（例: `DEPLOYMENT_GUIDE.md`）
   - アンダースコアで区切る
   - 明確な名前を付ける

3. **README.mdの更新**
   - 新しいドキュメントをREADME.mdに追加

---

## 🔗 主要ドキュメントへのリンク

### はじめての方
- [クイックスタート](development/QUICK_START.md)
- [セットアップガイド](development/SETUP_GUIDE.md)

### デプロイ
- [デプロイ手順](deployment/DEPLOYMENT_STEPS.md)
- [デプロイチェックリスト](deployment/DEPLOYMENT_CHECKLIST.md)

### サイト管理
- [サイト追加ガイド](site-management/SITE_ADDITION_GUIDE.md)
- [サイト調査結果](site-management/SITE_RESEARCH.md)

### チャネル管理
- [チャネル命名規則](channel-management/CHANNEL_NAMING_CONVENTION.md)

### 開発
- [開発ワークフロー](development/WORKFLOW.md)
- [テストガイド](development/TESTING_GUIDE.md)

---

**最終更新**: 2025-01-18
