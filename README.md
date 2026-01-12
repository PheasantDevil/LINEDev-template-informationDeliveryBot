# 📰 情報配信 LINE Bot

AI、ドローン、SDGs などの最新情報を扱うサイトから情報を収集し、LINE 経由で自動配信する Bot システムです。

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-enabled-brightgreen)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![LINE](https://img.shields.io/badge/LINE-Messaging%20API-00C300)](https://developers.line.biz/)

## 📝 概要

このプロジェクトは、複数の情報発信サイトから最新情報を収集し、LINE 経由でリアルタイムに配信します。情報源サイトは統一性がなく、メールや独自の方法で発信しているため、この Bot で一元管理します。

**主な機能:**

- ✅ **リアルタイム情報収集**: サイト更新直後に情報を収集
- ✅ **複数サイト対応**: スクレイピング、RSS、メール要約に対応
- ✅ **カテゴリ別配信**: AI、ドローン、SDGs など、カテゴリごとに配信
- ✅ **ユーザー登録**: LINE Bot 内で完結するユーザー登録
- ✅ **差分検知**: 新着情報のみを配信
- ✅ **完全無料運用可能**（無料枠内）

## 🎯 目標

- 情報発信サイトの情報を逐一集める
- 統一性のない情報発信を LINE で一元管理
- 自分の得たい情報を埋もれさせずにチェックできる
- どんな情報発信中のサイトがあるかを知ることができる
- どんな情報を定期的に知ることが必要かを発信
- 現在の日本の報道の一部分が機能していないかを発信

## 🏗️ アーキテクチャ

### システム構成

```
情報発信サイト → 情報収集（スクレイピング/RSS/メール）
                ↓
          差分検知システム
                ↓
          データ保存（JSON）
                ↓
          LINE Messaging API → ユーザー
                ↑
          Webhook（Render.com等）
                ↑
          ユーザー操作（登録・購読設定）
```

### プロジェクト構造

```
LINEDev-template-informationDeliveryBot/
├── .github/
│   └── workflows/
│       └── collect-and-deliver.yml    # 自動収集・配信
├── docs/
│   ├── YYYYMMDD/                      # 要件定義・技術検証
│   │   ├── NNN-prompt.md
│   │   └── implementation-NNN.md
│   └── sites/                         # サイト紹介ページ
│       ├── index.md
│       └── [site_id].md
├── src/
│   ├── collectors/                    # 情報収集システム
│   │   ├── base.py
│   │   ├── scraper.py
│   │   ├── rss_reader.py
│   │   └── email_processor.py
│   ├── diff_detector.py              # 差分検知
│   ├── user_manager.py                # ユーザー管理
│   ├── line_notifier.py               # LINE配信
│   ├── webhook_server.py              # Webhookサーバー
│   ├── collect_and_deliver.py         # 収集・配信実行
│   └── storage.py                     # データ永続化
├── tools/
│   ├── add_site.py                    # サイト追加ツール
│   └── generate_site_page.py          # サイトページ生成
├── data/
│   ├── sites.json                     # サイト設定
│   ├── information_items.json          # 収集した情報
│   ├── users.json                      # ユーザー情報
│   └── category_groups.json           # カテゴリグループ
├── requirements.txt
├── Procfile                           # Webhookサーバー用
└── README.md
```

## 🚀 セットアップ

### 必要なもの

- GitHub アカウント
- LINE アカウント
- LINE Developers アカウント（無料）
- （Webhook 用）Render.com アカウントまたは他のホスティングサービス

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/LINEDev-template-informationDeliveryBot.git
cd LINEDev-template-informationDeliveryBot
```

### 2. LINE Messaging API の設定

1. [LINE Developers Console](https://developers.line.biz/)にアクセス
2. 新規プロバイダーを作成
3. Messaging API チャネルを作成
4. チャネルアクセストークンとチャネルシークレットを取得
5. LINE User ID を取得（友だち追加後）

### 3. GitHub Secrets の設定

GitHub リポジトリの **Settings** > **Secrets and variables** > **Actions** で以下を設定：

- `LINE_CHANNEL_ACCESS_TOKEN`: チャネルアクセストークン
- `LINE_CHANNEL_SECRET`: チャネルシークレット（Webhook 用）

### 4. 依存関係のインストール

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Webhook サーバーのデプロイ

詳細は `docs/SETUP_GUIDE.md` を参照してください。

## 📚 ドキュメント

- `docs/SETUP_GUIDE.md`: **セットアップガイド（手動設定手順）** ⭐
- `docs/TESTING_GUIDE.md`: **テストガイド（連携テスト手順）** ⭐
- `docs/TODO.md`: **残りのタスク一覧** ⭐
- `docs/README.md`: ドキュメント管理方法
- `docs/YYYYMMDD/`: 要件定義・技術検証の記録
- `docs/sites/`: 情報発信サイトの紹介ページ

## 🛠️ 開発

### 実装フェーズ

- **Phase 1**: 基盤構築（LINE Bot 基本機能、ユーザー登録）
- **Phase 2**: 情報収集拡張（複数サイト対応、差分検知）
- **Phase 3**: 配信機能強化（自動実行、グループ管理）
- **Phase 4**: 高度な機能（メール要約、サービス紹介サイト）

### ローカル開発

```bash
# 環境変数を設定
export LINE_CHANNEL_ACCESS_TOKEN='your_token_here'
export LINE_CHANNEL_SECRET='your_secret_here'

# Webhookサーバーを起動
python src/webhook_server.py
```

## 📝 ライセンス

MIT License

## 🤝 貢献

Pull Requests を歓迎します！

---

**📰 Happy Information Gathering! 📡**
