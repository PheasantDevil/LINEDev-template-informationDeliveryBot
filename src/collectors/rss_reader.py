"""RSS/Atomフィードから情報を収集するモジュール"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urlparse

import feedparser
import requests

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.collectors.base import BaseInformationCollector, InformationItem
from src.diff_detector import DiffDetector
from src.storage import Storage


class RSSReaderCollector(BaseInformationCollector):
    """RSS/Atomフィードから情報を収集するクラス"""
    
    def __init__(self, storage: Optional[Storage] = None):
        """
        初期化
        
        Args:
            storage: Storageインスタンス
        """
        super().__init__(storage)
        self.max_retries = 3
        self.timeout = 30
    
    def collect(self, site_config: Dict) -> List[InformationItem]:
        """
        RSS/Atomフィードから情報を収集
        
        Args:
            site_config: サイト設定
            
        Returns:
            List[InformationItem]: 収集した情報アイテムのリスト
        """
        collector_config = site_config.get('collector_config', {})
        feed_url = collector_config.get('feed_url') or site_config.get('url', '')
        
        if not feed_url:
            print(f"警告: RSSフィードURLが設定されていません (site_id: {site_config.get('id')})")
            return []
        
        # フィードを取得・パース
        feed = self._fetch_feed(feed_url)
        if not feed:
            return []
        
        # エントリから情報アイテムを生成
        items = []
        for entry in feed.entries:
            item = self._parse_entry_to_item(entry, site_config)
            if item:
                items.append(item)
        
        return items
    
    def _fetch_feed(self, feed_url: str) -> Optional[feedparser.FeedParserDict]:
        """
        RSS/Atomフィードを取得・パース
        
        Args:
            feed_url: フィードURL
            
        Returns:
            feedparser.FeedParserDict: パースされたフィード。エラーの場合はNone
        """
        for attempt in range(self.max_retries):
            try:
                print(f"  RSSフィードを取得中: {feed_url} (試行 {attempt + 1}/{self.max_retries})")
                
                # リクエストヘッダーを設定（User-Agentなど）
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                # feedparserでフィードを取得・パース
                feed = feedparser.parse(feed_url, agent=headers.get('User-Agent'))
                
                # エラーをチェック
                if feed.bozo:
                    error_msg = feed.bozo_exception if hasattr(feed, 'bozo_exception') else 'Unknown error'
                    print(f"  警告: フィードのパースエラー - {error_msg}")
                    # bozoエラーでもエントリがあれば処理を続行
                    if not feed.entries:
                        return None
                
                if not feed.entries:
                    print(f"  警告: フィードにエントリがありません")
                    return None
                
                print(f"  ✓ フィードを取得しました: {len(feed.entries)}件のエントリ")
                return feed
                
            except requests.exceptions.Timeout:
                print(f"  ⚠️ タイムアウトエラー (試行 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数バックオフ
                else:
                    print(f"  ❌ タイムアウト: 最大試行回数に達しました")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️ ネットワークエラー: {e} (試行 {attempt + 1}/{self.max_retries})")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数バックオフ
                else:
                    print(f"  ❌ ネットワークエラー: 最大試行回数に達しました")
                    return None
                    
            except Exception as e:
                print(f"  ❌ 予期しないエラー: {e}")
                return None
        
        return None
    
    def _parse_entry_to_item(
        self,
        entry: feedparser.FeedParserDict,
        site_config: Dict
    ) -> Optional[InformationItem]:
        """
        RSSエントリをInformationItemに変換
        
        Args:
            entry: RSSエントリ
            site_config: サイト設定
            
        Returns:
            InformationItem: 情報アイテム
        """
        try:
            # タイトルを取得
            title = entry.get('title', '').strip()
            if not title:
                title = "タイトルなし"
            
            # URLを取得（linkまたはlinksから）
            url = entry.get('link', '')
            if not url and entry.get('links'):
                url = entry.links[0].get('href', '')
            
            if not url:
                print(f"  警告: URLが見つかりません (title: {title[:50]})")
                return None
            
            # 公開日時を取得
            published_at = self._parse_entry_date(entry)
            
            # 要約を取得（description、summary、contentから）
            summary = self._extract_summary(entry)
            
            # コンテンツハッシュを生成
            detector = DiffDetector()
            content_hash = detector.generate_content_hash(title, url, summary)
            
            item = InformationItem(
                title=title,
                url=url,
                category=site_config.get('category', ''),
                site_id=site_config.get('id', ''),
                site_name=site_config.get('name', ''),
                published_at=published_at,
                summary=summary,
                content_hash=content_hash
            )
            
            return item
            
        except Exception as e:
            print(f"  エラー: RSSエントリのパースに失敗しました - {e}")
            return None
    
    def _parse_entry_date(self, entry: feedparser.FeedParserDict) -> str:
        """
        RSSエントリの日時をパース
        
        Args:
            entry: RSSエントリ
            
        Returns:
            str: ISO形式の日時文字列
        """
        # published_parsedを優先的に使用
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                dt = datetime(*entry.published_parsed[:6])
                return dt.isoformat()
            except (ValueError, TypeError):
                pass
        
        # updated_parsedを試す
        if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            try:
                dt = datetime(*entry.updated_parsed[:6])
                return dt.isoformat()
            except (ValueError, TypeError):
                pass
        
        # 文字列の日時をパース
        date_str = entry.get('published') or entry.get('updated') or ''
        if date_str:
            try:
                # feedparserの日時パースを試す
                import email.utils
                parsed_date = email.utils.parsedate_to_datetime(date_str)
                if parsed_date:
                    return parsed_date.isoformat()
            except (ValueError, TypeError):
                pass
        
        # デフォルト: 現在時刻
        return datetime.now().isoformat()
    
    def _extract_summary(self, entry: feedparser.FeedParserDict) -> Optional[str]:
        """
        RSSエントリから要約を抽出
        
        Args:
            entry: RSSエントリ
            
        Returns:
            str: 要約。存在しない場合はNone
        """
        # 優先順位: summary -> description -> content[0].value
        summary = entry.get('summary', '')
        if not summary:
            summary = entry.get('description', '')
        if not summary and entry.get('content'):
            # contentはリストの場合がある
            content = entry.content[0] if isinstance(entry.content, list) else entry.content
            summary = content.get('value', '')
        
        # HTMLタグを除去（簡易的）
        if summary:
            summary = summary.strip()
            # HTMLタグの簡易除去
            import re
            summary = re.sub(r'<[^>]+>', '', summary)
            summary = summary.strip()
            
            # 長すぎる場合は切り詰め（500文字まで）
            if len(summary) > 500:
                summary = summary[:500] + "..."
            
            return summary if summary else None
        
        return None

