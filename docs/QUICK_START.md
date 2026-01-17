# クイックスタートガイド

## 依存関係のインストール

```bash
# 仮想環境の作成（推奨）
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
python3 -m pip install -r requirements.txt
```

**注意**: macOSでは`pip`コマンドが利用できない場合があります。その場合は`python3 -m pip`を使用してください。

## テスト実行

### 1. 環境変数の確認

`.env`ファイルに以下が設定されているか確認：
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `GMAIL_ACCOUNT`
- `GMAIL_APP_PASSWORD`
- `GEMINI_API_KEY`

### 2. 情報収集・配信スクリプトの実行

```bash
# プロジェクトルートから実行
python3 src/collect_and_deliver.py
```

### 3. Webhookサーバーの起動

```bash
# プロジェクトルートから実行
python3 src/webhook_server.py
```

## トラブルシューティング

### ModuleNotFoundError: No module named 'src'

**解決方法:**
- プロジェクトルートから実行しているか確認
- 依存関係がインストールされているか確認

### ModuleNotFoundError: No module named 'bs4'

**解決方法:**
```bash
# 仮想環境をアクティベートしてから実行
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

### zsh: command not found: pip

**解決方法:**
```bash
# python3 -m pip を使用
python3 -m pip install -r requirements.txt

# または仮想環境を作成してから実行
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

---

**最終更新**: 2025-01-12

