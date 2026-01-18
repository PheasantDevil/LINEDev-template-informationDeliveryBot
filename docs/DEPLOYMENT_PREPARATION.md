# Webhookサーバーデプロイ準備ガイド

## 📋 概要

このドキュメントは、Webhookサーバーを本番環境（Render.com）にデプロイする前の準備手順をまとめたものです。

---

## ✅ デプロイ前チェックリスト

### 必須環境変数

- [x] `LINE_CHANNEL_ACCESS_TOKEN` - LINE Channel Access Token（必須）
- [x] `LINE_CHANNEL_SECRET` - LINE Channel Secret（必須）
- [ ] `GMAIL_ACCOUNT` - メール収集用Gmailアカウント（オプション、動作確認済み）
- [ ] `GMAIL_APP_PASSWORD` - Gmailアプリパスワード（オプション、動作確認済み）
- [ ] `GEMINI_API_KEY` - Gemini APIキー（オプション、要約機能用、動作確認済み）

### ファイル確認

- [x] `Procfile` - Webサーバーの起動コマンド定義
- [x] `render.yaml` - Render.com設定ファイル
- [x] `requirements.txt` - Python依存関係
- [x] `src/webhook_server.py` - Webhookサーバー実装
- [x] `src/collect_and_deliver.py` - 情報収集・配信スクリプト

### 設定ファイル確認

- [x] `data/sites/ai_weekly.json` - AI Weekly設定（有効化済み）
- [x] `data/email_accounts.json` - メールアカウント設定

---

## 🔧 デプロイ設定ファイル確認

### Procfile

```procfile
web: gunicorn src.webhook_server:app --bind 0.0.0.0:$PORT
```

**確認事項**:
- [x] `gunicorn`が`requirements.txt`に含まれている
- [x] `src.webhook_server:app`が正しいモジュールパス
- [x] `$PORT`環境変数を使用（Render.comが自動設定）

### render.yaml

```yaml
services:
  - type: web
    name: information-delivery-bot-webhook
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT src.webhook_server:app
    healthCheckPath: /health
```

**確認事項**:
- [x] `plan: free`（無料プラン）
- [x] `healthCheckPath: /health`（ヘルスチェックエンドポイント）
- [x] ビルドコマンドと起動コマンドが正しい

### requirements.txt

**確認事項**:
- [x] `flask>=3.0.0` - Webフレームワーク
- [x] `gunicorn>=21.2.0` - WSGIサーバー
- [x] その他の依存関係が全て含まれている

---

## 📝 デプロイ手順（段階2-1, 2-2）

### 段階2-1: Render.comでのデプロイ準備

1. **Render.comアカウントの作成**
   - https://render.com にアクセス
   - GitHubアカウントでサインアップ

2. **GitHubリポジトリ連携**
   - Dashboard → "New +" → "Web Service"
   - GitHubリポジトリを選択: `LINEDev-template-informationDeliveryBot`
   - ブランチ: `main`（推奨）

3. **環境変数の設定**
   
   Render.comダッシュボードで以下を設定：
   
   | キー | 値 | 必須 | 説明 |
   |-----|-----|------|------|
   | `LINE_CHANNEL_ACCESS_TOKEN` | `(LINE Developersから取得)` | ✅ | LINE Channel Access Token |
   | `LINE_CHANNEL_SECRET` | `(LINE Developersから取得)` | ✅ | LINE Channel Secret |
   | `PORT` | `10000` | ❌ | ポート番号（Render.comが自動設定） |
   | `GMAIL_ACCOUNT` | `infobot.delivery@gmail.com` | ❌ | メール収集用Gmailアカウント |
   | `GMAIL_APP_PASSWORD` | `(設定済み)` | ❌ | Gmailアプリパスワード |
   | `GEMINI_API_KEY` | `(設定済み)` | ❌ | Gemini APIキー |

   **注意**: `LINE_CHANNEL_ACCESS_TOKEN`と`LINE_CHANNEL_SECRET`は必須です。

### 段階2-2: デプロイの実行

1. **Webサービスの作成**
   - 設定を確認して「Create Web Service」をクリック
   - 初回デプロイが自動的に開始される

2. **デプロイの確認**
   - ビルドログを確認
   - エラーがないことを確認
   - デプロイ完了を待つ（約2-5分）

3. **ヘルスチェックの確認**
   ```bash
   curl https://your-service-url.onrender.com/health
   # 期待される結果: OK
   ```
   
   **期待されるレスポンス**:
   ```
   OK
   ```

4. **サービスURLの確認**
   - デプロイ後に表示されるサービスURLをメモ
   - 例: `https://information-delivery-bot-webhook.onrender.com`
   - このURLをLINE Developersで設定する

---

## 🔗 LINE Developers設定（段階2-3）

### Webhook URLの設定

1. **LINE Developers Consoleにアクセス**
   - https://developers.line.biz/console/
   - チャンネルを選択

2. **Webhook設定**
   - "Messaging API" → "Webhook settings"
   - Webhook URL: `https://your-service-url.onrender.com/webhook`
   - 「Verify」ボタンで検証

3. **Webhookの有効化**
   - "Use webhook"をON
   - "Auto-reply messages"をOFF（Botの応答を制御するため）

---

## 🧪 テスト手順（段階2-4）

### 1. ヘルスチェックテスト

```bash
curl https://your-service-url.onrender.com/health
```

### 2. ユーザー登録テスト

LINEアプリでBotにメッセージを送信：
```
登録
```

**期待される応答**:
```
登録が完了しました！

利用可能なコマンド:
- 購読 [カテゴリ名] - カテゴリを購読
- 購読解除 [カテゴリ名] - 購読を解除
- 購読一覧 - 現在の購読状況を表示
- サイト一覧 - 利用可能なサイト一覧を表示
```

### 3. 購読機能テスト

```
購読 AI
```

**期待される応答**:
```
AIカテゴリを購読しました。
```

### 4. サイト一覧テスト

```
サイト一覧
```

**期待される応答**:
```
利用可能なサイト:

1. AI Weekly
   URL: https://aiweekly.co/
   カテゴリ: AI
   有効: はい
```

### 5. ログ確認

Render.comダッシュボードで：
- "Logs"タブを開く
- エラーログがないことを確認
- Webhook受信ログを確認

---

## ⚠️ 注意事項

1. **無料プランの制限**
   - Render.com無料プランは15分間の非アクティブ後にスリープする
   - 初回リクエスト時にウェイクアップが必要（約30秒）
   - 定期的なアクセスが必要な場合は有料プランを検討

2. **環境変数の管理**
   - 機密情報（トークン、パスワード）は環境変数で管理
   - `render.yaml`の`sync: false`設定で、環境変数がコードに含まれないようにする

3. **デプロイ後の動作確認**
   - デプロイ後、必ずヘルスチェックエンドポイントで確認
   - LINE DevelopersでWebhook検証を実行
   - 実際にLINE Botにメッセージを送信して動作確認

4. **ログ監視**
   - Render.comのログ画面でエラーを定期的に確認
   - 問題があれば早期に対応

---

## 📚 関連ドキュメント

- `docs/DEPLOYMENT_GUIDE.md` - 詳細なデプロイ手順
- `docs/DEPLOYMENT_CHECKLIST.md` - デプロイチェックリスト
- `docs/TESTING_GUIDE.md` - テストガイド

---

**最終更新**: 2025-01-18

