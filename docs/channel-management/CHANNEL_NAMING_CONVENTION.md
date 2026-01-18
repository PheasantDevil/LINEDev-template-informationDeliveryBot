# LINEチャネル命名規則

## 📋 目的

LINEチャネル作成時の手動操作における誤操作を防ぐため、統一された命名規則を定義します。

---

## 🎯 命名規則

### 1. チャネルID

**形式**: `channel_{識別子}`

**識別子の決定**:
- **サイト単位**: サイトIDを使用
  - 例: `channel_ai_weekly`
- **カテゴリ単位**: カテゴリ名（小文字）を使用
  - 例: `channel_ai`

**例**:
```
channel_ai_weekly          # AI Weekly用
channel_drone_news_001     # ドローン情報サイト用
channel_ai                 # AIカテゴリ全体用
```

---

### 2. 環境変数名

#### 2.1 GitHub Secrets / Render.com環境変数

**Channel Access Token**:
```
LINE_CHANNEL_ACCESS_TOKEN_{チャネルID（大文字）}
```

**Channel Secret**:
```
LINE_CHANNEL_SECRET_{チャネルID（大文字）}
```

**変換ルール**:
- チャネルIDを大文字に変換
- アンダースコアは維持

**例**:
```bash
# チャネルID: channel_ai_weekly
LINE_CHANNEL_ACCESS_TOKEN_CHANNEL_AI_WEEKLY
LINE_CHANNEL_SECRET_CHANNEL_AI_WEEKLY

# チャネルID: channel_drone_news_001
LINE_CHANNEL_ACCESS_TOKEN_CHANNEL_DRONE_NEWS_001
LINE_CHANNEL_SECRET_CHANNEL_DRONE_NEWS_001
```

#### 2.2 ローカル開発環境（.envファイル）

同じ命名規則を使用：

```bash
# .env
LINE_CHANNEL_ACCESS_TOKEN_CHANNEL_AI_WEEKLY=your_token_here
LINE_CHANNEL_SECRET_CHANNEL_AI_WEEKLY=your_secret_here
```

---

### 3. データファイル（channels.json）

```json
{
  "channels": [
    {
      "channel_id": "channel_ai_weekly",
      "channel_access_token": "xxx...",
      "channel_secret": "yyy...",
      "site_id": "ai_weekly",
      "category": "AI",
      "webhook_url": "https://your-service.onrender.com/webhook/channel_ai_weekly"
    }
  ]
}
```

---

## 📝 チャネル作成時のチェックリスト

### 事前準備

1. **チャネルIDの決定**
   - [ ] サイトIDまたはカテゴリ名を確認
   - [ ] チャネルIDを決定（`channel_{識別子}`形式）

2. **環境変数名の決定**
   - [ ] チャネルIDを大文字に変換
   - [ ] `LINE_CHANNEL_ACCESS_TOKEN_{大文字チャネルID}`を決定
   - [ ] `LINE_CHANNEL_SECRET_{大文字チャネルID}`を決定

### LINE Developers Console操作

1. **チャネル作成**
   - [ ] チャネル名を設定（サイト名またはカテゴリ名）
   - [ ] チャネル説明を入力

2. **トークン・シークレットの取得**
   - [ ] Channel Access Tokenを取得
   - [ ] 環境変数名をメモ: `LINE_CHANNEL_ACCESS_TOKEN_{大文字チャネルID}`
   - [ ] Channel Secretを取得
   - [ ] 環境変数名をメモ: `LINE_CHANNEL_SECRET_{大文字チャネルID}`

### 環境変数の設定

1. **GitHub Secrets**
   - [ ] `LINE_CHANNEL_ACCESS_TOKEN_{大文字チャネルID}`を追加
   - [ ] `LINE_CHANNEL_SECRET_{大文字チャネルID}`を追加

2. **Render.com環境変数**
   - [ ] `LINE_CHANNEL_ACCESS_TOKEN_{大文字チャネルID}`を追加
   - [ ] `LINE_CHANNEL_SECRET_{大文字チャネルID}`を追加

### チャネル設定の登録

```bash
python tools/manage_channel.py add \
  --channel-id {チャネルID} \
  --access-token "$LINE_CHANNEL_ACCESS_TOKEN_{大文字チャネルID}" \
  --secret "$LINE_CHANNEL_SECRET_{大文字チャネルID}" \
  --site-id {サイトID}
```

- [ ] コマンドを実行
- [ ] チャネル設定が正しく登録されたことを確認

---

## 🔍 命名規則の検証

### チャネルIDの検証

- ✅ 小文字とアンダースコアのみ
- ✅ `channel_`で始まる
- ✅ サイトIDまたはカテゴリ名が続く

**正しい例**:
- `channel_ai_weekly`
- `channel_drone_news_001`
- `channel_ai`

**間違った例**:
- `Channel_AI_Weekly` (大文字が含まれる)
- `ai_weekly` (`channel_`で始まらない)
- `channel-AI-weekly` (ハイフンは不可)

### 環境変数名の検証

- ✅ すべて大文字
- ✅ アンダースコアで区切る
- ✅ `LINE_CHANNEL_ACCESS_TOKEN_`または`LINE_CHANNEL_SECRET_`で始まる

**正しい例**:
- `LINE_CHANNEL_ACCESS_TOKEN_CHANNEL_AI_WEEKLY`
- `LINE_CHANNEL_SECRET_CHANNEL_DRONE_NEWS_001`

**間違った例**:
- `LINE_CHANNEL_ACCESS_TOKEN_channel_ai_weekly` (小文字が含まれる)
- `LINE_CHANNEL_ACCESS_TOKEN_CHANNEL-AI-WEEKLY` (ハイフンは不可)

---

## 📋 命名規則の参照表

| チャネルID | 環境変数名（Access Token） | 環境変数名（Secret） |
|-----------|------------------------|-------------------|
| `channel_ai_weekly` | `LINE_CHANNEL_ACCESS_TOKEN_CHANNEL_AI_WEEKLY` | `LINE_CHANNEL_SECRET_CHANNEL_AI_WEEKLY` |
| `channel_drone_news_001` | `LINE_CHANNEL_ACCESS_TOKEN_CHANNEL_DRONE_NEWS_001` | `LINE_CHANNEL_SECRET_CHANNEL_DRONE_NEWS_001` |
| `channel_ai` | `LINE_CHANNEL_ACCESS_TOKEN_CHANNEL_AI` | `LINE_CHANNEL_SECRET_CHANNEL_AI` |

---

## 🔗 関連ドキュメント

- `docs/LINE_CHANNEL_AUTO_MANAGEMENT_PROPOSAL.md` - チャネル自動管理の提案
- `.github/ISSUE_TEMPLATE/channel-creation.md` - チャネル作成Issueテンプレート
- `.github/workflows/create-channel-creation-issues.yml` - Issue自動生成ワークフロー

---

**最終更新**: 2025-01-18

