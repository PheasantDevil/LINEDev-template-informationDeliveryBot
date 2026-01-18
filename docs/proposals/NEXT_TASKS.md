# 次の作業内容（段階ごと）

## 📊 現在の実装状況

### ✅ 完了済み
- [x] メール受信・要約方式（EmailCollector）
- [x] RSS リーダー実装（RSSReaderCollector）
- [x] サイト設定バリデーション
- [x] CI/CDワークフロー（コード品質チェック、テスト自動実行）
- [x] 統合テスト
- [x] Webhookサーバーデプロイ設定（Render.com対応）

### ⏸️ 保留中（優先度低）
- [ ] スクレイパー実装（フェーズ1）
- [ ] サイト更新検知方式（フェーズ1）

**理由**: 現在の情報配信はSNSやメールが主流となっており、ブログへの直接アプローチは減少している。本サービスは「情報や情報サイトの配信内容の概要を定期配信するLINEグループ」という独自のアプローチを提供するため、ブログスクレイピングの優先度は低い。

---

## 🎯 次の作業タスク（優先順位順）

### 優先度 1: 実際のサイトデータ追加

**目的**: 実際の情報サイトを追加して動作確認

**実装段階**:

#### 段階 1-1: サイト調査（約1時間）
- AI、ドローン、SDGs関連の情報サイトを調査
- 各サイトの情報配信方式を確認（メール/RSS/その他）
- 適切な収集方式を決定

**作業内容**:
- サイトリストの作成
- 配信方式の確認
- 収集方式の選択

**調査対象**:
- AI関連: AI Weekly, AI Trends等
- ドローン関連: ドローン情報サイト等
- SDGs関連: SDGs関連ニュースサイト等

#### 段階 1-2: サイト設定の追加（約1時間）
- `tools/add_site.py`を使用してサイトを追加
- 各サイトの設定を最適化
- 設定の検証

**作業内容**:
```bash
# 例: AI Weeklyの追加
python tools/add_site.py \
  --id ai_weekly \
  --name "AI Weekly" \
  --url "https://aiweekly.co/" \
  --category "AI" \
  --type email \
  --enabled \
  --email-account gmail_account_001 \
  --subscription-email infobot.delivery+aiweekly@gmail.com \
  --sender-email hello@aiweekly.co \
  --summary-enabled
```

**確認項目**:
- サイト設定ファイルが正しく作成されているか
- `data/sites.json`が正しく更新されているか
- バリデーションエラーがないか

#### 段階 1-3: 動作確認（約1時間）
- 情報収集の実行
- 収集結果の確認
- LINE配信の確認
- エラーの修正

**作業内容**:
- `python src/collect_and_deliver.py`を実行
- 収集ログの確認
- LINE配信の確認（テスト環境）
- エラーの修正

**確認項目**:
- メールが正しく受信できているか
- 情報アイテムが正しく生成されているか
- 重複排除が機能しているか
- LINE配信が正常に動作しているか

---

### 優先度 2: Webhookサーバーの実際のデプロイ

**目的**: 本番環境でWebhookサーバーを稼働させる

**実装段階**:

#### 段階 2-1: Render.comでのデプロイ準備（約30分）
- Render.comアカウントの作成
- リポジトリの接続
- 環境変数の設定

**作業内容**:
1. Render.comアカウント作成
   - https://render.com にアクセス
   - GitHubアカウントでサインアップ

2. GitHubリポジトリ連携
   - Dashboard → "New +" → "Web Service"
   - GitHubリポジトリを選択

3. 環境変数の設定
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `GMAIL_ACCOUNT`（オプション）
   - `GMAIL_APP_PASSWORD`（オプション）
   - `GEMINI_API_KEY`（オプション）

#### 段階 2-2: デプロイの実行（約30分）
- `render.yaml`を使用してデプロイ
- デプロイの確認
- ヘルスチェックエンドポイントの確認

**作業内容**:
1. Webサービスの作成
   - `render.yaml`を使用してサービスを作成
   - または手動で設定
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `gunicorn --bind 0.0.0.0:$PORT src.webhook_server:app`

2. デプロイの実行
   - 初回デプロイを実行
   - ビルドログを確認

3. ヘルスチェックの確認
   ```bash
   curl https://your-service-url.onrender.com/health
   # 期待される結果: OK
   ```

#### 段階 2-3: LINE Developers設定（約30分）
- Webhook URLの設定
- 署名検証の確認
- テストメッセージの送信

**作業内容**:
1. LINE Developers Consoleでの設定
   - https://developers.line.biz/console/ にアクセス
   - チャンネルを選択
   - "Messaging API" → "Webhook settings"
   - Webhook URL: `https://your-service-url.onrender.com/webhook`
   - "Verify"ボタンで検証

2. Webhookの有効化
   - "Use webhook"をON
   - "Auto-reply messages"をOFF（必要に応じて）

3. テストメッセージの送信
   - LINEアプリでBotにメッセージを送信
   - サーバーログで受信を確認

#### 段階 2-4: 本番環境でのテスト（約1時間）
- 各コマンドの動作確認
- エラーハンドリングの確認
- ログの確認

**作業内容**:
1. ユーザー登録のテスト
   - "登録"コマンドの送信
   - 登録完了メッセージの確認

2. 購読機能のテスト
   - "購読 AI"コマンドの送信
   - 購読完了メッセージの確認

3. サイト一覧のテスト
   - "サイト一覧"コマンドの送信
   - サイトリストの表示確認

4. エラーケースのテスト
   - 未登録ユーザーの購読試行
   - 不正なコマンドの送信

5. ログの確認
   - Render.comのログ画面でエラーがないか確認
   - 配信ログの確認

---

## 📋 実装順序

### フェーズ 2: 実運用準備（今週-来週）
1. **実際のサイトデータ追加**（優先度1）- 約2-3時間
2. **Webhookサーバーのデプロイ**（優先度2）- 約2-3時間

---

## 📝 関連ドキュメント

- `docs/DEPLOYMENT_GUIDE.md` - デプロイ手順の詳細
- `docs/DEPLOYMENT_CHECKLIST.md` - デプロイチェックリスト
- `docs/SITE_ADDITION_GUIDE.md` - サイト追加ガイド
- `docs/FUTURE_ROADMAP.md` - 今後の実装構想

---

## 🎯 次のステップ

**推奨**: 優先度1（実際のサイトデータ追加）から開始

**理由**:
- 実際のサイトを追加することで、システムの動作を確認できる
- デプロイ前にローカルで動作確認ができる
- 問題を早期に発見できる

**実装開始の準備**:
1. サイト調査を行う
2. `tools/add_site.py`を使用してサイトを追加
3. ローカルで動作確認

---

**最終更新**: 2025-01-18
