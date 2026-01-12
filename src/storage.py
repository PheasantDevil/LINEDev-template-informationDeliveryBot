"""データの永続化を管理するモジュール"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class Storage:
    """データの保存・読み込みを管理するクラス"""
    
    def __init__(self, data_dir: str = "data"):
        """
        初期化
        
        Args:
            data_dir: データディレクトリのパス
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_json(self, filename: str, data: Dict) -> bool:
        """
        JSONファイルにデータを保存
        
        Args:
            filename: ファイル名
            data: 保存するデータ
            
        Returns:
            bool: 保存が成功したかどうか
        """
        try:
            file_path = self.data_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ データを保存しました: {file_path}")
            return True
        except Exception as e:
            print(f"エラー: データの保存に失敗しました - {e}")
            return False
    
    def load_json(self, filename: str) -> Optional[Dict]:
        """
        JSONファイルからデータを読み込み
        
        Args:
            filename: ファイル名
            
        Returns:
            Dict: 読み込んだデータ。ファイルが存在しない場合はNone
        """
        file_path = self.data_dir / filename
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"エラー: データの読み込みに失敗しました - {e}")
            return None
    
    def save_sites(self, sites: List[Dict]) -> bool:
        """
        サイト設定を保存
        
        Args:
            sites: サイト設定のリスト
            
        Returns:
            bool: 保存が成功したかどうか
        """
        data = {
            'updated_at': datetime.now().isoformat(),
            'count': len(sites),
            'sites': sites
        }
        return self.save_json('sites.json', data)
    
    def load_sites(self) -> Optional[Dict]:
        """
        サイト設定を読み込み
        
        Returns:
            Dict: サイト設定データ
        """
        return self.load_json('sites.json')
    
    def save_information_items(self, items: List[Dict]) -> bool:
        """
        情報アイテムを保存
        
        Args:
            items: 情報アイテムのリスト
            
        Returns:
            bool: 保存が成功したかどうか
        """
        data = {
            'updated_at': datetime.now().isoformat(),
            'count': len(items),
            'items': items
        }
        return self.save_json('information_items.json', data)
    
    def load_information_items(self) -> Optional[Dict]:
        """
        情報アイテムを読み込み
        
        Returns:
            Dict: 情報アイテムデータ
        """
        return self.load_json('information_items.json')
    
    def save_users(self, users: List[Dict]) -> bool:
        """
        ユーザー情報を保存
        
        Args:
            users: ユーザー情報のリスト
            
        Returns:
            bool: 保存が成功したかどうか
        """
        data = {
            'updated_at': datetime.now().isoformat(),
            'count': len(users),
            'users': users
        }
        return self.save_json('users.json', data)
    
    def load_users(self) -> Optional[Dict]:
        """
        ユーザー情報を読み込み
        
        Returns:
            Dict: ユーザー情報データ
        """
        return self.load_json('users.json')
    
    def save_category_groups(self, groups: List[Dict]) -> bool:
        """
        カテゴリグループ情報を保存
        
        Args:
            groups: カテゴリグループ情報のリスト
            
        Returns:
            bool: 保存が成功したかどうか
        """
        data = {
            'updated_at': datetime.now().isoformat(),
            'count': len(groups),
            'groups': groups
        }
        return self.save_json('category_groups.json', data)
    
    def load_category_groups(self) -> Optional[Dict]:
        """
        カテゴリグループ情報を読み込み
        
        Returns:
            Dict: カテゴリグループ情報データ
        """
        return self.load_json('category_groups.json')

