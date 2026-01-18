# 次の実装内容（優先順位順）

## 🎯 実装優先度と具体的な内容

### 優先度 1: RSS リーダー実装（`src/collectors/rss_reader.py`）

**目的**: メール方式の補完として、RSS フィードから情報を収集できるようにする

**実装内容**:

1. **`RSSReaderCollector`クラスの実装**

   - `BaseInformationCollector`を継承
   - `collect()`メソッドで RSS/Atom フィードをパース
   - `should_collect()`で収集タイミングを判定
   - `mark_as_collected()`で収集完了を記録

2. **RSS/Atom フィードのパース**

   - `feedparser`ライブラリを使用（`requirements.txt`に追加）
   - RSS 2.0、Atom 1.0、RDF に対応
   - エントリから`InformationItem`を生成
   - タイトル、URL、公開日時、要約を抽出

3. **エラーハンドリング**

   - フィード URL のアクセスエラー処理
   - パースエラーの処理
   - タイムアウト処理（30 秒）
   - リトライ機能（最大 3 回）

4. **`collect_and_deliver.py`への統合**
   - `_create_collector()`に`rss`タイプを追加
   - `src/collectors/__init__.py`に`RSSReaderCollector`を追加

**ファイル構成**:

```
src/collectors/rss_reader.py  (新規作成)
requirements.txt              (feedparser追加)
src/collectors/__init__.py   (RSSReaderCollector追加)
src/collect_and_deliver.py   (_create_collector更新)
```

**実装例**:

```python
class RSSReaderCollector(BaseInformationCollector):
    def collect(self, site_config: Dict) -> List[InformationItem]:
        feed_url = site_config.get('collector_config', {}).get('feed_url')
        # feedparserでフィードを取得・パース
        # エントリからInformationItemを生成
        # 重複排除（URLベース）
```

---

### 優先度 2: サイト設定のバリデーション（`src/storage.py`拡張）

**目的**: サイト設定の整合性を保証し、エラーを早期発見する

**実装内容**:

1. **`Storage.validate_site()`メソッドの追加**

   - 必須フィールドのチェック（`id`, `name`, `url`, `category`, `collector_type`）
   - 収集方式ごとの設定チェック
   - データ型の検証
   - 値の範囲チェック（例: `check_interval_minutes` > 0）

2. **収集方式別のバリデーション**

   - `email`: `email_account_id`, `subscription_email`の必須チェック
   - `rss`: `feed_url`の必須チェック、URL 形式の検証
   - `scraper`: `selector`の必須チェック

3. **`save_site()`への統合**
   - 保存前に自動的にバリデーションを実行
   - エラー時は例外を発生させて保存を拒否

**実装例**:

```python
def validate_site(self, site: Dict) -> Tuple[bool, List[str]]:
    """サイト設定をバリデーション"""
    errors = []

    # 必須フィールドチェック
    if not site.get('id'):
        errors.append('idは必須です')

    # 収集方式別チェック
    collector_type = site.get('collector_type')
    if collector_type == 'email':
        config = site.get('collector_config', {})
        if not config.get('subscription_email'):
            errors.append('email方式の場合、subscription_emailは必須です')

    return len(errors) == 0, errors
```

---

### 優先度 3: 連携テストの実施

**目的**: 実際の LINE Bot との連携を確認し、動作を検証する

**実装内容**:

1. **ローカル環境でのテスト**

   - ngrok を使用して Webhook サーバーを公開
   - LINE Developers で Webhook URL を設定
   - 各コマンドの動作確認
     - ユーザー登録
     - 購読設定
     - サイト一覧表示
     - ヘルプ表示

2. **情報収集・配信の動作確認**

   - テスト用のメールを送信
   - 情報収集の実行
   - LINE 配信の確認
   - エラーハンドリングの確認

3. **テスト結果の記録**
   - `docs/TESTING_GUIDE.md`に結果を追記
   - 発見した問題点を記録
   - 修正内容を記録

**テスト手順**:

1. ngrok で Webhook サーバーを起動
2. LINE Developers で Webhook URL を設定
3. LINE Bot にメッセージを送信して動作確認
4. テスト用メールを送信して情報収集を確認
5. 配信が正常に行われることを確認

---

### 優先度 4: Webhook サーバーのデプロイ

**目的**: 本番環境で Webhook サーバーを稼働させる

**実装内容**:

1. **Render.com（または他のホスティング）でのデプロイ**

   - `Procfile`を使用して Webhook サーバーを起動
   - 環境変数の設定
   - Webhook URL の設定

2. **デプロイ設定ファイルの作成**

   - `render.yaml`（Render.com の場合）
   - または他のホスティングサービスの設定ファイル

3. **動作確認**
   - Webhook URL が正しく設定されているか確認
   - LINE Bot からのメッセージが受信できるか確認
   - エラーログの確認

---

### 優先度 5: スクレイパー実装（`src/collectors/scraper.py`）

**目的**: メール方式、RSS 方式の補完として、スクレイピングで情報を収集

**実装内容**:

1. **`ScraperCollector`クラスの実装**

   - `BaseInformationCollector`を継承
   - BeautifulSoup を使用した HTML パース
   - CSS セレクターによる柔軟な情報抽出

2. **エラーハンドリングとリトライ機能**

   - ネットワークエラーの処理
   - タイムアウト処理
   - リトライ機能（最大 3 回、指数バックオフ）

3. **`collect_and_deliver.py`への統合**
   - `_create_collector()`に`scraper`タイプを追加

---

### 優先度 6: サイト更新検知方式（`src/collectors/change_detector.py`）

**目的**: ページの変更を検知して情報を収集

**実装内容**:

1. **`ChangeDetectorCollector`クラスの実装**

   - `BaseInformationCollector`を継承
   - ページハッシュ値ベースの変更検知
   - 変更検知後の詳細取得

2. **ハッシュ値の管理**
   - 前回のハッシュ値を保存
   - 現在のハッシュ値と比較
   - 変更があった場合のみ詳細を取得

---

## 📋 実装順序の推奨

1. **RSS リーダー実装**（約 2-3 時間）

   - 最も実装が容易で、多くのサイトで利用可能
   - メール方式の補完として重要

2. **サイト設定のバリデーション**（約 1 時間）

   - 品質向上に直結
   - エラーを早期発見できる

3. **連携テストの実施**（約 2-3 時間）

   - 実際の動作確認が重要
   - 問題点を早期に発見できる

4. **Webhook サーバーのデプロイ**（約 1-2 時間）

   - 本番環境での動作確認
   - ユーザーが実際に使用できる状態にする

5. **スクレイパー実装**（約 3-4 時間）

   - 補完的な機能
   - RSS 方式が使えないサイトに対応

6. **サイト更新検知方式**（約 2-3 時間）
   - 補完的な機能
   - 特定のサイトにのみ有効

---

## 🎯 次のステップ

**推奨**: 優先度 1（RSS リーダー実装）から開始

**理由**:

- 実装が比較的容易
- 多くのサイトで利用可能
- メール方式の補完として重要
- 即座に価値を提供できる

**実装開始の準備**:

1. `feedparser`ライブラリを`requirements.txt`に追加
2. `src/collectors/rss_reader.py`を作成
3. `BaseInformationCollector`を継承したクラスを実装
4. `collect_and_deliver.py`に統合

---

**最終更新**: 2025-01-15
