# Webhook サーバーデプロイ実作業手順

このドキュメントは、Render.com への Webhook サーバーデプロイを段階ごとに具体的に進める手順です。

---

## 🎯 段階 2-1: Render.com でのデプロイ準備

### ステップ 1: Render.com アカウントの作成

1. **ブラウザで Render.com にアクセス**

   - URL: https://render.com
   - または: https://dashboard.render.com

2. **アカウント作成**

   - 「Get Started for Free」または「Sign Up」をクリック
   - **GitHub アカウントでサインアップ**を選択（推奨）
     - 「Continue with GitHub」をクリック
     - GitHub の認証画面で承認
   - またはメールアドレスでサインアップも可能

3. **確認**
   - ✅ Render.com ダッシュボードが表示される
   - ✅ 右上にアカウント名が表示される

**⚠️ 注意**: 無料プランで十分です。有料プランへのアップグレードは不要です。

---

### ステップ 2: GitHub リポジトリの連携確認

1. **GitHub 連携の確認**

   - 既に GitHub アカウントでサインアップした場合、自動的に連携されています
   - 左上の「Dashboard」をクリック

2. **リポジトリの確認**
   - Render.com から GitHub リポジトリにアクセスできることを確認
   - リポジトリが表示されない場合は、GitHub の認証を再確認

---

### ステップ 3: Web サービスの作成（準備）

次のステップで実際に Web サービスを作成しますが、その前に以下を確認してください：

**必要な情報**:

- [ ] LINE Channel Access Token（LINE Developers Console から取得）
- [ ] LINE Channel Secret（LINE Developers Console から取得）
- [ ] Gmail アカウント（既に設定済み）
- [ ] Gmail App Password（既に設定済み）
- [ ] Gemini API Key（既に設定済み）

**確認方法**:

- LINE Developers Console: https://developers.line.biz/console/
  - チャンネルを選択
  - 「Messaging API」タブ
  - 「Channel access token」と「Channel secret」を確認

---

## 🚀 段階 2-2: デプロイの実行

### ステップ 1: Web サービスの作成

1. **「New +」をクリック**

   - 左上の「New +」ボタンをクリック
   - ドロップダウンから「**Web Service**」を選択

2. **リポジトリの選択**

   - 「Connect a repository」セクションで、GitHub リポジトリを検索
   - `LINEDev-template-informationDeliveryBot` を選択
   - 「Connect」をクリック

3. **サービス設定**

   以下の値を設定してください：

   | 項目               | 値                                                     | 説明                           |
   | ------------------ | ------------------------------------------------------ | ------------------------------ |
   | **Name**           | `information-delivery-bot-webhook`                     | サービス名（任意、識別用）     |
   | **Region**         | `Oregon (US West)` または `Tokyo (Asia Pacific)`       | 地域（近い地域を選択）         |
   | **Branch**         | `main`                                                 | デプロイするブランチ           |
   | **Root Directory** | （空欄のまま）                                         | プロジェクトルートディレクトリ |
   | **Runtime**        | `Python 3`                                             | Python 環境を選択              |
   | **Build Command**  | `pip install -r requirements.txt`                      | 依存関係のインストール         |
   | **Start Command**  | `gunicorn --bind 0.0.0.0:$PORT src.webhook_server:app` | サーバー起動コマンド           |
   | **Plan**           | `Free`                                                 | 無料プランを選択               |

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

   - `PORT` - Render.com が自動的に設定（手動設定不要）

5. **「Create Web Service」をクリック**

   ⚠️ **重要**: 環境変数を設定してから「Create Web Service」をクリックしてください。

---

### ステップ 2: デプロイの確認

1. **ビルドログの確認**

   - デプロイが開始されると、ビルドログが表示されます
   - ログで以下を確認：
     - ✅ `pip install -r requirements.txt` が正常に実行される
     - ✅ エラーメッセージがない

2. **デプロイ完了の確認**

   - ビルドが完了すると、「Live」ステータスが表示されます
   - 通常 2-5 分かかります

3. **サービス URL の確認**
   - デプロイ完了後、上部に表示される URL をメモ
   - 例: `https://information-delivery-bot-webhook.onrender.com`
   - この URL が Webhook URL になります

---

### ステップ 3: ヘルスチェックの確認

1. **ブラウザで確認**

   - サービス URL + `/health` にアクセス
   - 例: `https://information-delivery-bot-webhook.onrender.com/health`
   - 「OK」と表示されれば成功

2. **コマンドラインで確認**（オプション）

   ```bash
   curl https://your-service-url.onrender.com/health
   ```

   - 期待される結果: `OK`

3. **確認**
   - ✅ `/health` エンドポイントが `OK` を返す
   - ✅ エラーログがない（Render.com の「Logs」タブで確認）

---

## 🔗 段階 2-3: LINE Developers 設定

### ステップ 1: Webhook URL の設定

1. **LINE Developers Console にアクセス**

   - URL: https://developers.line.biz/console/
   - ログイン

2. **チャンネルの選択**

   - プロバイダーを選択
   - Webhook サーバーをデプロイするチャンネルを選択

3. **Webhook 設定ページへ移動**

   - 左メニューから「**Messaging API**」をクリック
   - 「**Webhook settings**」セクションまでスクロール

4. **Webhook URL の入力**

   - 「**Webhook URL**」フィールドに以下を入力：
     ```
     https://your-service-url.onrender.com/webhook
     ```
   - `your-service-url` を実際のサービス URL に置き換え
   - 例: `https://information-delivery-bot-webhook.onrender.com/webhook`

5. **検証**
   - 「**Verify**」ボタンをクリック
   - 緑のチェックマーク（✓）が表示されれば成功
   - エラーの場合、サービス URL が正しいか、サービスが起動しているか確認

---

### ステップ 2: Webhook の有効化

1. **「Use webhook」を有効化**

   - 「**Use webhook**」トグルを **ON** にする

2. **「Auto-reply messages」の設定**

   - 「**Auto-reply messages**」は **OFF** にする（推奨）
   - Bot の応答を Webhook サーバーで制御するため

3. **確認**
   - ✅ Webhook URL が検証済み（緑のチェックマーク）
   - ✅ 「Use webhook」が ON
   - ✅ 「Auto-reply messages」が OFF（必要に応じて）

---

### ステップ 3: Webhook イベントの確認

1. **Webhook イベントの設定**
   - 左メニューから「**Messaging API**」→「**Webhook settings**」
   - 「**Webhook event**」セクションを確認
   - 必要なイベントが有効になっていることを確認：
     - ✅ `message` - メッセージイベント
     - ✅ `follow` - 友達追加イベント
     - ✅ `unfollow` - 友達削除イベント

---

## 🧪 段階 2-4: 本番環境でのテスト

### ステップ 1: 基本的な動作確認

1. **LINE アプリで Bot を友達追加**

   - LINE アプリを開く
   - Bot の QR コードをスキャン（または LINE ID で検索）
   - 友達追加

2. **テストメッセージの送信**

   - Bot に何かメッセージを送信
   - 例: `テスト` または `help`

3. **応答の確認**
   - Bot から応答があることを確認
   - 応答がない場合、Render.com のログを確認

---

### ステップ 2: ユーザー登録のテスト

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
   - ✅ Render.com のログにエラーがない

---

### ステップ 3: 購読機能のテスト

1. **「購読 AI」コマンドを送信**

   ```
   購読 AI
   ```

   **注意**: 半角スペース ` ` または全角スペース `　` のどちらでも動作します。

2. **期待される応答**

   ```
   AIカテゴリを購読しました。
   ```

3. **購読一覧の確認**
   ```
   購読一覧
   ```
   - AI カテゴリが表示されることを確認

---

### ステップ 4: サイト一覧のテスト

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
   - ✅ AI Weekly が表示される

---

### ステップ 5: エラーケースのテスト

1. **未登録ユーザーのテスト**（別の LINE アカウントで）

   - 未登録の状態で「購読 AI」を送信
   - エラーメッセージが表示されることを確認

2. **不正なコマンドのテスト**
   - 不明なコマンドを送信
   - 適切なエラーメッセージが表示されることを確認

---

### ステップ 6: ログの確認

1. **Render.com でログを確認**

   - Render.com ダッシュボード → サービスを選択
   - 「**Logs**」タブをクリック
   - エラーログがないことを確認

2. **確認項目**
   - ✅ Webhook 受信ログが表示される
   - ✅ エラーログがない
   - ✅ 正常に処理されているログが表示される

---

## ✅ 完了チェックリスト

- [ ] Render.com アカウントが作成された
- [ ] Web サービスが作成され、デプロイが完了した
- [ ] `/health` エンドポイントが `OK` を返す
- [ ] LINE Developers Console で Webhook URL が設定された
- [ ] Webhook URL が検証された（緑のチェックマーク）
- [ ] 「Use webhook」が有効になっている
- [ ] ユーザー登録が動作する
- [ ] 購読機能が動作する
- [ ] サイト一覧が表示される
- [ ] エラーログがない

---

## 📝 メモ

**サービス URL**: `_________________________________`

**デプロイ日時**: `_________________________________`

**備考**:

---

---

**最終更新**: 2025-01-18
