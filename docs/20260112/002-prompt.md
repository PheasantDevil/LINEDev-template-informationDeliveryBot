## プロンプト

確認事項とその他について回答します

No1：具体的なサイトは決まっていません。初期段階は2,3サイトこちらで見繕う予定です。2,3サイトでの情報配信が軌道に乗ってきたら情報源サイトを調査して自主的に新しい情報発信も考えられるようになって欲しいです。またこちらから「このサイトの情報を発信できるようにしたい」となった際も手間を最小限に設定できることを目指します（目標はURLと情報発信の頻度を共有すれば発信できるようになるぐらい）

No2：配信頻度は発信するサイトが発信した直後が好ましいです。またグループ配信は必須ではありません。ただ同じ情報を求めている利用者がいる場合、ユーザーをグループで管理してここに配信できると良いと考えています

No3：現状LINEだけの場合、ユーザー登録はLINE Bot内で完結させます。No2で触れましたが、グループ配信は語弊でした。「情報ごとの配信者のグループ管理」程度に認識を更新してください

No4：カテゴリは固定しません。ただ初期段階では自身が興味のある「AI」と「（Ex：地域文化に活用される）ドローン」で考えています。よって将来的にカテゴリ追加の可能性はあります

No5：サービス紹介サイトは情報発信するサイトごとになると考えています。サイトは初期段階では静的サイトで問題ありませんが、今後サブスクなどの契約処理の拡張性も見越して検討したい

N06：初期はGitHubリポジトリ内のJSONで問題ありません。また「現在どんな情報サイトから発信しているか」は都度READMEや静的ページを見ればわかるようにしたいです。

その他：情報収集について。スクレーパーでは今後対策を取られ情報の抜き出しが難しくなるかもしれない。情報発信サイトからのメールを要約するなどオプションも検討したい

回答内容をもとに情報をアップデート必要情報を元に実装案を具体化してください

---

## Answer

回答内容を踏まえ、実装案を具体化しました。

## 具体化された実装案

### 1. システムアーキテクチャ（更新版）

```
┌─────────────────────────────────────────────────────────┐
│                   情報収集レイヤー                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ スクレイパ│  │ RSS/Feed │  │ メール   │             │
│  │ エンジン  │  │ リーダー │  │ 要約     │             │
│  └──────────┘  └──────────┘  └──────────┘             │
│         ↓              ↓              ↓                │
│  ┌──────────────────────────────────────────┐         │
│  │     統一情報収集インターフェース            │         │
│  │  (BaseInformationCollector)               │         │
│  └──────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   データ管理レイヤー                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ 情報ストレ│  │ 差分検知 │  │ サイト   │             │
│  │ ージ     │  │ システム │  │ 設定管理 │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│                   配信レイヤー                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ LINE Bot │  │ カテゴリ │  │ ユーザー │             │
│  │ Webhook  │  │ 別グループ│  │ 設定管理 │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

### 2. 主要コンポーネント設計（詳細版）

#### A. 情報収集システム（`src/collectors/`）

**設計方針：**
- 統一インターフェースで複数の収集方法をサポート
- サイト追加を最小限の設定で実現
- 将来的な自動サイト発見機能の拡張性を考慮

**ディレクトリ構造：**
```
src/collectors/
├── __init__.py
├── base.py              # BaseInformationCollector（統一インターフェース）
├── scraper.py           # スクレイピング実装
├── rss_reader.py        # RSS/Feedリーダー実装
├── email_processor.py   # メール要約実装（将来対応）
└── site_config.py       # サイト設定管理
```

**BaseInformationCollector インターフェース：**
```python
class BaseInformationCollector:
    """情報収集の統一インターフェース"""
    
    def collect(self, site_config: dict) -> List[InformationItem]:
        """情報を収集して返す"""
        pass
    
    def get_last_collected_time(self, site_id: str) -> datetime:
        """最後に収集した時刻を取得"""
        pass
    
    def mark_as_collected(self, site_id: str, items: List[InformationItem]):
        """収集完了を記録"""
        pass
```

**サイト設定（`data/sites.json`）：**
```json
{
  "sites": [
    {
      "id": "ai_site_001",
      "name": "AI情報サイト例",
      "url": "https://example.com/ai-news",
      "category": "AI",
      "collector_type": "scraper|rss|email",
      "collector_config": {
        "rss_url": "https://example.com/feed.xml",
        "scraping_selector": ".article-list > article",
        "check_interval_minutes": 60
      },
      "enabled": true,
      "created_at": "2025-01-12T10:00:00",
      "last_collected_at": "2025-01-12T09:00:00"
    }
  ]
}
```

**簡易サイト追加機能：**
- `tools/add_site.py` スクリプトでURLと頻度を指定するだけで追加可能
- 自動でRSS検出、スクレイピング設定の推奨値を提示

#### B. 差分検知システム（`src/diff_detector.py`）

**機能：**
- 新着情報のみを検出
- 重複排除（URL、タイトル、内容のハッシュ比較）
- 収集履歴の管理

**実装方針：**
```python
class DiffDetector:
    """差分検知システム"""
    
    def detect_new_items(
        self, 
        collected_items: List[InformationItem],
        stored_items: List[InformationItem]
    ) -> List[InformationItem]:
        """新着情報のみを抽出"""
        # URL、タイトル、内容ハッシュで比較
        pass
```

#### C. ユーザー管理システム（`src/user_manager.py`）

**機能：**
- LINE Bot内でのユーザー登録
- カテゴリ購読管理（動的カテゴリ対応）
- 情報ごとの配信者グループ管理

**データ構造（`data/users.json`）：**
```json
{
  "users": [
    {
      "user_id": "LINE_USER_ID",
      "line_display_name": "ユーザー名",
      "subscribed_categories": ["AI", "ドローン"],
      "subscribed_sites": ["ai_site_001", "drone_site_001"],
      "notification_groups": {
        "AI": "group_ai_001",
        "ドローン": "group_drone_001"
      },
      "registered_at": "2025-01-12T10:00:00",
      "last_active_at": "2025-01-12T10:00:00"
    }
  ]
}
```

**情報ごとのグループ管理：**
- カテゴリごとにLINEグループを作成（手動または自動）
- 同じカテゴリを購読しているユーザーをグループに追加
- グループIDを`data/category_groups.json`で管理

#### D. 情報配信システム（`src/line_notifier.py`）

**機能：**
- リアルタイム配信（サイト更新直後）
- カテゴリ別グループ配信
- 個人へのプッシュ通知

**配信フロー：**
1. 新着情報検出
2. 該当カテゴリを購読しているユーザーを取得
3. グループ配信（グループが設定されている場合）
4. 個人通知（グループ未設定の場合）

#### E. Webhookサーバー（`src/webhook_server.py`）

**機能：**
- ユーザー登録/解除
- カテゴリ購読設定変更
- 情報検索
- サイト一覧表示

**コマンド例：**
- `登録` - ユーザー登録
- `購読 AI` - AIカテゴリを購読
- `購読解除 ドローン` - ドローンカテゴリを購読解除
- `検索 AI 最新` - AIカテゴリの最新情報を検索
- `サイト一覧` - 登録されているサイト一覧を表示

### 3. データ構造設計（更新版）

#### 情報アイテム（`data/information_items.json`）
```json
{
  "items": [
    {
      "id": "info_20250112_001",
      "title": "記事タイトル",
      "url": "https://example.com/article/123",
      "category": "AI",
      "site_id": "ai_site_001",
      "site_name": "AI情報サイト例",
      "published_at": "2025-01-12T10:00:00",
      "scraped_at": "2025-01-12T10:05:00",
      "summary": "要約（オプション）",
      "content_hash": "sha256_hash_for_deduplication"
    }
  ],
  "last_updated": "2025-01-12T10:05:00"
}
```

#### サイト設定（`data/sites.json`）
```json
{
  "sites": [
    {
      "id": "site_unique_id",
      "name": "サイト名",
      "url": "https://example.com",
      "category": "AI|ドローン|...",
      "collector_type": "scraper|rss|email",
      "collector_config": {
        "check_interval_minutes": 60,
        "rss_url": "...",
        "scraping_config": {...}
      },
      "enabled": true,
      "created_at": "2025-01-12T10:00:00",
      "last_collected_at": "2025-01-12T09:00:00",
      "stats": {
        "total_collected": 150,
        "last_7_days": 12
      }
    }
  ]
}
```

#### カテゴリグループ（`data/category_groups.json`）
```json
{
  "groups": [
    {
      "category": "AI",
      "line_group_id": "group_ai_001",
      "subscribed_user_ids": ["user_001", "user_002"],
      "created_at": "2025-01-12T10:00:00"
    }
  ]
}
```

### 4. 自動実行システム（GitHub Actions）

**リアルタイム配信の実現：**
- 短い間隔（例：30分ごと）でGitHub Actionsを実行
- 各サイトの`check_interval_minutes`に基づいて収集頻度を調整
- 新着情報があれば即座に配信

**ワークフロー設計（`.github/workflows/collect-and-deliver.yml`）：**
```yaml
name: 情報収集・配信

on:
  schedule:
    # 30分ごとに実行
    - cron: "*/30 * * * *"
  workflow_dispatch:

jobs:
  collect-and-deliver:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - name: 情報収集・配信実行
        env:
          LINE_CHANNEL_ACCESS_TOKEN: ${{ secrets.LINE_CHANNEL_ACCESS_TOKEN }}
        run: python src/collect_and_deliver.py
```

**収集・配信スクリプト（`src/collect_and_deliver.py`）：**
- 有効なサイトを読み込み
- 各サイトの`check_interval_minutes`をチェック
- 収集タイミングが来ているサイトのみ収集
- 差分検知で新着情報を抽出
- 新着情報を配信

### 5. サイト追加の簡易化

**ツール：`tools/add_site.py`**
```bash
python tools/add_site.py \
  --name "AI情報サイト" \
  --url "https://example.com/ai-news" \
  --category "AI" \
  --interval 60
```

**自動検出機能：**
1. URLからRSSフィードを自動検出
2. RSSが見つかればRSSリーダーを使用
3. RSSが見つからなければスクレイピング設定を推奨
4. 設定ファイルを自動生成

**将来的な自動サイト発見：**
- カテゴリキーワードでWeb検索
- 情報発信サイトを自動発見
- サイトの評価・フィルタリング
- 管理者承認後に自動追加

### 6. メール要約機能（将来対応）

**設計方針：**
- IMAP/POP3でメール受信
- メール本文から情報を抽出
- AI要約（OpenAI API、無料枠を考慮）
- 情報アイテムとして登録

**実装例（`src/collectors/email_processor.py`）：**
```python
class EmailProcessor(BaseInformationCollector):
    """メールから情報を抽出・要約"""
    
    def collect(self, site_config: dict) -> List[InformationItem]:
        # メール受信
        # 本文抽出
        # AI要約（オプション）
        # 情報アイテム化
        pass
```

### 7. サービス紹介サイト

**初期実装（静的サイト）：**
- GitHub Pagesでホスティング
- `docs/sites/`ディレクトリに各サイトの説明ページ
- `index.html`でサイト一覧を表示
- サイト追加時に自動でページ生成

**ディレクトリ構造：**
```
docs/
├── sites/
│   ├── index.md          # サイト一覧
│   ├── ai_site_001.md    # 個別サイトページ
│   └── drone_site_001.md
└── _config.yml           # GitHub Pages設定
```

**将来的な拡張：**
- サブスクリプション管理機能
- 認証システム（Firebase Auth等）
- 決済処理（Stripe等）
- 動的コンテンツ（Firebase Hosting + Functions）

### 8. 実装フェーズ（更新版）

#### Phase 1: 基盤構築（1-2週間）
1. プロジェクト構造作成
2. LINE Bot基本機能（Webhook、メッセージ受信）
3. ユーザー登録機能（LINE Bot内）
4. 統一情報収集インターフェース実装
5. 1つのサイト（AI）のスクレイパー実装
6. 基本的な配信機能

**成果物：**
- ユーザーがLINE Botで登録できる
- AIカテゴリの1サイトから情報を収集・配信できる

#### Phase 2: 情報収集拡張（1-2週間）
1. 差分検知システム実装
2. 複数サイト対応（AI: 2-3サイト、ドローン: 1-2サイト）
3. RSSリーダー実装
4. サイト追加ツール実装
5. データ永続化（JSON）

**成果物：**
- 複数サイトから情報を収集
- 新着情報のみを配信
- 簡単にサイトを追加できる

#### Phase 3: 配信機能強化（1週間）
1. GitHub Actionsでの自動実行
2. カテゴリ別グループ管理
3. リアルタイム配信（30分間隔）
4. 情報検索機能

**成果物：**
- 自動で情報収集・配信
- カテゴリごとにグループ配信
- ユーザーが情報を検索できる

#### Phase 4: 高度な機能（2-3週間）
1. メール要約機能（オプション）
2. サービス紹介サイト（GitHub Pages）
3. 自動サイト発見機能（将来対応）
4. 統計・レポート機能

**成果物：**
- メールから情報を抽出できる
- サイト一覧をWebで公開
- 運用統計を確認できる

### 9. 無料枠での運用戦略

#### GitHub Actions
- **制限：** 2,000分/月（無料枠）
- **運用：** 30分間隔で実行 = 1,440回/月 = 約1,440分/月
- **対策：** 必要に応じて間隔を調整（60分間隔なら約720分/月）

#### ホスティング（Webhook用）
- **Render.com：** 無料枠750時間/月（推奨）
- **Railway：** $5相当/月（無料枠）
- **Fly.io：** 無料枠あり

#### データストレージ
- **GitHub：** JSONファイル（無制限、無料）
- **将来的に：** Supabase（無料枠: 500MB、2GB転送/月）

### 10. プロジェクト構造（最終案）

```
LINEDev-template-informationDeliveryBot/
├── .github/
│   └── workflows/
│       └── collect-and-deliver.yml    # 自動収集・配信
├── docs/
│   ├── sites/                         # サイト紹介ページ
│   │   ├── index.md
│   │   └── [site_id].md
│   ├── first-prompt.md
│   └── implementation-plan-*.md
├── src/
│   ├── __init__.py
│   ├── collectors/                    # 情報収集システム
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── scraper.py
│   │   ├── rss_reader.py
│   │   ├── email_processor.py
│   │   └── site_config.py
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
├── render.yaml                        # Render.com設定
└── README.md
```

### 11. 次のステップ

1. **Phase 1の実装開始**
   - プロジェクト構造作成
   - LINE Bot基本機能実装
   - ユーザー登録機能実装

2. **初期サイトの選定**
   - AIカテゴリ: 2-3サイト
   - ドローンカテゴリ: 1-2サイト

3. **開発環境セットアップ**
   - LINE Developers設定
   - ローカル開発環境構築

---

**作成日時：** 2025-01-12T19:50:03
**バージョン：** 1.0

