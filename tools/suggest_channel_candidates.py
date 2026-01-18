#!/usr/bin/env python3
"""
LINEチャネル作成候補を提示するスクリプト

現在のサイト設定から、チャネル作成候補を抽出して表示します。
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage import Storage


def load_sites() -> List[Dict]:
    """サイト設定を読み込み"""
    storage = Storage()
    sites_data = storage.load_sites()
    return sites_data.get("sites", []) if sites_data else []


def load_existing_channels() -> List[str]:
    """既存のチャネルIDを取得"""
    channels_file = project_root / "data" / "channels.json"
    if not channels_file.exists():
        return []
    
    with open(channels_file, "r", encoding="utf-8") as f:
        channels_data = json.load(f)
    
    return [ch["channel_id"] for ch in channels_data.get("channels", [])]


def calculate_priority(site: Dict) -> str:
    """
    サイトの優先度を計算

    優先度の判定基準:
    - 高: enabled=true, 収集回数が多い、重要なカテゴリ
    - 中: enabled=true または 重要なカテゴリ
    - 低: その他

    Args:
        site: サイト設定

    Returns:
        str: 優先度（"high", "medium", "low"）
    """
    enabled = site.get("enabled", False)
    stats = site.get("stats", {})
    total_collected = stats.get("total_collected", 0)
    category = site.get("category", "")
    
    # 優先度の判定
    # AI Weeklyは優先度を高に設定（実際に運用予定のため）
    if site.get("id") == "ai_weekly":
        return "high"
    elif enabled and total_collected > 0:
        # 有効で収集実績がある → 高
        return "high"
    elif enabled or category in ["AI", "ドローン", "SDGs"]:
        # 有効または主要カテゴリ → 中
        return "medium"
    else:
        # その他 → 低
        return "low"


def get_candidates(sites: List[Dict], existing_channels: List[str], limit: int = 3) -> List[Dict]:
    """
    チャネル作成候補を取得

    Args:
        sites: サイト設定のリスト
        existing_channels: 既存のチャネルIDリスト
        limit: 取得する候補数

    Returns:
        List[Dict]: 候補のリスト（優先度順）
    """
    candidates = []
    
    for site in sites:
        site_id = site.get("id", "")
        if not site_id:
            continue
        
        channel_id = f"channel_{site_id}"
        
        # 既存チャネルは除外
        if channel_id in existing_channels:
            continue
        
        priority = calculate_priority(site)
        
        candidate = {
            "site": site,
            "channel_id": channel_id,
            "priority": priority,
            "site_id": site_id,
            "site_name": site.get("name", ""),
            "category": site.get("category", ""),
            "enabled": site.get("enabled", False),
        }
        
        candidates.append(candidate)
    
    # 優先度でソート（high > medium > low）
    priority_order = {"high": 0, "medium": 1, "low": 2}
    candidates.sort(key=lambda x: (priority_order.get(x["priority"], 3), x["site_name"]))
    
    # 上位limit件を返す
    return candidates[:limit]


def print_candidates(candidates: List[Dict]):
    """候補を表示"""
    if not candidates:
        print("❌ チャネル作成候補が見つかりませんでした")
        return
    
    print("=" * 60)
    print("LINEチャネル作成候補")
    print("=" * 60)
    print()
    
    for i, candidate in enumerate(candidates, 1):
        priority_emoji = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢"
        }
        priority_name = {
            "high": "高",
            "medium": "中",
            "low": "低"
        }
        
        emoji = priority_emoji.get(candidate["priority"], "⚪")
        priority = priority_name.get(candidate["priority"], "不明")
        
        print(f"{i}. {emoji} 優先度: {priority}")
        print(f"   サイト名: {candidate['site_name']}")
        print(f"   サイトID: {candidate['site_id']}")
        print(f"   チャネルID: {candidate['channel_id']}")
        print(f"   カテゴリ: {candidate['category']}")
        print(f"   状態: {'有効' if candidate['enabled'] else '無効'}")
        print()


def main():
    """メイン処理"""
    # サイト設定を読み込み
    sites = load_sites()
    
    if not sites:
        print("❌ サイト設定が見つかりませんでした")
        sys.exit(1)
    
    # 既存チャネルを確認
    existing_channels = load_existing_channels()
    
    # 候補を取得（上位3件）
    candidates = get_candidates(sites, existing_channels, limit=3)
    
    # 候補を表示
    print_candidates(candidates)
    
    # JSON出力（スクリプト間の連携用）
    output = {
        "candidates": [
            {
                "site_id": c["site_id"],
                "channel_id": c["channel_id"],
                "priority": c["priority"],
                "site_name": c["site_name"],
                "category": c["category"],
            }
            for c in candidates
        ]
    }
    
    # 標準出力にJSONを出力（他のスクリプトから利用可能）
    json_output_file = project_root / "tmp" / "channel_candidates.json"
    json_output_file.parent.mkdir(exist_ok=True)
    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✓ 候補情報を {json_output_file} に保存しました")


if __name__ == "__main__":
    main()

