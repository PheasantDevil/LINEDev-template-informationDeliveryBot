# Webhook検証エラー対応ガイド

## 🔴 エラー: 500 Internal Server Error

Webhook URL検証時に `500 Internal Server Error` が発生する場合の対応方法です。

---

## 📋 エラー原因の確認手順

### ステップ1: Render.comログの確認

1. **Render.comダッシュボードにアクセス**
   - https://dashboard.render.com
   - デプロイしたWebサービスを選択

2. **「Logs」タブを開く**
   - 左メニューから「**Logs**」をクリック
   - 最新のログを確認

3. **エラーメッセージを確認**
   - エラートレースバックを探す
   - 特に以下のメッセージに注目：
     - `LINE_CHANNEL_ACCESS_TOKEN が設定されていません`
     - `Signature verification failed`
     - `Webhook error`
     - `ValueError`
     - `AttributeError`

---

## 🔧 よくある原因と対処法

### 原因1: 環境変数が設定されていない

**エラーメッセージ例**:
```
ValueError: LINE_CHANNEL_ACCESS_TOKEN が設定されていません
```

**対処法**:

1. **Render.comダッシュボードで環境変数を確認**
   - サービスを選択 → 「**Environment**」タブ
   - 以下の環境変数が設定されているか確認：
     - `LINE_CHANNEL_ACCESS_TOKEN`
     - `LINE_CHANNEL_SECRET`

2. **環境変数を追加・更新**
   - 「**Environment Variables**」セクションで追加
   - LINE Developers Consoleから値をコピー：
     - https://developers.line.biz/console/
     - チャンネルを選択 → 「Messaging API」タブ
     - 「Channel access token」と「Channel secret」をコピー

3. **サービスを再デプロイ**
   - 環境変数を変更したら、自動的に再デプロイされる
   - または「**Manual Deploy**」→「**Deploy latest commit**」をクリック

---

### 原因2: 署名検証エラー

**エラーメッセージ例**:
```
❌ Signature verification failed
```

**対処法**:

1. **LINE_CHANNEL_SECRETが正しく設定されているか確認**
   - 環境変数に`LINE_CHANNEL_SECRET`が設定されているか
   - 値が正しいか（LINE Developers Consoleと一致しているか）

2. **一時的に署名検証をスキップしてテスト**（デバッグ用）
   - ⚠️ **本番環境では推奨しません**
   - `src/webhook_server.py`の署名検証部分をコメントアウト
   - ただし、セキュリティ上の理由から、問題解決後は必ず元に戻す

---

### 原因3: リクエストボディのパースエラー

**エラーメッセージ例**:
```
JSON decode error
KeyError: 'events'
```

**対処法**:

1. **LINE Developers Consoleでの検証リクエストを確認**
   - LINE Developers Consoleの検証リクエストは空のJSON `{}` を送信する可能性がある
   - `webhook_server.py`の`events`取得部分でエラーが発生している

2. **空のリクエストボディの処理を確認**
   - 現在のコードは空のリクエストを適切に処理できているか確認

---

### 原因4: モジュールインポートエラー

**エラーメッセージ例**:
```
ModuleNotFoundError: No module named 'xxx'
ImportError: cannot import name 'xxx'
```

**対処法**:

1. **requirements.txtの確認**
   - すべての依存関係が含まれているか確認

2. **ビルドログの確認**
   - Render.comのビルドログで、依存関係のインストールが正常に完了しているか確認

---

## 🔍 デバッグ手順

### ステップ1: ログの詳細確認

Render.comのログで以下を確認：

```
Webhook received
Body length: XXX bytes
Signature: ...
✓ LineNotifier initialized successfully
```

上記のログが表示されているか確認します。

### ステップ2: 手動でWebhookエンドポイントをテスト

**curlコマンドでテスト**（ローカル環境またはターミナルから）:

```bash
curl -X POST https://your-service-url.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-Line-Signature: test" \
  -d '{"events":[]}'
```

**期待される結果**: 
- ステータスコード: `200 OK`
- レスポンス: `OK`

**エラーが出る場合**:
- エラーメッセージを確認
- Render.comのログで詳細を確認

---

## ✅ 確認チェックリスト

Webhook検証エラーが発生した場合、以下を確認してください：

- [ ] `LINE_CHANNEL_ACCESS_TOKEN`環境変数が設定されている
- [ ] `LINE_CHANNEL_SECRET`環境変数が設定されている
- [ ] 環境変数の値が正しい（LINE Developers Consoleと一致）
- [ ] サービスが再デプロイされている（環境変数変更後）
- [ ] Render.comのログで具体的なエラーメッセージを確認
- [ ] `/health`エンドポイントは正常に動作している
- [ ] ビルドログにエラーがない

---

## 📝 次のステップ

1. **Render.comのログを確認**
   - 具体的なエラーメッセージを特定

2. **エラー内容に応じて対処**
   - 上記の「よくある原因と対処法」を参照

3. **再度検証**
   - LINE Developers Consoleで「Verify」ボタンを再度クリック

4. **まだエラーが出る場合**
   - ログのエラーメッセージを共有してください
   - より具体的な対処法を提案します

---

**最終更新**: 2025-01-18

