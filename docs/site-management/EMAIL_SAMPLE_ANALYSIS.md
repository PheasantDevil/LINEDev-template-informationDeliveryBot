# AI News Weekly メールサンプル分析

## 📧 メールサンプル情報

**ファイル**: `data/samples/mail/Gmail - AI News Weekly - Issue #459_ Is Elon Musk the worst in Tech_.pdf`

**件名パターン**: `AI News Weekly - Issue #459_ Is Elon Musk the worst in Tech`

**発信元**: AI News Weekly (newsletter@aiweekly.co / hello@aiweekly.co)

---

## 🔍 EmailCollectorでの処理分析

### 1. 件名マッチング

**現在の設定**:
```json
{
  "subject_pattern": "AI News Weekly|Issue #"
}
```

**メール件名**: `AI News Weekly - Issue #459_ Is Elon Musk the worst in Tech`

**マッチング結果**: ✅ 成功
- `AI News Weekly` が含まれている
- `Issue #` も含まれている
- 両方のパターンにマッチする

### 2. タイトル抽出

**EmailCollectorの処理**:
```python
title = subject or self._extract_title_from_body(body) or "メール通知"
```

**抽出されるタイトル**:
- 件名から直接: `AI News Weekly - Issue #459_ Is Elon Musk the worst in Tech`
- または本文から抽出したタイトル

### 3. リンク抽出

**EmailCollectorの処理**:
```python
links = self._extract_links(body)
main_link = links[0] if links else site_config.get("url", "")
```

**期待される動作**:
- HTML本文から`<a href="...">`タグを抽出
- 最初のリンクをメインリンクとして使用
- リンクがない場合はサイトURLを使用

### 4. AI要約生成

**現在の設定**:
```json
{
  "summary_enabled": true,
  "summary_model": "gemini-1.5-flash"
}
```

**EmailCollectorの処理**:
- メール本文（HTML）をBeautifulSoupでパース
- HTMLタグを除去してテキスト抽出
- 10,000文字を超える場合は切り詰め
- Gemini APIで3-5行の要約を生成

---

## ✅ 設定確認

### AI Weekly サイト設定

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
    "check_interval_minutes": 60,
    "summary_enabled": true,
    "summary_model": "gemini-1.5-flash"
  },
  "enabled": true
}
```

### メールアカウント設定

```json
{
  "id": "gmail_account_001",
  "email": "infobot.delivery@gmail.com",
  "imap_server": "imap.gmail.com",
  "imap_port": 993,
  "username": "infobot.delivery@gmail.com",
  "password": "WFG4od-8",
  "provider": "gmail",
  "plus_alias_enabled": true,
  "enabled": true
}
```

---

## 🎯 EmailCollectorの動作確認ポイント

### 1. メール受信
- [ ] IMAP接続が成功する
- [ ] `infobot.delivery+aiweekly@gmail.com`宛のメールを検索できる
- [ ] `sender_email: newsletter@aiweekly.co`でフィルタリングできる

### 2. 件名マッチング
- [ ] `subject_pattern`にマッチするメールを抽出できる
- [ ] マッチしないメールは除外される

### 3. 情報抽出
- [ ] タイトルが正しく抽出される
- [ ] リンクが正しく抽出される
- [ ] 公開日時が正しく抽出される

### 4. AI要約生成
- [ ] メール本文が正しくテキスト化される
- [ ] Gemini APIで要約が生成される
- [ ] 要約が3-5行で生成される

### 5. InformationItem生成
- [ ] `InformationItem`が正しく生成される
- [ ] `content_hash`が正しく生成される
- [ ] 重複排除が機能する

---

## 📝 注意事項

1. **実際のメール購読が必要**
   - `infobot.delivery+aiweekly@gmail.com`でAI Weeklyを購読している必要がある
   - メールが届いていない場合、情報収集は空の結果になる

2. **環境変数の設定**
   - `GMAIL_ACCOUNT`: 設定済み
   - `GMAIL_APP_PASSWORD`: 設定済み
   - `GEMINI_API_KEY`: 設定済み（要約を使用する場合）

3. **件名パターンの柔軟性**
   - 現在のパターン `"AI News Weekly|Issue #"` はOR条件
   - `AI News Weekly` または `Issue #` のいずれかが含まれていればマッチ
   - Issue番号が変わる可能性を考慮して柔軟なパターンを使用

---

## 🔄 テスト実行時の確認事項

1. **メール受信の確認**
   ```bash
   python src/collect_and_deliver.py
   # ログで「メールを受信しました: X件」を確認
   ```

2. **情報抽出の確認**
   - ログで「収集した情報: X件」を確認
   - `data/information_items.json`で抽出結果を確認

3. **重複排除の確認**
   - 同じメールを再度処理した場合、重複が除外されることを確認

4. **LINE配信の確認**（テスト環境）
   - 新着情報がある場合、LINE配信が実行されることを確認

---

**最終更新**: 2025-01-18

