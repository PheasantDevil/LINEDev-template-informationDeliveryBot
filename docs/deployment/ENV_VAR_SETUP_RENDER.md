# Render.com環境変数設定手順

## 🔴 問題

ログに以下のエラーが表示されています：
```
❌ LINE Notifier initialization error: LINE_CHANNEL_ACCESS_TOKEN が設定されていません
```

## ✅ 解決方法: 環境変数の設定

Render.comで環境変数を設定する必要があります。

---

## 📋 ステップ1: LINE Developers Consoleから値を取得

### 1. LINE Developers Consoleにアクセス

1. **ブラウザでLINE Developers Consoleを開く**
   - URL: https://developers.line.biz/console/
   - ログイン

2. **チャンネルを選択**
   - プロバイダーを選択
   - Webhookサーバーをデプロイするチャンネルを選択

3. **Channel Access Tokenを取得**
   - 左メニューから「**Messaging API**」をクリック
   - 「**Channel access token**」セクションまでスクロール
   - 「**Issue**」ボタンをクリックしてトークンを発行（まだ発行していない場合）
   - 表示されたトークンをコピー（⚠️ 再表示できません）

4. **Channel Secretを取得**
   - 同じ「Messaging API」ページの上部
   - 「**Channel secret**」の値をコピー

---

## 📋 ステップ2: Render.comで環境変数を設定

### 1. Render.comダッシュボードにアクセス

1. **ブラウザでRender.comダッシュボードを開く**
   - URL: https://dashboard.render.com
   - ログイン

2. **サービスを選択**
   - デプロイしたWebサービス（`information-delivery-bot-webhook`など）をクリック

### 2. 環境変数を追加

1. **「Environment」タブを開く**
   - 左メニューから「**Environment**」をクリック
   - または上部のタブから「**Environment**」を選択

2. **環境変数を追加**

   **環境変数1: LINE_CHANNEL_ACCESS_TOKEN**

   - 「**Add Environment Variable**」をクリック
   - **Key**: `LINE_CHANNEL_ACCESS_TOKEN`
   - **Value**: （LINE Developers ConsoleからコピーしたChannel Access Tokenを貼り付け）
   - 「**Save Changes**」をクリック

   **環境変数2: LINE_CHANNEL_SECRET**

   - 再度「**Add Environment Variable**」をクリック
   - **Key**: `LINE_CHANNEL_SECRET`
   - **Value**: （LINE Developers ConsoleからコピーしたChannel Secretを貼り付け）
   - 「**Save Changes**」をクリック

   **オプション: その他の環境変数**（メール収集・要約機能を使用する場合）

   - `GMAIL_ACCOUNT`: `infobot.delivery@gmail.com`
   - `GMAIL_APP_PASSWORD`: （設定済みのアプリパスワード）
   - `GEMINI_API_KEY`: （設定済みのAPIキー）

### 3. 確認

環境変数が正しく設定されているか確認：

| Key | 状態 | 説明 |
|-----|------|------|
| `LINE_CHANNEL_ACCESS_TOKEN` | ✅ 設定済み | LINE Channel Access Token |
| `LINE_CHANNEL_SECRET` | ✅ 設定済み | LINE Channel Secret |
| `GMAIL_ACCOUNT` | ⚠️ オプション | Gmailアカウント |
| `GMAIL_APP_PASSWORD` | ⚠️ オプション | Gmailアプリパスワード |
| `GEMINI_API_KEY` | ⚠️ オプション | Gemini APIキー |

---

## 📋 ステップ3: サービスの再デプロイ

環境変数を追加・変更すると、Render.comが自動的に再デプロイを開始します。

1. **自動再デプロイの確認**
   - ダッシュボードの上部に「Deploying...」または「Deploy started」と表示される
   - 約2-5分でデプロイが完了する

2. **デプロイ完了を待つ**
   - ステータスが「Live」になるまで待つ
   - 「Logs」タブでデプロイログを確認

---

## 📋 ステップ4: Webhook検証の再試行

デプロイが完了したら、LINE Developers ConsoleでWebhook検証を再試行します。

1. **LINE Developers Consoleに戻る**
   - https://developers.line.biz/console/
   - チャンネルを選択

2. **Webhook設定を確認**
   - 「Messaging API」→「Webhook settings」
   - Webhook URLが正しく設定されていることを確認

3. **検証を実行**
   - 「**Verify**」ボタンをクリック
   - ✅ 緑のチェックマークが表示されれば成功！

---

## ✅ 確認チェックリスト

- [ ] LINE Developers ConsoleからChannel Access Tokenを取得した
- [ ] LINE Developers ConsoleからChannel Secretを取得した
- [ ] Render.comで`LINE_CHANNEL_ACCESS_TOKEN`環境変数を設定した
- [ ] Render.comで`LINE_CHANNEL_SECRET`環境変数を設定した
- [ ] 環境変数設定後、自動再デプロイが開始された
- [ ] デプロイが完了し、ステータスが「Live」になった
- [ ] LINE Developers ConsoleでWebhook検証が成功した

---

## 🔍 トラブルシューティング

### まだエラーが出る場合

1. **環境変数の値を再確認**
   - トークンやシークレットの値に余分なスペースや改行が入っていないか
   - 値が正しくコピーされているか

2. **再デプロイを確認**
   - 環境変数を設定後、再デプロイが完了しているか
   - 「Logs」タブで最新のログを確認

3. **ログで確認**
   - Render.comの「Logs」タブで以下のメッセージがないか確認：
     - `✓ LineNotifier initialized successfully` ← これが表示されれば成功
     - `❌ LINE Notifier initialization error` ← これが出ていれば環境変数の問題

---

**最終更新**: 2025-01-18

