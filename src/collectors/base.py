"""情報収集の統一インターフェース"""

import sys
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.storage import Storage


class InformationItem:
    """情報アイテムのデータクラス"""
    
    def __init__(
        self,
        title: str,
        url: str,
        category: str,
        site_id: str,
        site_name: str,
        published_at: Optional[str] = None,
        summary: Optional[str] = None,
        content_hash: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            title: タイトル
            url: URL
            category: カテゴリ
            site_id: サイトID
            site_name: サイト名
            published_at: 公開日時（ISO形式）
            summary: 要約
            content_hash: 内容のハッシュ（重複検知用）
        """
        self.title = title
        self.url = url
        self.category = category
        self.site_id = site_id
        self.site_name = site_name
        self.published_at = published_at or datetime.now().isoformat()
        self.summary = summary
        self.content_hash = content_hash
        self.scraped_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """
        辞書形式に変換
        
        Returns:
            Dict: 情報アイテムの辞書
        """
        return {
            'id': f"{self.site_id}_{self.scraped_at}",
            'title': self.title,
            'url': self.url,
            'category': self.category,
            'site_id': self.site_id,
            'site_name': self.site_name,
            'published_at': self.published_at,
            'scraped_at': self.scraped_at,
            'summary': self.summary,
            'content_hash': self.content_hash
        }


class BaseInformationCollector(ABC):
    """情報収集の統一インターフェース"""
    
    def __init__(self, storage: Optional[Storage] = None):
        """
        初期化
        
        Args:
            storage: Storageインスタンス
        """
        self.storage = storage or Storage()
    
    @abstractmethod
    def collect(self, site_config: Dict) -> List[InformationItem]:
        """
        情報を収集して返す
        
        Args:
            site_config: サイト設定（sites.jsonの1エントリ）
            
        Returns:
            List[InformationItem]: 収集した情報アイテムのリスト
        """
        pass
    
    def get_last_collected_time(self, site_id: str) -> Optional[datetime]:
        """
        最後に収集した時刻を取得
        
        Args:
            site_id: サイトID
            
        Returns:
            datetime: 最後に収集した時刻。未収集の場合はNone
        """
        sites_data = self.storage.load_sites()
        if not sites_data:
            return None
        
        sites = sites_data.get('sites', [])
        site = next((s for s in sites if s.get('id') == site_id), None)
        
        if not site or not site.get('last_collected_at'):
            return None
        
        try:
            return datetime.fromisoformat(site['last_collected_at'])
        except (ValueError, TypeError):
            return None
    
    def mark_as_collected(self, site_id: str, items: List[InformationItem]) -> bool:
        """
        収集完了を記録
        
        Args:
            site_id: サイトID
            items: 収集した情報アイテムのリスト
            
        Returns:
            bool: 記録が成功したかどうか
        """
        site = self.storage.load_site(site_id)
        if not site:
            return False
        
        # 最終収集時刻を更新
        site['last_collected_at'] = datetime.now().isoformat()
        
        # 統計情報を更新
        if 'stats' not in site:
            site['stats'] = {}
        site['stats']['total_collected'] = site['stats'].get('total_collected', 0) + len(items)
        site['stats']['last_collected_count'] = len(items)
        
        return self.storage.save_site(site)
    
    def should_collect(self, site_config: Dict) -> bool:
        """
        収集タイミングかどうかを判定
        
        Args:
            site_config: サイト設定
            
        Returns:
            bool: 収集タイミングの場合True
        """
        if not site_config.get('enabled', False):
            return False
        
        check_interval = site_config.get('collector_config', {}).get('check_interval_minutes', 60)
        last_collected = self.get_last_collected_time(site_config.get('id', ''))
        
        if last_collected is None:
            # 未収集の場合は収集する
            return True
        
        # 収集間隔をチェック
        elapsed_minutes = (datetime.now() - last_collected).total_seconds() / 60
        return elapsed_minutes >= check_interval

