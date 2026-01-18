# サイト調査結果

実際の情報サイトを追加するための調査結果をまとめます。

## 📋 調査対象カテゴリ

- **AI関連**: AI、機械学習、深層学習などの最新情報
- **ドローン関連**: ドローン技術、法規制、活用事例など
- **SDGs関連**: 持続可能な開発目標に関する情報

---

## 🔍 調査結果

### AI関連サイト

#### 1. AI Weekly
- **URL**: https://aiweekly.co/
- **配信方式**: メール配信（週刊）
- **メール送信元**: newsletter@aiweekly.co / hello@aiweekly.co
- **配信頻度**: 週1回
- **内容**: AI関連の最新ニュース、論文、ツールなどのキュレーション
- **収集方式**: `email`
- **推奨設定**:
  - `subscription_email`: `infobot.delivery+aiweekly@gmail.com`
  - `sender_email`: `hello@aiweekly.co` または `newsletter@aiweekly.co`
  - `subject_pattern`: `AI News Weekly|Issue #`
  - `summary_enabled`: `true`

#### 2. AI Trends (候補)
- **URL**: https://www.aitrends.com/
- **配信方式**: RSS / メール（要確認）
- **収集方式**: `rss` または `email`（要確認）

#### 3. The Batch by deeplearning.ai (候補)
- **URL**: https://www.deeplearning.ai/the-batch/
- **配信方式**: メール配信（週刊）
- **内容**: 深層学習の最新動向
- **収集方式**: `email`

---

### ドローン関連サイト

#### 1. ドローン情報サイト（要調査）
- **URL**: 要調査
- **配信方式**: RSS / メール（要確認）
- **収集方式**: `rss` または `email`（要確認）

#### 2. DroneLife (候補)
- **URL**: https://dronelife.com/
- **配信方式**: RSS / メール（要確認）
- **内容**: ドローン業界のニュース
- **収集方式**: `rss`（要確認）

---

### SDGs関連サイト

#### 1. SDGs関連ニュースサイト（要調査）
- **URL**: 要調査
- **配信方式**: RSS / メール（要確認）
- **収集方式**: `rss` または `email`（要確認）

---

## ✅ 追加予定サイト（確定）

### 優先度: 高

1. **AI Weekly** (既に設定あり)
   - 既に `data/sites/ai_weekly.json` が存在
   - `enabled: false` なので有効化が必要
   - 設定を確認して動作確認

---

## 📝 サイト追加手順

### AI Weeklyの場合

```bash
# 既存設定を確認
cat data/sites/ai_weekly.json

# 設定が正しいことを確認したら、有効化する場合は:
# enabled: true に変更するか、コマンドで再追加
```

---

## 🔄 次のステップ

1. 既存の `ai_weekly` 設定を確認
2. 必要に応じて設定を修正・有効化
3. 新しいサイトを追加（必要に応じて）
4. 動作確認

---

**最終更新**: 2025-01-18

