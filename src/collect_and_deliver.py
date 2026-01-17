"""情報収集・配信実行スクリプト"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

from src.collectors.base import BaseInformationCollector, InformationItem
from src.collectors.email_collector import EmailCollector
from src.diff_detector import DiffDetector
from src.line_notifier import LineNotifier
from src.storage import Storage
from src.user_manager import UserManager


def main():
    """メイン処理"""
    print("=" * 60)
    print("情報収集・配信スクリプト開始")
    print("=" * 60)
    
    # 環境変数の確認（デバッグ用）
    line_token_exists = bool(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
    gmail_account_exists = bool(os.getenv('GMAIL_ACCOUNT'))
    gemini_key_exists = bool(os.getenv('GEMINI_API_KEY'))
    
    print(f"環境変数チェック:")
    print(f"  LINE_CHANNEL_ACCESS_TOKEN: {'✓' if line_token_exists else '✗'}")
    print(f"  GMAIL_ACCOUNT: {'✓' if gmail_account_exists else '✗'}")
    print(f"  GEMINI_API_KEY: {'✓' if gemini_key_exists else '✗'}")
    
    # 初期化
    storage = Storage()
    user_manager = UserManager(storage)
    diff_detector = DiffDetector()
    
    # LINE通知の初期化
    try:
        line_notifier = LineNotifier()
    except ValueError as e:
        print(f"❌ LINE Notifierの初期化エラー: {e}")
        print("環境変数 LINE_CHANNEL_ACCESS_TOKEN が設定されているか確認してください")
        print("⚠️ LINE Notifierが初期化できませんでしたが、情報収集のみ続行します")
        line_notifier = None
    
    # サイト設定を読み込み
    sites_data = storage.load_sites()
    if not sites_data or not sites_data.get('sites'):
        print("⚠️ 警告: サイト設定が見つかりません")
        print("✓ サイト設定がないため、処理を正常終了します")
        sys.exit(0)
    
    sites = sites_data.get('sites', [])
    enabled_sites = [s for s in sites if s.get('enabled', False)]
    
    print(f"有効なサイト数: {len(enabled_sites)}")
    
    # 各サイトから情報を収集
    all_new_items = []
    
    for site in enabled_sites:
        site_id = site.get('id', '')
        site_name = site.get('name', '不明')
        collector_type = site.get('collector_type', '')
        
        print(f"\n--- サイト: {site_name} ({site_id}) ---")
        
        # 収集タイミングをチェック
        collector = _create_collector(collector_type, storage)
        if not collector:
            print(f"警告: コレクタータイプ '{collector_type}' は未実装です")
            continue
        
        if not collector.should_collect(site):
            print(f"スキップ: 収集タイミングではありません")
            continue
        
        # 情報を収集
        try:
            items = collector.collect(site)
            print(f"収集した情報: {len(items)}件")
            
            if items:
                # 差分検知で新着情報を抽出
                stored_items_data = storage.load_information_items()
                stored_items = stored_items_data.get('items', []) if stored_items_data else []
                
                new_items = diff_detector.detect_new_items(items, stored_items)
                print(f"新着情報: {len(new_items)}件")
                
                if new_items:
                    all_new_items.extend(new_items)
                    
                    # 収集完了を記録
                    collector.mark_as_collected(site_id, items)
                    
                    # 情報アイテムを保存
                    _save_new_items(storage, new_items, stored_items)
        except Exception as e:
            print(f"❌ エラー: 情報収集に失敗しました - {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 新着情報を配信
    if all_new_items:
        if line_notifier is None:
            print(f"\n⚠️ 警告: 新着情報 {len(all_new_items)}件がありますが、LINE Notifierが初期化されていないため配信をスキップします")
        else:
            print(f"\n--- 新着情報の配信開始 ({len(all_new_items)}件) ---")
            _deliver_new_items(all_new_items, user_manager, line_notifier)
    else:
        print("\n新着情報はありませんでした")
    
    print("\n" + "=" * 60)
    print("情報収集・配信スクリプト完了")
    print("=" * 60)


def _create_collector(
    collector_type: str,
    storage: Storage
) -> BaseInformationCollector:
    """
    コレクターを作成
    
    Args:
        collector_type: コレクタータイプ
        storage: Storageインスタンス
        
    Returns:
        BaseInformationCollector: コレクターインスタンス
    """
    if collector_type == 'email':
        return EmailCollector(storage)
    # 将来的に他のタイプも追加
    # elif collector_type == 'rss':
    #     return RSSReaderCollector(storage)
    # elif collector_type == 'scraper':
    #     return ScraperCollector(storage)
    else:
        return None


def _save_new_items(
    storage: Storage,
    new_items: List[InformationItem],
    stored_items: List[Dict]
):
    """
    新着情報アイテムを保存
    
    Args:
        storage: Storageインスタンス
        new_items: 新着情報アイテムのリスト
        stored_items: 既存の情報アイテムのリスト
    """
    # 新着アイテムを辞書形式に変換
    new_items_dict = [item.to_dict() for item in new_items]
    
    # 既存アイテムと統合
    all_items = stored_items + new_items_dict
    
    # 最新1000件のみ保持（簡易的な実装）
    if len(all_items) > 1000:
        all_items = sorted(all_items, key=lambda x: x.get('scraped_at', ''), reverse=True)[:1000]
    
    storage.save_information_items(all_items)


def _deliver_new_items(
    new_items: List[InformationItem],
    user_manager: UserManager,
    line_notifier: LineNotifier
):
    """
    新着情報を配信
    
    Args:
        new_items: 新着情報アイテムのリスト
        user_manager: UserManagerインスタンス
        line_notifier: LineNotifierインスタンス
    """
    # カテゴリごとにグループ化
    items_by_category = {}
    for item in new_items:
        category = item.category
        if category not in items_by_category:
            items_by_category[category] = []
        items_by_category[category].append(item)
    
    # カテゴリごとに配信
    for category, items in items_by_category.items():
        # カテゴリを購読しているユーザーを取得
        user_ids = user_manager.get_subscribed_users(category)
        
        if not user_ids:
            print(f"カテゴリ '{category}' を購読しているユーザーがいません")
            continue
        
        print(f"カテゴリ '{category}': {len(user_ids)}人のユーザーに配信")
        
        # 各ユーザーに配信
        for user_id in user_ids:
            try:
                success = line_notifier.send_information_items(user_id, [item.to_dict() for item in items])
                if success:
                    print(f"✓ 配信成功: {user_id[:10]}...")
                else:
                    print(f"❌ 配信失敗: {user_id[:10]}...")
            except Exception as e:
                print(f"❌ 配信エラー: {user_id[:10]}... - {e}")


if __name__ == '__main__':
    main()

