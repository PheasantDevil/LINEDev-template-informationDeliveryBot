# Webhookサーバーデプロイ実作業手順

このドキュメントは、Render.comへのWebhookサーバーデプロイを段階ごとに具体的に進める手順です。

---

## 🎯 段階2-1: Render.comでのデプロイ準備

### ステップ1: Render.comアカウントの作成

1. **ブラウザでRender.comにアクセス**
   - URL: https://render.com
   - または: https://dashboard.render.com

2. **アカウント作成**
   - 「Get Started for Free」または「Sign Up」をクリック
   - **GitHubアカウントでサインアップ**を選択（推奨）
     - 「Continue with GitHub」をクリック
     - GitHubの認証画面で承認
   - またはメールアドレスでサインアップも可能

3. **確認**
   - ✅ Render.comダッシュボードが表示される
   - ✅ 右上にアカウント名が表示される

**⚠️ 注意**: 無料プランで十分です。有料プランへのアップグレードは不要です。

---

### ステップ2: GitHubリポジトリの連携確認

1. **GitHub連携の確認**
   - 既にGitHubアカウントでサインアップした場合、自動的に連携されています
   - 左上の「Dashboard」をクリック

2. **リポジトリの確認**
   - Render.comからGitHubリポジトリにアクセスできることを確認
   - リポジトリが表示されない場合は、GitHubの認証を再確認

---

### ステップ3: Webサービスの作成（準備）

次のステップで実際にWebサービスを作成しますが、その前に以下を確認してください：

**必要な情報**:
- [ ] LINE Channel Access Token（LINE Developers Consoleから取得）
- [ ] LINE Channel Secret（LINE Developers Consoleから取得）
- [ ] Gmailアカウント（既に設定済み）
- [ ] Gmail App Password（既に設定済み）
- [ ] Gemini API Key（既に設定済み）

**確認方法**:
- LINE Developers Console: https://developers.line.biz/console/
  - チャンネルを選択
  - 「Messaging API」タブ
  - 「Channel access token」と「Channel secret」を確認

---

## 🚀 段階2-2: デプロイの実行

### ステップ1: Webサービスの作成

1. **「New +」をクリック**
   - 左上の「New +」ボタンをクリック
   - ドロップダウンから「**Web Service**」を選択

2. **リポジトリの選択**
   - 「Connect a repository」セクションで、GitHubリポジトリを検索
   - `LINEDev-template-informationDeliveryBot` を選択
   - 「Connect」をクリック

3. **サービス設定**

   以下の値を設定してください：

   | 項目 | 値 | 説明 |
   |------|-----|------|
   | **Name** | `information-delivery-bot-webhook` | サービス名（任意、識別用） |
   | **Region** | `Oregon (US West)` または `Tokyo (Asia Pacific)` | 地域（近い地域を選択） |
   | **Branch** | `main` | デプロイするブランチ |
   | **Root Directory** | （空欄のまま） | プロジェクトルートディレクトリ |
   | **Runtime** | `Python 3` | Python環境を選択 |
   | **Build Command** | `pip install -r requirements.txt` | 依存関係のインストール |
   | **Start Command** | `gunicorn --bind 0.0.0.0:$PORT src.webhook_server:app` | サーバー起動コマンド |
   | **Plan** | `Free` | 無料プランを選択 |

4. **環境変数の設定**

   「Environment Variables」セクションで以下を追加：

   **必須環境変数**:

   ```
   LINE_CHANNEL_ACCESS_TOKEN = (LINE Developers Consoleから取得したトークン)
   LINE_CHANNEL_SECRET = (LINE Developers Consoleから取得したシークレット)
   ```

   **オプション環境変数**（メール収集・要約機能を使用する場合）:

   ```
   GMAIL_ACCOUNT = infobot.delivery@gmail.com
   GMAIL_APP_PASSWORD = (設定済みのアプリパスワード)
   GEMINI_API_KEY = (設定済みのAPIキー)
   ```

   **自動設定される環境変数**:
   - `PORT` - Render.comが自動的に設定（手動設定不要）

5. **「Create Web Service」をクリック**

   ⚠️ **重要**: 環境変数を設定してから「Create Web Service」をクリックしてください。

---

### ステップ2: デプロイの確認

1. **ビルドログの確認**
   - デプロイが開始されると、ビルドログが表示されます
   - ログで以下を確認：
     - ✅ `pip install -r requirements.txt` が正常に実行される
     - ✅ エラーメッセージがない

2. **デプロイ完了の確認**
   - ビルドが完了すると、「Live」ステータスが表示されます
   - 通常2-5分かかります

3. **サービスURLの確認**
   - デプロイ完了後、上部に表示されるURLをメモ
   - 例: `https://information-delivery-bot-webhook.onrender.com`
   - このURLがWebhook URLになります

---

### ステップ3: ヘルスチェックの確認

1. **ブラウザで確認**
   - サービスURL + `/health` にアクセス
   - 例: `https://information-delivery-bot-webhook.onrender.com/health`
   - 「OK」と表示されれば成功

2. **コマンドラインで確認**（オプション）
   ```bash
   curl https://your-service-url.onrender.com/health
   ```
   - 期待される結果: `OK`

3. **確認**
   - ✅ `/health` エンドポイントが `OK` を返す
   - ✅ エラーログがない（Render.comの「Logs」タブで確認）

---

## 🔗 段階2-3: LINE Developers設定

### ステップ1: Webhook URLの設定

1. **LINE Developers Consoleにアクセス**
   - URL: https://developers.line.biz/console/
   - ログイン

2. **チャンネルの選択**
   - プロバイダーを選択
   - Webhookサーバーをデプロイするチャンネルを選択

3. **Webhook設定ページへ移動**
   - 左メニューから「**Messaging API**」をクリック
   - 「**Webhook settings**」セクションまでスクロール

4. **Webhook URLの入力**
   - 「**Webhook URL**」フィールドに以下を入力：
     ```
     https://your-service-url.onrender.com/webhook
     ```
   - `your-service-url` を実際のサービスURLに置き換え
   - 例: `https://information-delivery-bot-webhook.onrender.com/webhook`

5. **検証**
   - 「**Verify**」ボタンをクリック
   - 緑のチェックマーク（✓）が表示されれば成功
   - エラーの場合、サービスURLが正しいか、サービスが起動しているか確認

---

### ステップ2: Webhookの有効化

1. **「Use webhook」を有効化**
   - 「**Use webhook**」トグルを **ON** にする

2. **「Auto-reply messages」の設定**
   - 「**Auto-reply messages**」は **OFF** にする（推奨）
   - Botの応答をWebhookサーバーで制御するため

3. **確認**
   - ✅ Webhook URLが検証済み（緑のチェックマーク）
   - ✅ 「Use webhook」がON
   - ✅ 「Auto-reply messages」がOFF（必要に応じて）

---

### ステップ3: Webhookイベントの確認

1. **Webhookイベントの設定**
   - 左メニューから「**Messaging API**」→「**Webhook settings**」
   - 「**Webhook event**」セクションを確認
   - 必要なイベントが有効になっていることを確認：
     - ✅ `message` - メッセージイベント
     - ✅ `follow` - 友達追加イベント
     - ✅ `unfollow` - 友達削除イベント

---

## 🧪 段階2-4: 本番環境でのテスト

### ステップ1: 基本的な動作確認

1. **LINEアプリでBotを友達追加**
   - LINEアプリを開く
   - BotのQRコードをスキャン（またはLINE IDで検索）
   - 友達追加

2. **テストメッセージの送信**
   - Botに何かメッセージを送信
   - 例: `テスト` または `help`

3. **応答の確認**
   - Botから応答があることを確認
   - 応答がない場合、Render.comのログを確認

---

### ステップ2: ユーザー登録のテスト

1. **「登録」コマンドを送信**
   ```
   登録
   ```

2. **期待される応答**
   ```
   登録が完了しました！

   利用可能なコマンド:
   - 購読 [カテゴリ名] - カテゴリを購読
   - 購読解除 [カテゴリ名] - 購読を解除
   - 購読一覧 - 現在の購読状況を表示
   - サイト一覧 - 利用可能なサイト一覧を表示
   ```

3. **確認**
   - ✅ 登録完了メッセージが表示される
   - ✅ Render.comのログにエラーがない

---

### ステップ3: 購読機能のテスト

1. **「購読 AI」コマンドを送信**
   ```
   購読 AI
   ```

2. **期待される応答**
   ```
   AIカテゴリを購読しました。
   ```

3. **購読一覧の確認**
   ```
   購読一覧
   ```
   - AIカテゴリが表示されることを確認

---

### ステップ4: サイト一覧のテスト

1. **「サイト一覧」コマンドを送信**
   ```
   サイト一覧
   ```

2. **期待される応答**
   ```
   利用可能なサイト:

   1. AI Weekly
      URL: https://aiweekly.co/
      カテゴリ: AI
      有効: はい
   ```

3. **確認**
   - ✅ サイト一覧が正しく表示される
   - ✅ AI Weeklyが表示される

---

### ステップ5: エラーケースのテスト

1. **未登録ユーザーのテスト**（別のLINEアカウントで）
   - 未登録の状態で「購読 AI」を送信
   - エラーメッセージが表示されることを確認

2. **不正なコマンドのテスト**
   - 不明なコマンドを送信
   - 適切なエラーメッセージが表示されることを確認

---

### ステップ6: ログの確認

1. **Render.comでログを確認**
   - Render.comダッシュボード → サービスを選択
   - 「**Logs**」タブをクリック
   - エラーログがないことを確認

2. **確認項目**
   - ✅ Webhook受信ログが表示される
   - ✅ エラーログがない
   - ✅ 正常に処理されているログが表示される

---

## ✅ 完了チェックリスト

- [ ] Render.comアカウントが作成された
- [ ] Webサービスが作成され、デプロイが完了した
- [ ] `/health` エンドポイントが `OK` を返す
- [ ] LINE Developers ConsoleでWebhook URLが設定された
- [ ] Webhook URLが検証された（緑のチェックマーク）
- [ ] 「Use webhook」が有効になっている
- [ ] ユーザー登録が動作する
- [ ] 購読機能が動作する
- [ ] サイト一覧が表示される
- [ ] エラーログがない

---

## 📝 メモ

**サービスURL**: `_________________________________`

**デプロイ日時**: `_________________________________`

**備考**: 
_______________________________________________________________________________

---

**最終更新**: 2025-01-18

