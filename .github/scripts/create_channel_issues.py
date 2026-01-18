#!/usr/bin/env python3
"""
LINEチャネル作成Issueを自動生成するスクリプト

週次で実行され、未作成のチャネルに対してIssueを作成します。
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

import requests

# GitHub API settings
GITHUB_API_BASE = "https://api.github.com"
REPO_OWNER = os.getenv("GITHUB_REPOSITORY", "").split("/")[0]
REPO_NAME = os.getenv("GITHUB_REPOSITORY", "").split("/")[1] if "/" in os.getenv("GITHUB_REPOSITORY", "") else "LINEDev-template-informationDeliveryBot"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SITES_DIR = PROJECT_ROOT / "data" / "sites"
CHANNELS_FILE = PROJECT_ROOT / "data" / "channels.json"


def normalize_channel_id(site_id: str, category: str = None) -> str:
    """
    チャネルIDを正規化

    Args:
        site_id: サイトID
        category: カテゴリ名（オプション）

    Returns:
        str: 正規化されたチャネルID
    """
    if site_id:
        return f"channel_{site_id}"
    elif category:
        return f"channel_{category.lower()}"
    else:
        raise ValueError("site_id or category is required")


def channel_id_to_upper(channel_id: str) -> str:
    """
    チャネルIDを大文字に変換（環境変数名用）

    Args:
        channel_id: チャネルID

    Returns:
        str: 大文字に変換されたチャネルID
    """
    return channel_id.upper()


def load_sites() -> list:
    """
    サイト設定を読み込み

    Returns:
        list: サイト設定のリスト
    """
    sites_data_path = PROJECT_ROOT / "data" / "sites.json"
    
    if not sites_data_path.exists():
        print("Warning: sites.json not found")
        return []
    
    with open(sites_data_path, "r", encoding="utf-8") as f:
        sites_data = json.load(f)
    
    return sites_data.get("sites", [])


def load_existing_channels() -> list:
    """
    既存のチャネル設定を読み込み

    Returns:
        list: チャネルIDのリスト
    """
    if not CHANNELS_FILE.exists():
        return []
    
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        channels_data = json.load(f)
    
    return [ch["channel_id"] for ch in channels_data.get("channels", [])]


def check_existing_issue(channel_id: str, repo_owner: str, repo_name: str) -> bool:
    """
    既存のIssueがあるかチェック

    Args:
        channel_id: チャネルID
        repo_owner: リポジトリオーナー
        repo_name: リポジトリ名

    Returns:
        bool: Issueが存在する場合True
    """
    if not GITHUB_TOKEN:
        return False
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    # 未クローズのIssueを検索
    url = f"{GITHUB_API_BASE}/repos/{repo_owner}/{repo_name}/issues"
    params = {
        "state": "open",
        "labels": "channel-creation",
        "per_page": 100
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        issues = response.json()
        
        # チャネルIDが含まれるIssueをチェック
        for issue in issues:
            if channel_id in issue.get("title", "") or channel_id in issue.get("body", ""):
                return True
        
        return False
    except Exception as e:
        print(f"Error checking existing issues: {e}")
        return False


def create_issue(title: str, body: str, labels: list, repo_owner: str, repo_name: str) -> bool:
    """
    GitHub Issueを作成

    Args:
        title: Issueタイトル
        body: Issue本文
        labels: ラベルリスト
        repo_owner: リポジトリオーナー
        repo_name: リポジトリ名

    Returns:
        bool: 作成が成功した場合True
    """
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN is not set")
        return False
    
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    url = f"{GITHUB_API_BASE}/repos/{repo_owner}/{repo_name}/issues"
    data = {
        "title": title,
        "body": body,
        "labels": labels
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        issue = response.json()
        print(f"✓ Issue created: #{issue['number']} - {title}")
        return True
    except Exception as e:
        print(f"Error creating issue: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return False


def generate_issue_body(site: dict, channel_id: str) -> str:
    """
    Issue本文を生成

    Args:
        site: サイト設定
        channel_id: チャネルID

    Returns:
        str: Issue本文
    """
    site_id = site.get("id", "")
    site_name = site.get("name", "")
    category = site.get("category", "")
    channel_id_upper = channel_id_to_upper(channel_id)
    
    # 期限は2週間後
    due_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    created_date = datetime.now().strftime("%Y-%m-%d")
    
    # テンプレートを読み込み
    template_path = PROJECT_ROOT / ".github" / "ISSUE_TEMPLATE" / "channel-creation.md"
    if template_path.exists():
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
    else:
        # フォールバックテンプレート
        template = """# LINEチャネル作成タスク

## 📋 チャネル情報

- **チャネル名**: {{CHANNEL_NAME}}
- **サイトID**: {{SITE_ID}}
- **カテゴリ**: {{CATEGORY}}

## 🎯 作成タスク

[タスクリストは省略]

## 📝 命名規則

### チャネルID
- 形式: `channel_{{SITE_ID}}`
- 例: `channel_ai_weekly`

### 環境変数名
- Channel Access Token: `LINE_CHANNEL_ACCESS_TOKEN_{{CHANNEL_ID_UPPER}}`
- Channel Secret: `LINE_CHANNEL_SECRET_{{CHANNEL_ID_UPPER}}`

**作成日**: {{CREATED_DATE}}
**期限**: {{DUE_DATE}}
"""
    
    # テンプレート変数を置換
    body = template.replace("{{CHANNEL_NAME}}", site_name)
    body = body.replace("{{SITE_ID}}", site_id)
    body = body.replace("{{CATEGORY}}", category)
    body = body.replace("{{CHANNEL_ID}}", channel_id)
    body = body.replace("{{CHANNEL_ID_UPPER}}", channel_id_upper)
    body = body.replace("{{CREATED_DATE}}", created_date)
    body = body.replace("{{DUE_DATE}}", due_date)
    
    return body


def main():
    """メイン処理"""
    print("=" * 60)
    print("LINEチャネル作成Issue生成スクリプト")
    print("=" * 60)
    
    # サイト設定を読み込み
    sites = load_sites()
    print(f"Loaded {len(sites)} sites")
    
    # 既存のチャネルを読み込み
    existing_channels = load_existing_channels()
    print(f"Existing channels: {len(existing_channels)}")
    
    # 未作成のチャネルを特定
    channels_to_create = []
    for site in sites:
        if not site.get("enabled", False):
            continue
        
        site_id = site.get("id", "")
        channel_id = normalize_channel_id(site_id)
        
        # 既にチャネルが存在する場合はスキップ
        if channel_id in existing_channels:
            print(f"Skipped: {channel_id} (already exists)")
            continue
        
        # 既存のIssueがある場合はスキップ
        if check_existing_issue(channel_id, REPO_OWNER, REPO_NAME):
            print(f"Skipped: {channel_id} (issue already exists)")
            continue
        
        channels_to_create.append((site, channel_id))
    
    if not channels_to_create:
        print("\n✓ No new channels to create")
        return
    
    print(f"\nFound {len(channels_to_create)} channels to create")
    
    # Issueを作成
    created_count = 0
    for site, channel_id in channels_to_create:
        site_name = site.get("name", "")
        title = f"📱 LINEチャネル作成: {site_name} ({channel_id})"
        body = generate_issue_body(site, channel_id)
        labels = ["channel-creation", "enhancement"]
        
        if create_issue(title, body, labels, REPO_OWNER, REPO_NAME):
            created_count += 1
    
    print(f"\n✓ Created {created_count} issues")


if __name__ == "__main__":
    main()

