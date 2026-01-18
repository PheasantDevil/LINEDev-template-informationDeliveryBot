# 作業フロー

## 基本的な作業手順

### 1. 作業ブランチの作成

新しい作業を開始する際は、**必ず最新の`main`ブランチから`feature/**`ブランチを作成**してください。

```bash
# 最新のmainブランチを取得
git fetch origin

# mainブランチに切り替え
git checkout main

# mainブランチを最新にする
git pull origin main

# 新しいfeatureブランチを作成
git checkout -b feature/feature-name

# 例: RSSリーダー実装の場合
# git checkout -b feature/rss-reader
```

### 2. 実装作業

作業ブランチで実装を進めます。

```bash
# 作業ブランチで実装
# ファイルの編集、新規作成など
```

### 3. コミット・プッシュ

**作業を終えるごとにコミット・プッシュ**してください。

```bash
# 変更をステージング
git add .

# コミット（意味のあるコミットメッセージを付ける）
git commit -m "feat: RSSリーダーを実装

- feedparserライブラリを追加
- RSSReaderCollectorクラスを実装
- collect_and_deliver.pyに統合"

# リモートにプッシュ
git push origin feature/feature-name
```

### 4. 複数回のコミット

大きな作業の場合は、**機能ごとに小分けしてコミット**してください。

```bash
# 例: RSSリーダー実装の場合
git add requirements.txt
git commit -m "chore: feedparserライブラリを追加"

git add src/collectors/rss_reader.py
git commit -m "feat: RSSReaderCollectorクラスを実装"

git add src/collectors/__init__.py src/collect_and_deliver.py
git commit -m "feat: RSSリーダーをcollect_and_deliver.pyに統合"

# 各コミット後にプッシュ
git push origin feature/feature-name
```

### 5. mainブランチへのマージ

作業が完了したら、mainブランチにマージします。

```bash
# mainブランチに切り替え
git checkout main

# mainブランチを最新にする
git pull origin main

# featureブランチをマージ
git merge feature/feature-name --no-ff -m "Merge feature/feature-name: 説明"

# リモートにプッシュ
git push origin main
```

## コミットメッセージのルール

### プレフィックス

- `feat:` - 新機能の追加
- `fix:` - バグ修正
- `refactor:` - リファクタリング
- `docs:` - ドキュメントの変更
- `chore:` - ビルド設定や依存関係の変更
- `test:` - テストの追加・修正

### 例

```
feat: RSSリーダーを実装

- feedparserライブラリを追加
- RSSReaderCollectorクラスを実装
- collect_and_deliver.pyに統合

fix: メール受信時のエラーハンドリングを改善

- タイムアウト処理を追加
- リトライ機能を実装

docs: READMEを更新

- セットアップ手順を追加
- RSSリーダーの使用方法を記載
```

## 注意事項

1. **必ず最新のmainブランチから作業ブランチを作成する**
   - 最新の変更を確実に取り込むため

2. **作業を終えるごとにコミット・プッシュする**
   - 作業の履歴を残すため
   - 他の開発者と共有するため

3. **意味のあるコミットメッセージを付ける**
   - 後で変更内容を理解しやすくするため

4. **機能ごとに小分けしてコミットする**
   - レビューしやすくするため
   - 問題があった場合にロールバックしやすくするため

---

**最終更新**: 2025-01-15

