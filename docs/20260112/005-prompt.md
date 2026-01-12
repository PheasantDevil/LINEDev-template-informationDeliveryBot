## プロンプト

確認事項に回答します。

No1：メール配信している情報配信サービスであれば LINE と連携しやすいメールアドレスが好ましい。またどのアドレスで定期購読したかは`data/sites.json`の他の情報と合わせて管理か好ましい。もし検討結果 Gmail を使用することになったらその旨と「アドレスプラスでのエイリアス機能」を採用して複数サイトへ対応できるよう考慮したい。

No2：メールの要約とコスト面を考慮してどの AI API を使うべきか提案してください（No1 が Google の場合 Gemini と仮定しているがそれ以外により良い組み合わせがあれば採用したい）

NO3：わかりません。AI Weekly はあくまで一例です。収集・配信実行スクリプト内の調査時にメール以外での取得方法が採用されるかもしれませんね。

---

## Answer

回答内容を踏まえ、メールアドレス選定と AI API 比較の提案を行います。

## 1. メールアドレス選定と Gmail プラスエイリアス機能

### 1.1 Gmail プラスエイリアス機能の採用

**推奨: Gmail + プラスエイリアス機能**

**理由:**

- ✅ **LINE 連携**: Gmail は LINE と連携しやすい
- ✅ **管理の簡素化**: 1 つのアカウントで複数サイトに対応
- ✅ **フィルタリング**: エイリアスごとに自動フィルタリング可能
- ✅ **無料**: Gmail は無料で利用可能
- ✅ **信頼性**: Google のインフラで高い可用性

**Gmail プラスエイリアスの仕組み:**

```
基本アドレス: info.delivery.bot@gmail.com
エイリアス例:
- info.delivery.bot+aiweekly@gmail.com
- info.delivery.bot+drone@gmail.com
- info.delivery.bot+sdgs@gmail.com
```

**メリット:**

- 1 つの Gmail アカウントで複数サイトのメールを受信可能
- エイリアスごとにメールを識別・管理可能
- サイトごとに異なるエイリアスを使用して購読

### 1.2 データ構造の設計

**`data/sites.json`に追加:**

```json
{
  "id": "ai_weekly",
  "name": "AI Weekly",
  "category": "AI",
  "collector_type": "email",
  "collector_config": {
    "email_account_id": "gmail_account_001",
    "subscription_email": "information.bot+aiweekly@gmail.com",
    "sender_email": "newsletter@aiweekly.co",
    "subject_pattern": "AI News Weekly",
    "check_interval_minutes": 15
  }
}
```

**`data/email_accounts.json`（新規作成）:**

```json
{
  "accounts": [
    {
      "id": "gmail_account_001",
      "email": "info.delivery.bot@gmail.com",
      "imap_server": "imap.gmail.com",
      "imap_port": 993,
      "username": "information.bot@gmail.com",
      "password": "app_password_here",
      "provider": "gmail",
      "plus_alias_enabled": true,
      "enabled": true
    }
  ]
}
```

### 1.3 実装時の考慮事項

**Gmail アプリパスワードの設定:**

1. Google アカウント設定 > セキュリティ
2. 2 段階認証を有効化
3. アプリパスワードを生成
4. 生成されたパスワードを`email_accounts.json`に保存

**エイリアスでのフィルタリング:**

- IMAP 検索で`TO`フィールドを指定
- エイリアスごとにメールを分離
- サイトごとに異なるエイリアスで購読

---

## 2. AI API 比較と推奨案

### 2.1 AI API 比較表

| API                        | 無料枠   | 要約品質   | コスト（要約 1 件） | 日本語対応 | 推奨度     |
| -------------------------- | -------- | ---------- | ------------------- | ---------- | ---------- |
| **Gemini (Google)**        | 60 回/分 | ⭐⭐⭐⭐   | $0.000125/1K tokens | 優秀       | ⭐⭐⭐⭐⭐ |
| **Claude (Anthropic)**     | 制限あり | ⭐⭐⭐⭐⭐ | $0.003/1K tokens    | 優秀       | ⭐⭐⭐⭐   |
| **GPT-4o-mini (OpenAI)**   | 制限あり | ⭐⭐⭐⭐   | $0.00015/1K tokens  | 優秀       | ⭐⭐⭐⭐   |
| **GPT-3.5-turbo (OpenAI)** | 制限あり | ⭐⭐⭐     | $0.0005/1K tokens   | 良好       | ⭐⭐⭐     |

### 2.2 詳細比較

#### Gemini (Google) ⭐ 推奨

**無料枠:**

- 60 リクエスト/分
- 1 日あたり 1,500 リクエスト
- 月間 15,000 リクエスト

**コスト（有料時）:**

- Gemini 1.5 Flash: $0.000125/1K input tokens
- Gemini 1.5 Pro: $0.000625/1K input tokens

**メリット:**

- ✅ **Gmail との統合**: 同じ Google アカウントで管理可能
- ✅ **無料枠が充実**: 60 回/分は十分
- ✅ **コストが低い**: 要約 1 件あたり約$0.001-0.002
- ✅ **日本語対応**: 優秀
- ✅ **要約品質**: 高品質

**デメリット:**

- ❌ API キーの取得が必要

#### Claude (Anthropic)

**無料枠:**

- 制限あり（詳細は要確認）

**コスト:**

- Claude 3 Haiku: $0.003/1K input tokens
- Claude 3 Sonnet: $0.015/1K input tokens

**メリット:**

- ✅ **要約品質**: 最高クラス
- ✅ **日本語対応**: 優秀

**デメリット:**

- ❌ コストが高い（Gemini の約 24 倍）
- ❌ Gmail との統合性が低い

#### GPT-4o-mini (OpenAI)

**無料枠:**

- 制限あり（詳細は要確認）

**コスト:**

- GPT-4o-mini: $0.00015/1K input tokens

**メリット:**

- ✅ **コストが低い**: Gemini と同等
- ✅ **日本語対応**: 優秀

**デメリット:**

- ❌ Gmail との統合性が低い
- ❌ 無料枠が限定的

### 2.3 推奨案: Gmail + Gemini

**推奨理由:**

1. **統合性**: Gmail と Gemini は同じ Google アカウントで管理可能
2. **コスト**: 無料枠が充実（60 回/分）
3. **品質**: 要約品質が高い
4. **日本語対応**: 優秀
5. **運用**: 1 つのアカウントで完結

**実装例:**

```python
# requirements.txtに追加
google-generativeai>=0.3.0

# 使用例
import google.generativeai as genai

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

response = model.generate_content(
    f"以下のメール内容を3-5行で要約してください:\n\n{email_body}"
)
summary = response.text
```

**コスト試算（月間 100 件のメール要約）:**

- 1 メールあたり平均 500 tokens と仮定
- 100 件 × 500 tokens = 50,000 tokens
- コスト: 50,000 / 1,000 × $0.000125 = **$0.00625/月**
- 無料枠内で十分対応可能

---

## 3. 実装方針の確定

### 3.1 メール方式の実装

**実装内容:**

1. **Gmail アカウント設定**

   - 専用 Gmail アカウントを作成
   - アプリパスワードを生成
   - `data/email_accounts.json`に設定

2. **プラスエイリアス機能の実装**

   - サイトごとに異なるエイリアスを使用
   - `data/sites.json`でエイリアスを管理
   - IMAP 検索でエイリアスごとにフィルタリング

3. **メール受信機能**

   - IMAP 接続
   - 新着メールの検出
   - メール ID ベースの重複排除

4. **情報抽出機能**

   - メール本文から HTML をパース
   - リンクを抽出
   - タイトルを抽出

5. **AI 要約機能（Gemini）**

   - Gemini API を使用
   - メール本文を要約
   - 3-5 行程度の簡潔な要約

6. **LINE 通知機能**
   - 要約とリンクを LINE で配信

### 3.2 データ構造の更新

**`data/sites.json`の例:**

```json
{
  "sites": [
    {
      "id": "ai_weekly",
      "name": "AI Weekly",
      "url": "https://aiweekly.co/",
      "category": "AI",
      "collector_type": "email",
      "collector_config": {
        "email_account_id": "gmail_account_001",
        "subscription_email": "info.delivery.bot+aiweekly@gmail.com",
        "sender_email": "newsletter@aiweekly.co",
        "subject_pattern": "AI News Weekly|Issue #",
        "check_interval_minutes": 15,
        "summary_enabled": true,
        "summary_model": "gemini-1.5-flash"
      },
      "enabled": true,
      "created_at": "2025-01-12T00:00:00",
      "last_collected_at": null
    }
  ]
}
```

### 3.3 収集・配信実行スクリプトの拡張

**調査機能の追加:**

- サイトの情報発信方法を自動調査
- メール配信の有無を確認
- RSS フィードの有無を確認
- 最適な収集方法を提案

**実装例:**

```python
def investigate_site(url: str) -> Dict:
    """サイトの情報発信方法を調査"""
    # メール配信の有無を確認
    # RSSフィードの有無を確認
    # 最適な収集方法を提案
    pass
```

---

## 4. 実装優先順位

### Phase 1.5: メール方式の実装（最優先）

1. **Gmail アカウント設定**

   - 専用アカウント作成
   - アプリパスワード生成
   - `email_accounts.json`の作成

2. **メール受信機能**（`src/collectors/email_collector.py`）

   - IMAP 接続
   - プラスエイリアス対応
   - 新着メール検出
   - 重複排除

3. **情報抽出機能**

   - メール本文パース
   - リンク抽出
   - タイトル抽出

4. **AI 要約機能（Gemini）**

   - Gemini API 連携
   - 要約生成
   - エラーハンドリング

5. **LINE 通知機能**
   - 要約とリンクの配信

### Phase 2: 調査機能の追加

6. **サイト調査機能**
   - メール配信の有無を確認
   - RSS フィードの有無を確認
   - 最適な収集方法の提案

---

## 5. 必要な環境変数

**`.env`に追加:**

```bash
# Gmail設定
GMAIL_ACCOUNT=information.bot@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here

# Gemini API設定
GEMINI_API_KEY=your_gemini_api_key_here
```

**GitHub Secrets に追加:**

- `GMAIL_ACCOUNT`
- `GMAIL_APP_PASSWORD`
- `GEMINI_API_KEY`

---

## 6. 次のステップ

1. **Gmail アカウントの作成**

   - 専用アカウントを作成
   - アプリパスワードを生成

2. **Gemini API キーの取得**

   - Google AI Studio (https://aistudio.google.com/) で取得

3. **メール方式の実装開始**

   - `src/collectors/email_collector.py`の実装
   - プラスエイリアス機能の実装

4. **テスト**
   - AI Weekly にエイリアスアドレスで購読
   - メール受信・要約・LINE 通知のテスト

---

**作成日時：** 2025-01-12T23:05:46
