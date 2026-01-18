# LINEチャネル自動管理機能の提案

## 📋 背景

### 現在の実装
- **1つのLINE Botチャネル**: すべてのカテゴリ・サイトで1つのチャネルを使用
- チャネル内でカテゴリやサイトごとに購読管理

### ユーザーの要望
- **チャネル単位の分離**: サイトやカテゴリごとに別々のLINEチャネルを作成
- **マンレス運用**: CLIやコマンドでチャネルを自動作成・管理

---

## 🔍 LINE Developers API の制約と可能性

### LINE Messaging API の制約

⚠️ **重要な制約**:
- LINE Messaging APIには**チャネルをプログラムから自動作成するAPIが提供されていない**
- チャネルの作成は、LINE Developers Consoleで手動で行う必要がある

### 可能な自動化範囲

以下の操作は自動化可能です：

1. ✅ **チャネル情報の取得**: 既存チャネルの情報取得
2. ✅ **Webhook URLの設定**: チャネルのWebhook URLをAPIで設定
3. ✅ **チャネル設定の変更**: 一部の設定をAPIで変更
4. ❌ **チャネルの作成**: APIでは不可能（手動のみ）

---

## 💡 実装アプローチ

### アプローチ1: 事前作成 + 自動設定（推奨）

#### コンセプト

1. **チャネルの事前作成**: 管理画面または手動で必要分のチャネルを作成
2. **自動設定・管理**: 作成されたチャネルを自動的に設定・管理

#### 実装内容

**1. チャネル設定ファイルの管理**

```json
// data/channels.json
{
  "channels": [
    {
      "channel_id": "channel_ai_weekly",
      "channel_access_token": "xxx...",
      "channel_secret": "yyy...",
      "site_id": "ai_weekly",
      "category": "AI",
      "webhook_url": "https://your-service.onrender.com/webhook",
      "enabled": true,
      "created_at": "2025-01-18T10:00:00"
    },
    {
      "channel_id": "channel_ai_category",
      "channel_access_token": "xxx...",
      "channel_secret": "yyy...",
      "category": "AI",
      "webhook_url": "https://your-service.onrender.com/webhook",
      "enabled": true
    }
  ]
}
```

**2. CLIツールの実装**

```bash
# チャネル設定の追加（既存チャネルを登録）
python tools/manage_channel.py add \
  --channel-id channel_ai_weekly \
  --access-token "xxx..." \
  --secret "yyy..." \
  --site-id ai_weekly

# Webhook URLの設定
python tools/manage_channel.py set-webhook \
  --channel-id channel_ai_weekly \
  --webhook-url "https://your-service.onrender.com/webhook"

# チャネル一覧の表示
python tools/manage_channel.py list

# チャネルの有効化/無効化
python tools/manage_channel.py enable channel_ai_weekly
python tools/manage_channel.py disable channel_ai_weekly
```

**3. 配信ロジックの変更**

```python
# collect_and_deliver.py
def _deliver_new_items(new_items, user_manager, channels_config):
    for item in new_items:
        # サイト単位で配信
        site_id = item.site_id
        channel_config = _get_channel_for_site(site_id, channels_config)
        if channel_config:
            notifier = LineNotifier(
                channel_access_token=channel_config["channel_access_token"],
                channel_secret=channel_config["channel_secret"]
            )
            # 配信実行
```

---

### アプローチ2: LINE Developers Console API（調査が必要）

#### 調査項目

LINE Developers APIには以下のAPIが存在する可能性があります：

1. **LINE Developers API v2**: チャネル管理API
   - プロバイダー管理
   - チャネル管理（作成、更新、削除）

**確認方法**:
- LINE Developers API ドキュメントを確認
- LINE Developers API v2 のエンドポイントを調査

**制約**:
- 企業アカウントや特別な権限が必要な可能性
- APIの提供状況が不明

---

## 🔧 実装詳細（アプローチ1）

### 段階1: チャネル設定管理機能

#### 1. チャネル設定のストレージ

```python
# src/storage.py に追加
def load_channels(self) -> Optional[Dict]:
    """チャネル設定を読み込み"""
    return self.load_json("channels.json")

def save_channels(self, channels_data: Dict) -> bool:
    """チャネル設定を保存"""
    return self.save_json("channels.json", channels_data)
```

#### 2. CLI ツールの実装

```python
# tools/manage_channel.py
import argparse
import sys
from pathlib import Path

# チャネル追加
def add_channel(channel_id, access_token, secret, site_id=None, category=None):
    # channels.jsonに追加

# Webhook設定
def set_webhook(channel_id, webhook_url):
    # LINE Messaging APIでWebhook URLを設定
    # 注意: Webhook URLの設定APIは存在するか要確認
```

#### 3. チャネル設定の取得機能

```python
# src/channel_manager.py（新規作成）
class ChannelManager:
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def get_channel_for_site(self, site_id: str) -> Optional[Dict]:
        """サイトIDに対応するチャネル設定を取得"""
        # 実装
    
    def get_channel_for_category(self, category: str) -> Optional[Dict]:
        """カテゴリに対応するチャネル設定を取得"""
        # 実装
```

---

### 段階2: 配信ロジックの変更

#### チャネル単位での配信

```python
# collect_and_deliver.py の変更
from src.channel_manager import ChannelManager

def _deliver_new_items(new_items, user_manager, channel_manager):
    # チャネルごとにアイテムをグループ化
    items_by_channel = {}
    
    for item in new_items:
        # サイト単位のチャネルを優先
        channel = channel_manager.get_channel_for_site(item.site_id)
        if not channel:
            # カテゴリ単位のチャネルにフォールバック
            channel = channel_manager.get_channel_for_category(item.category)
        
        if channel:
            channel_id = channel["channel_id"]
            if channel_id not in items_by_channel:
                items_by_channel[channel_id] = []
            items_by_channel[channel_id].append((channel, item))
    
    # チャネルごとに配信
    for channel_id, items in items_by_channel.items():
        channel_config = items[0][0]  # チャネル設定を取得
        notifier = LineNotifier(
            channel_access_token=channel_config["channel_access_token"],
            channel_secret=channel_config["channel_secret"]
        )
        # 配信実行
```

---

### 段階3: Webhookサーバーの拡張

#### 複数チャネル対応

現在の`webhook_server.py`は1つのチャネルシークレットを想定していますが、複数チャネルに対応する必要があります：

```python
# webhook_server.py の変更
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    
    # チャネルを特定（リクエストヘッダーから、またはルーティングから）
    channel_id = _identify_channel(request)
    channel_config = channel_manager.get_channel(channel_id)
    
    if not channel_config:
        abort(400)
    
    # 署名検証
    notifier = LineNotifier(
        channel_access_token=channel_config["channel_access_token"],
        channel_secret=channel_config["channel_secret"]
    )
    
    # 以降の処理
```

**注意**: LINE Webhookは通常、チャネルごとに異なるエンドポイントを使用するか、リクエストからチャネルを特定する必要があります。

---

## 🚧 実装上の課題と解決策

### 課題1: Webhook URLの自動設定

**問題**: LINE Messaging APIでWebhook URLを自動設定できるか不明

**解決策**:
1. **手動設定**: チャネル作成後、手動でWebhook URLを設定
2. **API調査**: LINE Developers API v2でWebhook設定APIが提供されているか確認
3. **代替案**: チャネル作成時にWebhook URLを設定するテンプレートを提供

### 課題2: チャネルの自動作成

**問題**: LINE Messaging APIではチャネルを自動作成できない

**解決策**:
1. **事前作成**: 必要分のチャネルを事前に手動作成
2. **テンプレート化**: チャネル作成手順をドキュメント化・スクリプト化
3. **半自動化**: チャネル作成チェックリストと登録ツールを提供

### 課題3: 複数チャネルのWebhook管理

**問題**: 1つのWebhookエンドポイントで複数チャネルを処理する方法

**解決策**:
1. **パスベースルーティング**: `/webhook/{channel_id}`のようにパスで分ける
2. **チャネル特定**: リクエストヘッダーや署名からチャネルを特定
3. **複数エンドポイント**: チャネルごとに異なるエンドポイントを設定

---

## 📋 実装計画

### Phase 1: チャネル設定管理（2-3時間）

1. **ストレージ機能の追加**
   - `channels.json`の読み込み・保存機能

2. **CLIツールの実装**
   - `tools/manage_channel.py`の実装
   - チャネル追加、一覧、有効化/無効化

3. **チャネルマネージャーの実装**
   - `src/channel_manager.py`の実装

### Phase 2: 配信ロジックの変更（2-3時間）

1. **配信ロジックの拡張**
   - チャネル単位での配信
   - チャネル設定の取得とLineNotifierの初期化

2. **テスト**
   - チャネル単位配信のテスト

### Phase 3: Webhookサーバーの拡張（3-4時間）

1. **複数チャネル対応**
   - Webhookエンドポイントの拡張
   - チャネル特定ロジックの実装

2. **テスト**
   - 複数チャネルでのWebhook受信テスト

---

## ✅ 結論

### 実現可能性

- ✅ **チャネル設定の自動管理**: 可能（CLIツールで実装）
- ⚠️ **チャネルの自動作成**: **不可能**（LINE APIの制約）
- ✅ **Webhook URLの設定**: **要調査**（APIの提供状況次第）
- ✅ **チャネル単位での配信**: 可能（実装必要）

### 推奨アプローチ

**半自動化アプローチ**:

1. **チャネル作成**: 手動（LINE Developers Console）
   - 作成手順をドキュメント化
   - 必要数を事前に作成

2. **チャネル設定**: 自動（CLIツール）
   - 作成したチャネルの情報をCLIツールで登録
   - チャネル設定の管理を自動化

3. **配信・Webhook**: 自動（実装）
   - チャネル設定に基づいて自動配信
   - Webhookサーバーで複数チャネルに対応

---

## 🔍 次のステップ

1. **LINE Developers API v2の調査**
   - チャネル管理APIの有無を確認
   - Webhook設定APIの有無を確認

2. **プロトタイプ実装**
   - チャネル設定管理機能の実装
   - CLIツールの実装

3. **テスト**
   - 複数チャネルでの動作確認

---

**最終更新**: 2025-01-18

