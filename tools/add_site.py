#!/usr/bin/env python3
"""サイト追加ツール

使用方法:
    python tools/add_site.py --id <site_id> --name <site_name> --url <url> --category <category> --type <collector_type> [options]
    
例:
    python tools/add_site.py --id ai_weekly --name "AI Weekly" --url https://aiweekly.co/ --category AI --type email --email-account gmail_account_001 --subscription-email infobot.delivery+aiweekly@gmail.com
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.storage import Storage


def create_email_site_config(args) -> dict:
    """メール方式のサイト設定を作成"""
    return {
        'id': args.id,
        'name': args.name,
        'url': args.url,
        'category': args.category,
        'collector_type': 'email',
        'collector_config': {
            'email_account_id': args.email_account or 'gmail_account_001',
            'subscription_email': args.subscription_email,
            'sender_email': args.sender_email or '',
            'subject_pattern': args.subject_pattern or '',
            'check_interval_minutes': args.check_interval or 60,
            'summary_enabled': args.summary_enabled,
            'summary_model': args.summary_model or 'gemini-1.5-flash'
        },
        'enabled': args.enabled,
        'created_at': datetime.now().isoformat(),
        'last_collected_at': None,
        'stats': {
            'total_collected': 0,
            'last_7_days': 0
        }
    }


def create_rss_site_config(args) -> dict:
    """RSS方式のサイト設定を作成"""
    return {
        'id': args.id,
        'name': args.name,
        'url': args.url,
        'category': args.category,
        'collector_type': 'rss',
        'collector_config': {
            'feed_url': args.feed_url or args.url,
            'check_interval_minutes': args.check_interval or 60
        },
        'enabled': args.enabled,
        'created_at': datetime.now().isoformat(),
        'last_collected_at': None,
        'stats': {
            'total_collected': 0,
            'last_7_days': 0
        }
    }


def create_scraper_site_config(args) -> dict:
    """スクレイパー方式のサイト設定を作成"""
    return {
        'id': args.id,
        'name': args.name,
        'url': args.url,
        'category': args.category,
        'collector_type': 'scraper',
        'collector_config': {
            'selector': args.selector or '',
            'check_interval_minutes': args.check_interval or 60
        },
        'enabled': args.enabled,
        'created_at': datetime.now().isoformat(),
        'last_collected_at': None,
        'stats': {
            'total_collected': 0,
            'last_7_days': 0
        }
    }


def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(
        description='サイト設定を追加するツール',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # 必須引数
    parser.add_argument('--id', required=True, help='サイトID（英数字とアンダースコア）')
    parser.add_argument('--name', required=True, help='サイト名')
    parser.add_argument('--url', required=True, help='サイトURL')
    parser.add_argument('--category', required=True, help='カテゴリ（例: AI, ドローン）')
    parser.add_argument('--type', required=True, choices=['email', 'rss', 'scraper'],
                       help='収集方式（email/rss/scraper）')
    
    # オプション引数
    parser.add_argument('--enabled', action='store_true', default=False,
                       help='有効化する（デフォルト: False）')
    parser.add_argument('--check-interval', type=int, default=60,
                       help='収集間隔（分、デフォルト: 60）')
    
    # メール方式のオプション
    parser.add_argument('--email-account', help='メールアカウントID（email方式の場合）')
    parser.add_argument('--subscription-email', help='購読メールアドレス（email方式の場合）')
    parser.add_argument('--sender-email', help='送信者メールアドレス（email方式の場合）')
    parser.add_argument('--subject-pattern', help='件名パターン（email方式の場合）')
    parser.add_argument('--summary-enabled', action='store_true', default=False,
                       help='AI要約を有効化（email方式の場合）')
    parser.add_argument('--summary-model', default='gemini-1.5-flash',
                       help='要約モデル（デフォルト: gemini-1.5-flash）')
    
    # RSS方式のオプション
    parser.add_argument('--feed-url', help='RSSフィードURL（rss方式の場合、未指定時はurlを使用）')
    
    # スクレイパー方式のオプション
    parser.add_argument('--selector', help='CSSセレクター（scraper方式の場合）')
    
    args = parser.parse_args()
    
    # サイト設定を作成
    if args.type == 'email':
        if not args.subscription_email:
            print("❌ エラー: email方式の場合、--subscription-emailが必要です")
            sys.exit(1)
        site_config = create_email_site_config(args)
    elif args.type == 'rss':
        site_config = create_rss_site_config(args)
    elif args.type == 'scraper':
        site_config = create_scraper_site_config(args)
    else:
        print(f"❌ エラー: 不明な収集方式: {args.type}")
        sys.exit(1)
    
    # サイト設定を保存
    storage = Storage()
    
    # 既存のサイトIDをチェック
    existing_site = storage.load_site(args.id)
    if existing_site:
        response = input(f"サイトID '{args.id}' は既に存在します。上書きしますか？ (y/N): ")
        if response.lower() != 'y':
            print("キャンセルしました")
            sys.exit(0)
    
    # 保存
    if storage.save_site(site_config):
        print(f"✓ サイト設定を追加しました: {args.id}")
        print(f"  名前: {args.name}")
        print(f"  URL: {args.url}")
        print(f"  カテゴリ: {args.category}")
        print(f"  収集方式: {args.type}")
        print(f"  有効: {'はい' if args.enabled else 'いいえ'}")
    else:
        print("❌ エラー: サイト設定の保存に失敗しました")
        sys.exit(1)


if __name__ == '__main__':
    main()

