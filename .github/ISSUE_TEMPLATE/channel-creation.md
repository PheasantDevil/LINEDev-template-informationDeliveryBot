# LINEチャネル作成タスク

## 📋 チャネル情報

- **チャネル名**: `{{CHANNEL_NAME}}`
- **サイトID**: `{{SITE_ID}}`
- **カテゴリ**: `{{CATEGORY}}`
- **優先度**: 🔴 高 / 🟡 中 / 🟢 低

## 🎯 作成タスク

### 1. LINE Developers Consoleでチャネルを作成

- [ ] プロバイダーを選択（既存のプロバイダーを使用）
- [ ] 「Messaging API」チャネルを作成
- [ ] チャネル名: `{{CHANNEL_NAME}}`
- [ ] チャネル説明を入力
- [ ] カテゴリを選択

### 2. チャネル情報の取得

- [ ] **Channel Access Token**を取得
  - 変数名: `LINE_CHANNEL_ACCESS_TOKEN_{{CHANNEL_ID_UPPER}}`
  - 値: `_____________________________`
  
- [ ] **Channel Secret**を取得
  - 変数名: `LINE_CHANNEL_SECRET_{{CHANNEL_ID_UPPER}}`
  - 値: `_____________________________`

### 3. GitHub Secretsに追加

- [ ] `LINE_CHANNEL_ACCESS_TOKEN_{{CHANNEL_ID_UPPER}}`を追加
- [ ] `LINE_CHANNEL_SECRET_{{CHANNEL_ID_UPPER}}`を追加

### 4. Render.com環境変数に追加（Webhookサーバー用）

- [ ] `LINE_CHANNEL_ACCESS_TOKEN_{{CHANNEL_ID_UPPER}}`を追加
- [ ] `LINE_CHANNEL_SECRET_{{CHANNEL_ID_UPPER}}`を追加

### 5. チャネル設定の登録（CLIツール）

```bash
python tools/manage_channel.py add \
  --channel-id {{CHANNEL_ID}} \
  --access-token "$LINE_CHANNEL_ACCESS_TOKEN_{{CHANNEL_ID_UPPER}}" \
  --secret "$LINE_CHANNEL_SECRET_{{CHANNEL_ID_UPPER}}" \
  --site-id {{SITE_ID}}
```

- [ ] コマンドを実行
- [ ] チャネル設定が正しく登録されたことを確認

### 6. Webhook URLの設定

- [ ] LINE Developers ConsoleでWebhook URLを設定
- [ ] Webhook URL: `https://your-service-url.onrender.com/webhook/{{CHANNEL_ID}}`
- [ ] 「Verify」ボタンで検証
- [ ] 「Use webhook」をONに設定

### 7. 動作確認

- [ ] テストメッセージを送信
- [ ] Botからの応答を確認
- [ ] 情報配信のテスト

## 📝 命名規則

### チャネルID
- 形式: `channel_{{SITE_ID}}` または `channel_{{CATEGORY}}`
- 例: `channel_ai_weekly`, `channel_ai_category`

### 環境変数名
- Channel Access Token: `LINE_CHANNEL_ACCESS_TOKEN_{{CHANNEL_ID_UPPER}}`
- Channel Secret: `LINE_CHANNEL_SECRET_{{CHANNEL_ID_UPPER}}`
- 例: `LINE_CHANNEL_ACCESS_TOKEN_CHANNEL_AI_WEEKLY`

**注意**: 環境変数名は大文字で統一、アンダースコアで区切る

## 🔗 関連情報

- サイトID: `{{SITE_ID}}`
- カテゴリ: `{{CATEGORY}}`
- 関連Issue: `{{RELATED_ISSUES}}`

---

**作成日**: {{CREATED_DATE}}
**期限**: {{DUE_DATE}}

