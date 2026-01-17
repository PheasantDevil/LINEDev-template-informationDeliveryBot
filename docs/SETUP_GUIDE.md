# セットアップガイド

このドキュメントでは、情報配信 LINE Bot を動作させるために必要な手動設定の手順を説明します。

## 📋 必要な手動設定一覧

1. **LINE Developers 設定**（必須）
2. **環境変数の設定**（必須）
3. **初期データファイルの作成**（オプション）
4. **GitHub Secrets 設定**（GitHub Actions 使用時）
5. **Webhook URL 設定**（Webhook サーバーデプロイ後）

---

## 1. LINE Developers 設定（必須）

### 1.1 LINE Developers Console でチャネルを作成

1. [LINE Developers Console](https://developers.line.biz/)にアクセス
2. ログイン後、**「新規プロバイダー」**を作成
3. **「Messaging API」**チャネルを作成
   - チャネル名: 例）情報配信 Bot
   - チャネル説明: 例）最新情報を配信する Bot
   - カテゴリ: 適切なものを選択

### 1.2 チャネルアクセストークンの取得

1. 作成したチャネルの**「Messaging API 設定」**タブを開く
2. **「チャネルアクセストークン」**セクションで**「発行」**ボタンをクリック
3. 表示されたトークンをコピーして保存
   - ⚠️ **このトークンは一度しか表示されません。必ず保存してください**

### 1.3 チャネルシークレットの取得

1. 同じページの**「チャネルシークレット」**セクションを確認
2. チャネルシークレットをコピーして保存

### 1.4 Webhook URL の設定（後で設定）

- Webhook サーバーをデプロイした後に設定します（手順 5 を参照）

---

## 2. 環境変数の設定（必須）

### 2.1 ローカル開発環境

#### 方法 A: `.env`ファイルを使用（推奨）

プロジェクトルートに`.env`ファイルを作成：

```bash
# .envファイル
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token_here
LINE_CHANNEL_SECRET=your_channel_secret_here

# Gmail設定（メール方式使用時）
GMAIL_ACCOUNT=infobot.delivery@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here

# Gemini API設定（AI要約使用時）
GEMINI_API_KEY=your_gemini_api_key_here
```

⚠️ `.env`ファイルは`.gitignore`に含まれているため、Git にはコミットされません。

#### 方法 B: 環境変数を直接設定

```bash
# macOS/Linux
export LINE_CHANNEL_ACCESS_TOKEN='your_channel_access_token_here'
export LINE_CHANNEL_SECRET='your_channel_secret_here'

# Windows (PowerShell)
$env:LINE_CHANNEL_ACCESS_TOKEN='your_channel_access_token_here'
$env:LINE_CHANNEL_SECRET='your_channel_secret_here'
```

### 2.2 ホスティング環境（Render.com 等）

ホスティングサービスの環境変数設定画面で以下を設定：

- `LINE_CHANNEL_ACCESS_TOKEN`: チャネルアクセストークン
- `LINE_CHANNEL_SECRET`: チャネルシークレット

**Render.com の場合：**

1. Dashboard > サービス選択 > Environment
2. 「Add Environment Variable」をクリック
3. 上記の 2 つの環境変数を追加

---

## 3. 初期データファイルの作成（オプション）

サイト一覧機能を使用する場合、初期データファイルを作成します。

### 3.1 `data/sites/`ディレクトリの設定

サイト設定は個別ファイルで管理されます。各サイトは`data/sites/[site_id].json`として保存されます。

```bash
# sitesディレクトリが存在することを確認（自動生成されます）
ls -la data/sites/
```

新しいサイトを追加する場合は、`data/sites/`ディレクトリ内に`[site_id].json`ファイルを作成します。

例：`data/sites/ai_weekly.json`

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
  "created_at": "2025-01-12T00:00:00",
  "last_collected_at": null,
  "stats": {
    "total_collected": 0,
    "last_7_days": 0
  }
}
```

設定例ファイルは`data/sites/*.example.json`を参照してください。

または、`tools/add_site.py`を使用してサイトを追加することもできます（実装後）。

---

## 4. GitHub Secrets 設定（GitHub Actions 使用時）

GitHub Actions で自動実行する場合、Secrets を設定します。

### 4.1 Secrets の設定手順

1. GitHub リポジトリのページで **Settings** > **Secrets and variables** > **Actions** を開く
2. **「New repository secret」**をクリック
3. 以下の Secrets を追加：

| Secret 名                   | 値                       | 説明                  |
| --------------------------- | ------------------------ | --------------------- |
| `LINE_CHANNEL_ACCESS_TOKEN` | チャネルアクセストークン | LINE Messaging API 用 |
| `LINE_CHANNEL_SECRET`       | チャネルシークレット     | Webhook 署名検証用    |

### 4.2 確認

- Secrets は暗号化されて保存されます
- リポジトリのコラボレーターのみが参照可能です

---

## 5. Webhook URL 設定（Webhook サーバーデプロイ後）

Webhook サーバーをデプロイした後、LINE Developers Console で Webhook URL を設定します。

### 5.1 Webhook サーバーのデプロイ

**Render.com の場合：**

1. Render.com で New Web Service を作成
2. GitHub リポジトリを接続
3. 環境変数を設定（手順 2.2 参照）
4. デプロイ
5. デプロイ完了後、Webhook URL を確認（例: `https://your-app.onrender.com/webhook`）

### 5.2 LINE Developers Console で Webhook URL を設定

1. LINE Developers Console > 作成したチャネル > **「Messaging API 設定」**タブ
2. **「Webhook URL」**セクションで以下を設定：
   - Webhook URL: `https://your-app.onrender.com/webhook`
   - **「検証」**ボタンをクリックして接続を確認
3. **「Webhook の利用」**を**ON**に設定
4. **「応答メッセージ」**を**OFF**に設定（Bot で応答するため）

### 5.3 動作確認

1. LINE アプリで Bot を友だち追加
2. Bot に「登録」と送信
3. ウェルカムメッセージが返ってくれば成功

---

## 6. 動作確認チェックリスト

### ローカル環境

- [ ] `.env`ファイルまたは環境変数が設定されている
- [ ] `pip install -r requirements.txt`で依存関係をインストール済み
- [ ] `python src/webhook_server.py`でサーバーが起動する
- [ ] サーバーが`http://localhost:5000`で起動している

### ホスティング環境

- [ ] 環境変数が設定されている
- [ ] Webhook サーバーがデプロイされている
- [ ] Webhook URL が LINE Developers Console に設定されている
- [ ] Webhook の利用が ON になっている

### LINE Bot

- [ ] Bot を友だち追加できる
- [ ] 「登録」コマンドでユーザー登録できる
- [ ] 「サイト一覧」コマンドでサイト一覧が表示される（初期データがある場合）

---

## 7. トラブルシューティング

### エラー: `LINE_CHANNEL_ACCESS_TOKEN が設定されていません`

**原因**: 環境変数が設定されていない

**解決方法**:

- `.env`ファイルを作成して設定
- または環境変数を直接設定

### エラー: 署名検証失敗

**原因**: チャネルシークレットが正しく設定されていない、または Webhook URL が間違っている

**解決方法**:

- `LINE_CHANNEL_SECRET`環境変数を確認
- LINE Developers Console の Webhook URL を確認

### Webhook が動作しない

**原因**: Webhook URL が正しく設定されていない、またはサーバーが起動していない

**解決方法**:

- Webhook URL が正しいか確認（末尾に`/webhook`が含まれているか）
- サーバーのログを確認
- LINE Developers Console で「検証」ボタンをクリック

---

## 8. 次のステップ

セットアップが完了したら：

1. **情報収集機能の実装**（Phase 2）
2. **初期サイトの追加**
3. **自動配信機能の実装**（Phase 3）

詳細は`docs/20260112/002-prompt.md`を参照してください。

---

**最終更新**: 2025-01-12
