# 次の実装計画（2025-01-18）

## 📊 現在の実装状況

### ✅ 完了済み

#### 基盤システム
- [x] LINE Bot基本機能（Webhookサーバー、ユーザー登録、購読管理）
- [x] 情報収集インターフェース（`collectors/base.py`）
- [x] 差分検知システム（`diff_detector.py`）
- [x] データ永続化システム（`storage.py`）
- [x] サイト管理機能（個別ファイル管理、`sites.json`自動集約）

#### 情報収集
- [x] メール受信・要約方式（`EmailCollector`）
- [x] RSSリーダー実装（`RSSReaderCollector`）
- [x] サイト設定バリデーション

#### 配信・自動化
- [x] 情報収集・配信実行スクリプト（`collect_and_deliver.py`）
- [x] GitHub Actionsワークフロー（3時間間隔での自動実行）
- [x] CI/CDワークフロー（コード品質チェック、テスト自動実行）

#### デプロイ・運用
- [x] Webhookサーバーデプロイ設定（Render.com対応）
- [x] 実際のサイトデータ追加（AI Weekly）
- [x] Webhookサーバーのデプロイ完了

#### ツール・ドキュメント
- [x] サイト追加ツール（`tools/add_site.py`）
- [x] チャネル作成Issue自動生成機能
- [x] ドキュメント整理・カテゴリ別分類

---

## 🎯 次の実装計画（優先順位順）

### 優先度1: サイト単位購読機能の実装 ⭐ 最優先

**目的**: ユーザーが特定の情報配信サービス（例：AI Weekly）単位で購読できるようにする

**推定時間**: 3-4時間

#### 実装内容

##### 段階1: UserManagerの拡張（1時間）

**ファイル**: `src/user_manager.py`

**追加メソッド**:

```python
def subscribe_site(self, user_id: str, site_id: str) -> bool:
    """
    サイトを購読
    
    Args:
        user_id: LINEユーザーID
        site_id: サイトID
        
    Returns:
        bool: 購読が成功したかどうか
    """
    # 実装: subscribed_sitesに追加

def unsubscribe_site(self, user_id: str, site_id: str) -> bool:
    """
    サイトの購読を解除
    
    Args:
        user_id: LINEユーザーID
        site_id: サイトID
        
    Returns:
        bool: 解除が成功したかどうか
    """
    # 実装: subscribed_sitesから削除

def get_subscribed_users_by_site(self, site_id: str) -> List[str]:
    """
    サイトを購読しているユーザーIDリストを取得
    
    Args:
        site_id: サイトID
        
    Returns:
        List[str]: ユーザーIDリスト
    """
    # 実装: subscribed_sitesに含まれるユーザーを抽出
```

**確認項目**:
- [ ] `subscribed_sites`フィールドが既に存在することを確認
- [ ] メソッドが正しく動作するかテスト

---

##### 段階2: 配信ロジックの拡張（1-1.5時間）

**ファイル**: `src/collect_and_deliver.py`

**変更内容**:

```python
def _deliver_new_items(new_items, user_manager, line_notifier):
    # 既存のカテゴリ単位配信（維持）
    # サイト単位配信を追加
    
    # 配信済みユーザーをトラッキング（重複防止）
    delivered_users = set()
    
    # サイト単位で配信（優先）
    for item in new_items:
        site_id = item.site_id
        user_ids = user_manager.get_subscribed_users_by_site(site_id)
        
        for user_id in user_ids:
            if user_id not in delivered_users:
                # 配信実行
                line_notifier.send_information_items(user_id, [item.to_dict()])
                delivered_users.add(user_id)
    
    # カテゴリ単位で配信（サイト購読で配信済みはスキップ）
    for category, items in items_by_category.items():
        user_ids = user_manager.get_subscribed_users(category)
        
        for user_id in user_ids:
            if user_id not in delivered_users:
                # 配信実行
                # ...
```

**確認項目**:
- [ ] サイト単位配信が正しく動作する
- [ ] 重複配信が防止される
- [ ] カテゴリ購読との共存が機能する

---

##### 段階3: LINE Botコマンドの拡張（1時間）

**ファイル**: `src/webhook_server.py`

**追加コマンドハンドラ**:

```python
def handle_site_subscribe_command(reply_token: str, user_id: str, site_id: str, notifier: LineNotifier):
    """
    サイト購読コマンドを処理
    
    コマンド例: "サイト購読 ai_weekly"
    """
    # ユーザー登録チェック
    # subscribe_site()を呼び出し
    # 応答メッセージを送信

def handle_site_unsubscribe_command(reply_token: str, user_id: str, site_id: str, notifier: LineNotifier):
    """
    サイト購読解除コマンドを処理
    
    コマンド例: "サイト購読解除 ai_weekly"
    """
    # unsubscribe_site()を呼び出し
    # 応答メッセージを送信

def handle_subscription_list_command(reply_token: str, user_id: str, notifier: LineNotifier):
    """
    購読一覧コマンドを処理
    
    コマンド: "購読一覧"
    """
    # カテゴリ購読とサイト購読の両方を表示
    # メッセージフォーマット:
    # "【カテゴリ】
    #  - AI
    #  
    # 【サイト】
    #  - AI Weekly (ai_weekly)"
```

**コマンドパーサーの拡張**:

```python
# handle_text_message()内で追加
elif message_text.startswith("サイト購読 ") or message_text.startswith("サイト購読　"):
    # 全角スペース対応
    site_id = message_text.replace("サイト購読 ", "").replace("サイト購読　", "").strip()
    handle_site_subscribe_command(reply_token, user_id, site_id, notifier)

elif message_text.startswith("サイト購読解除 ") or message_text.startswith("サイト購読解除　"):
    site_id = message_text.replace("サイト購読解除 ", "").replace("サイト購読解除　", "").strip()
    handle_site_unsubscribe_command(reply_token, user_id, site_id, notifier)

elif message_text == "購読一覧":
    handle_subscription_list_command(reply_token, user_id, notifier)
```

**確認項目**:
- [ ] コマンドが正しく認識される
- [ ] エラーハンドリングが適切
- [ ] ヘルプメッセージを更新

---

##### 段階4: テストと動作確認（0.5-1時間）

**テスト内容**:
1. **ユニットテスト**: UserManagerの新メソッド
2. **統合テスト**: サイト購読・配信のE2Eテスト
3. **LINE Botでの動作確認**:
   - `サイト購読 ai_weekly`
   - `購読一覧`
   - `サイト購読解除 ai_weekly`

**確認項目**:
- [ ] サイト購読が正しく動作する
- [ ] 配信がサイト単位で行われる
- [ ] 重複配信が防止される
- [ ] エラーケースが適切に処理される

---

### 優先度2: チャネル管理機能の実装

**目的**: 複数LINEチャネルを管理し、サイトやカテゴリごとにチャネルを分離

**推定時間**: 4-5時間

#### 実装内容

##### 段階1: チャネル設定管理機能（1.5時間）

**新規ファイル**: `src/channel_manager.py`

```python
class ChannelManager:
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def get_channel_for_site(self, site_id: str) -> Optional[Dict]:
        """サイトIDに対応するチャネル設定を取得"""
        # channels.jsonから検索
    
    def get_channel_for_category(self, category: str) -> Optional[Dict]:
        """カテゴリに対応するチャネル設定を取得"""
        # channels.jsonから検索
    
    def get_all_channels(self) -> List[Dict]:
        """すべてのチャネル設定を取得"""
        # channels.jsonから読み込み
```

**ファイル**: `src/storage.py` に追加

```python
def load_channels(self) -> Optional[Dict]:
    """チャネル設定を読み込み"""
    return self.load_json("channels.json")

def save_channels(self, channels_data: Dict) -> bool:
    """チャネル設定を保存"""
    return self.save_json("channels.json", channels_data)
```

---

##### 段階2: CLIツールの実装（1.5時間）

**新規ファイル**: `tools/manage_channel.py`

**コマンド例**:

```bash
# チャネル追加
python tools/manage_channel.py add \
  --channel-id channel_ai_weekly \
  --access-token "xxx..." \
  --secret "yyy..." \
  --site-id ai_weekly

# チャネル一覧
python tools/manage_channel.py list

# チャネル有効化/無効化
python tools/manage_channel.py enable channel_ai_weekly
python tools/manage_channel.py disable channel_ai_weekly
```

---

##### 段階3: 配信ロジックの変更（1時間）

**ファイル**: `src/collect_and_deliver.py`

**変更内容**:

```python
from src.channel_manager import ChannelManager

# ChannelManagerの初期化
channel_manager = ChannelManager(storage)

def _deliver_new_items(new_items, user_manager, line_notifier, channel_manager):
    # チャネルごとにアイテムをグループ化
    # サイト優先、カテゴリはフォールバック
    # チャネルごとにLineNotifierを初期化して配信
```

---

##### 段階4: Webhookサーバーの拡張（1-1.5時間）

**ファイル**: `src/webhook_server.py`

**変更内容**:
- 複数チャネル対応
- パスベースルーティング: `/webhook/{channel_id}`
- またはリクエストヘッダーからチャネルを特定

---

### 優先度3: 情報収集・配信の改善

**目的**: システムの安定性向上と問題の早期発見

**推定時間**: 2-3時間

#### 実装内容

##### 段階1: ログ改善（1時間）

**改善点**:
- 収集・配信ログの詳細化
- エラーログの構造化
- 統計情報の記録

##### 段階2: エラーハンドリング強化（1時間）

**改善点**:
- メール受信エラーの詳細化
- LINE配信失敗時のリトライ機能
- 一時的なエラーと恒久的なエラーの区別

##### 段階3: 動作確認とテスト（0.5-1時間）

- GitHub Actionsワークフローの手動実行
- 実際のメール収集・配信の確認

---

## 📋 実装順序の推奨

### フェーズ1: コア機能の拡張（1週間）

1. **サイト単位購読機能**（優先度1）- 3-4時間
   - ユーザーニーズに直接対応
   - 既存機能との共存が容易

2. **情報収集・配信の改善**（優先度3）- 2-3時間
   - システムの安定性確保

### フェーズ2: 運用機能の拡張（1週間）

3. **チャネル管理機能**（優先度2）- 4-5時間
   - 複数チャネル対応
   - スケーラビリティの向上

---

## 🎯 次のステップ（具体的）

### 即座に開始可能: サイト単位購読機能

**推奨理由**:
1. ユーザーの明確なニーズに対応
2. 実装コストが適度（3-4時間）
3. 既存機能との共存が容易
4. テストが容易

**実装開始手順**:

1. **作業ブランチの作成**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/site-based-subscription
   ```

2. **段階1から開始**
   - `src/user_manager.py`の拡張
   - メソッドの実装とテスト

3. **段階ごとにコミット**
   - 各段階完了後にコミット・プッシュ

---

## 📊 実装時間見積もり

| 優先度 | 機能 | 推定時間 | 累計 |
|--------|------|----------|------|
| 1 | サイト単位購読機能 | 3-4時間 | 3-4時間 |
| 2 | チャネル管理機能 | 4-5時間 | 7-9時間 |
| 3 | 情報収集・配信改善 | 2-3時間 | 9-12時間 |

**合計**: 約9-12時間（1-2週間で完了可能）

---

## 🔗 関連ドキュメント

- サイト単位購読提案: `docs/site-management/SITE_BASED_SUBSCRIPTION_PROPOSAL.md`
- チャネル管理提案: `docs/channel-management/LINE_CHANNEL_AUTO_MANAGEMENT_PROPOSAL.md`
- 次の実装オプション: `docs/proposals/NEXT_IMPLEMENTATION_OPTIONS.md`

---

**作成日**: 2025-01-18

