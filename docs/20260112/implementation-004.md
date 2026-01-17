## 実装内容
Gmailアカウント情報とGemini APIキーの環境変数設定

## ファイル構成
- `.env`: 実際のGmailアカウント情報とGemini APIキーを設定
  - GMAIL_ACCOUNT=infobot.delivery@gmail.com
  - GMAIL_APP_PASSWORD=WFG4od-8
  - GEMINI_API_KEY=AIzaSyANP6rd7s9yTo8-Sr15z0ARwKJ-YOx0DUc
- `data/email_accounts.json`: 実際のGmailアカウント設定
- `data/sites.json`: AI Weeklyの設定を追加（enabled: false）
- `src/collectors/email_collector.py`: 環境変数GMAIL_APP_PASSWORDを優先するように修正

## エラー
なし

## 懸念点
- パスワードとAPIキーは機密情報のため、.envとdata/email_accounts.jsonは.gitignoreで除外されている
- 実際のメール受信テストは未実施
- AI Weeklyへの購読は未実施（enabled: falseのまま）

## 次のステップ
- AI Weeklyにエイリアスアドレス（infobot.delivery+aiweekly@gmail.com）で購読
- sites.jsonでenabledをtrueに設定
- 実際のメール受信・要約・LINE通知のテスト

