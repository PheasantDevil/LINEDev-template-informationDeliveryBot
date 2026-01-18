#!/usr/bin/env python3
"""
優先度に基づいてLINEチャネル作成Issueを作成するスクリプト

候補から優先度：高（1つ）、中（2つ）のIssueを作成します。
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.suggest_channel_candidates import get_candidates, load_sites, load_existing_channels


def generate_issue_body(site: dict, channel_id: str, priority: str) -> str:
    """Issue本文を生成"""
    site_id = site.get("id", "")
    site_name = site.get("name", "")
    category = site.get("category", "")
    channel_id_upper = channel_id.upper()
    
    # 期限は2週間後
    due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    created_date = datetime.now().strftime("%Y-%m-%d")
    
    # テンプレートを読み込み
    template_path = project_root / ".github" / "ISSUE_TEMPLATE" / "channel-creation.md"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
    else:
        template = "# LINEチャネル作成タスク\n\n## 📋 チャネル情報\n\n- **チャネル名**: {{CHANNEL_NAME}}\n- **サイトID**: {{SITE_ID}}\n- **カテゴリ**: {{CATEGORY}}\n- **優先度**: {{PRIORITY}}\n\n**作成日**: {{CREATED_DATE}}\n**期限**: {{DUE_DATE}}\n"
    
    priority_emoji = {"high": "🔴 高", "medium": "🟡 中", "low": "🟢 低"}
    priority_text = priority_emoji.get(priority, "不明")
    
    # テンプレート変数を置換
    body = template.replace("{{CHANNEL_NAME}}", site_name)
    body = body.replace("{{SITE_ID}}", site_id)
    body = body.replace("{{CATEGORY}}", category)
    body = body.replace("{{CHANNEL_ID}}", channel_id)
    body = body.replace("{{CHANNEL_ID_UPPER}}", channel_id_upper)
    body = body.replace("{{CREATED_DATE}}", created_date)
    body = body.replace("{{DUE_DATE}}", due_date)
    body = body.replace("{{RELATED_ISSUES}}", "なし")
    
    # 優先度をテンプレートに反映
    if "優先度" in body and "{{PRIORITY}}" not in body:
        # 既存の優先度行を置換
        body = body.replace("優先度**: 🔴 高 / 🟡 中 / 🟢 低", f"優先度**: {priority_text}")
    
    return body


def create_issue_with_gh(title: str, body: str, priority: str) -> bool:
    """GitHub CLIを使用してIssueを作成"""
    try:
        import subprocess
        
        # 一時ファイルに本文を保存
        body_file = project_root / "tmp" / f"issue_body_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        body_file.parent.mkdir(exist_ok=True)
        with open(body_file, "w", encoding="utf-8") as f:
            f.write(body)
        
        # ラベルを決定（既存のラベルのみ使用）
        labels = ["channel-creation"]
        # priorityラベルは必要に応じて手動で追加
        
        # gh issue createコマンドを実行
        cmd = [
            "gh", "issue", "create",
            "--title", title,
            "--body-file", str(body_file),
            "--label", ",".join(labels)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            issue_url = result.stdout.strip()
            print(f"✓ Issue created: {issue_url}")
            body_file.unlink()  # 一時ファイルを削除
            return True
        else:
            print(f"❌ Issue creation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """メイン処理"""
    print("=" * 60)
    print("LINEチャネル作成Issue生成（優先度別）")
    print("=" * 60)
    print()
    
    # サイト設定を読み込み
    sites = load_sites()
    existing_channels = load_existing_channels()
    
    # 候補を取得
    candidates = get_candidates(sites, existing_channels, limit=10)
    
    if not candidates:
        print("❌ チャネル作成候補が見つかりませんでした")
        sys.exit(1)
    
    # 優先度別にグループ化
    high_priority = [c for c in candidates if c["priority"] == "high"]
    medium_priority = [c for c in candidates if c["priority"] == "medium"]
    
    # 高優先度：1つ、中優先度：2つを選択
    selected = []
    
    if high_priority:
        selected.append(("high", high_priority[0]))
        print(f"🔴 高優先度: {high_priority[0]['site_name']} を選択")
    
    if medium_priority:
        for candidate in medium_priority[:2]:
            selected.append(("medium", candidate))
            print(f"🟡 中優先度: {candidate['site_name']} を選択")
    
    if not selected:
        print("❌ 選択可能な候補がありません")
        sys.exit(1)
    
    print()
    print(f"合計 {len(selected)} 件のIssueを作成します")
    print()
    
    # Issueを作成
    created_count = 0
    for priority, candidate in selected:
        site = candidate["site"]
        channel_id = candidate["channel_id"]
        site_name = candidate["site_name"]
        
        title = f"📱 LINEチャネル作成: {site_name} ({channel_id})"
        body = generate_issue_body(site, channel_id, priority)
        
        print(f"作成中: {title}")
        if create_issue_with_gh(title, body, priority):
            created_count += 1
        print()
    
    print("=" * 60)
    print(f"✓ {created_count}件のIssueを作成しました")
    print("=" * 60)


if __name__ == "__main__":
    main()

