# サイト設定状況

## 📋 現在のサイト設定

### AI Weekly
- **ファイル**: `data/sites/ai_weekly.json`
- **状態**: 有効化済み (`enabled: true`)
- **設定**:
  - `check_interval_minutes`: 60分（週刊配信に適した間隔）
  - `summary_enabled`: true（AI要約有効）

**注意**: `data/sites/`配下のファイルは`.gitignore`で無視されるため、リポジトリにはコミットされません。実際の運用時は、各環境で設定ファイルを管理するか、環境変数やシークレット管理を使用してください。

---

## ✅ 設定確認項目

- [x] `ai_weekly.json`が存在する
- [x] `enabled: true`に設定されている
- [x] メールアカウント設定が正しい
- [x] 購読メールアドレスが設定されている
- [x] 収集間隔が適切（60分）

---

## 🔄 次のステップ

実際の動作確認を行う前に、以下を確認してください：

1. **メール購読の確認**
   - `infobot.delivery+aiweekly@gmail.com`でAI Weeklyを購読しているか
   - メールが届いているか

2. **環境変数の確認**
   - `GMAIL_ACCOUNT`
   - `GMAIL_APP_PASSWORD`
   - `GEMINI_API_KEY`（要約を使用する場合）

3. **動作確認の実行**
   - `python src/collect_and_deliver.py`を実行
   - ログを確認

---

**最終更新**: 2025-01-18

