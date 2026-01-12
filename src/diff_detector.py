"""差分検知システム"""

import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.collectors.base import InformationItem


class DiffDetector:
    """差分検知システム"""
    
    def __init__(self):
        """初期化"""
        pass
    
    def detect_new_items(
        self,
        collected_items: List[InformationItem],
        stored_items: List[Dict]
    ) -> List[InformationItem]:
        """
        新着情報のみを抽出
        
        Args:
            collected_items: 収集した情報アイテムのリスト
            stored_items: 保存済みの情報アイテムのリスト（辞書形式）
            
        Returns:
            List[InformationItem]: 新着情報アイテムのリスト
        """
        if not stored_items:
            # 保存済みデータがない場合は全て新着
            return collected_items
        
        # 保存済みのURLとハッシュのセットを作成
        stored_urls = {item.get('url') for item in stored_items if item.get('url')}
        stored_hashes = {item.get('content_hash') for item in stored_items if item.get('content_hash')}
        
        new_items = []
        for item in collected_items:
            # URLで重複チェック
            if item.url in stored_urls:
                continue
            
            # ハッシュで重複チェック（ハッシュが設定されている場合）
            if item.content_hash and item.content_hash in stored_hashes:
                continue
            
            new_items.append(item)
        
        return new_items
    
    def generate_content_hash(self, title: str, url: str, summary: Optional[str] = None) -> str:
        """
        内容のハッシュを生成（重複検知用）
        
        Args:
            title: タイトル
            url: URL
            summary: 要約（オプション）
            
        Returns:
            str: SHA256ハッシュ
        """
        content = f"{title}|{url}"
        if summary:
            content += f"|{summary}"
        
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

