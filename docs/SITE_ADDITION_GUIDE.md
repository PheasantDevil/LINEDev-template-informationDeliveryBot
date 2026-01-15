# サイト追加ガイド

このガイドでは、実際のサイトを追加する方法を説明します。

## 前提条件

- メール方式の場合: Gmailアカウントとアプリパスワードの設定が必要
- RSS方式の場合: サイトのRSSフィードURLが必要
- スクレイパー方式の場合: サイトのHTML構造の理解が必要

## サイト追加方法

### 方法1: コマンドラインツールを使用（推奨）

`tools/add_site.py`を使用してサイトを追加します。

#### メール方式の例

```bash
python tools/add_site.py \
  --id ai_weekly \
  --name "AI Weekly" \
  --url https://aiweekly.co/ \
  --category AI \
  --type email \
  --email-account gmail_account_001 \
  --subscription-email infobot.delivery+aiweekly@gmail.com \
  --sender-email newsletter@aiweekly.co \
  --subject-pattern "AI News Weekly|Issue #" \
  --check-interval 15 \
  --summary-enabled \
  --enabled
```

#### RSS方式の例

```bash
python tools/add_site.py \
  --id tech_news \
  --name "Tech News" \
  --url https://example.com/tech-news \
  --category AI \
  --type rss \
  --feed-url https://example.com/tech-news/feed.xml \
  --check-interval 60 \
  --enabled
```

#### スクレイパー方式の例

```bash
python tools/add_site.py \
  --id drone_news \
  --name "Drone News" \
  --url https://example.com/drone-news \
  --category ドローン \
  --type scraper \
  --selector ".article-list .article" \
  --check-interval 120 \
  --enabled
```

### 方法2: 手動でJSONファイルを作成

`data/sites/`ディレクトリに`{site_id}.json`ファイルを作成します。

#### メール方式の設定例

```json
{
  "id": "ai_weekly",
  "name": "AI Weekly",
  "url": "https://aiweekly.co/",
  "category": "AI",
  "collector_type": "email",
  "collector_config": {
    "email_account_id": "gmail_account_001",
    "subscription_email": "infobot.delivery+aiweekly@gmail.com",
    "sender_email": "newsletter@aiweekly.co",
    "subject_pattern": "AI News Weekly|Issue #",
    "check_interval_minutes": 15,
    "summary_enabled": true,
    "summary_model": "gemini-1.5-flash"
  },
  "enabled": false,
  "created_at": "2025-01-15T00:00:00",
  "last_collected_at": null,
  "stats": {
    "total_collected": 0,
    "last_7_days": 0
  }
}
```

## 設定項目の説明

### 共通設定

- `id`: サイトID（英数字とアンダースコア、一意である必要がある）
- `name`: サイト名（表示用）
- `url`: サイトURL
- `category`: カテゴリ（例: AI, ドローン, SDGs）
- `collector_type`: 収集方式（`email`, `rss`, `scraper`）
- `enabled`: 有効/無効（`true`/`false`）
- `check_interval_minutes`: 収集間隔（分）

### メール方式の設定

- `email_account_id`: メールアカウントID（`data/email_accounts.json`で定義）
- `subscription_email`: 購読メールアドレス（Gmail Plus Alias推奨）
- `sender_email`: 送信者メールアドレス（フィルタリング用）
- `subject_pattern`: 件名パターン（正規表現、オプション）
- `summary_enabled`: AI要約を有効化（`true`/`false`）
- `summary_model`: 要約モデル（デフォルト: `gemini-1.5-flash`）

### RSS方式の設定

- `feed_url`: RSSフィードURL

### スクレイパー方式の設定

- `selector`: CSSセレクター（情報を抽出する要素）

## サイトの有効化

サイトを追加した後、`enabled: true`に設定するか、`--enabled`フラグを使用して有効化します。

```bash
# 既存サイトを有効化する場合
python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
from src.storage import Storage

storage = Storage()
site = storage.load_site('ai_weekly')
if site:
    site['enabled'] = True
    storage.save_site(site)
    print('✓ サイトを有効化しました')
"
```

## 実際のサイト追加の手順

1. **サイトの選定**
   - AIカテゴリ: 2-3サイト
   - ドローンカテゴリ: 1-2サイト
   - その他のカテゴリ: 必要に応じて

2. **メール購読の設定**（メール方式の場合）
   - Gmail Plus Aliasを使用して購読
   - 例: `infobot.delivery+aiweekly@gmail.com`

3. **サイト設定の追加**
   - `tools/add_site.py`を使用して追加
   - または手動でJSONファイルを作成

4. **動作確認**
   - `python src/collect_and_deliver.py`を実行してテスト
   - エラーがないか確認

5. **有効化**
   - 動作確認後、`enabled: true`に設定

## トラブルシューティング

### メールが受信できない

- Gmailアプリパスワードが正しく設定されているか確認
- `data/email_accounts.json`の設定を確認
- メールボックスの権限を確認

### 情報が収集されない

- `enabled: true`になっているか確認
- `check_interval_minutes`が適切か確認
- ログを確認してエラーがないか確認

### 重複した情報が配信される

- `diff_detector.py`の動作を確認
- `content_hash`が正しく生成されているか確認

---

**最終更新**: 2025-01-15

