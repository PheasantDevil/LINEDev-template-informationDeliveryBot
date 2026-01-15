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
        self.sites_dir = self.data_dir / 'sites'
        self.sites_dir.mkdir(parents=True, exist_ok=True)
        
        # 既存のsites.jsonを移行（初回のみ）
        self._migrate_legacy_sites()
    
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
    
    def _migrate_legacy_sites(self):
        """
        既存のsites.jsonを個別ファイルに移行（初回のみ）
        """
        legacy_file = self.data_dir / 'sites.json'
        if not legacy_file.exists():
            return
        
        # 既にsitesディレクトリにファイルがある場合は移行済み
        if any(self.sites_dir.glob('*.json')):
            return
        
        print("既存のsites.jsonを個別ファイルに移行中...")
        legacy_data = self.load_json('sites.json')
        if legacy_data and legacy_data.get('sites'):
            for site in legacy_data['sites']:
                site_id = site.get('id')
                if site_id:
                    self.save_site(site)
            print(f"✓ {len(legacy_data['sites'])}件のサイトを移行しました")
    
    def save_site(self, site: Dict) -> bool:
        """
        個別サイト設定を保存
        
        Args:
            site: サイト設定
            
        Returns:
            bool: 保存が成功したかどうか
        """
        site_id = site.get('id')
        if not site_id:
            print("エラー: サイトIDが設定されていません")
            return False
        
        # メタデータを追加
        site_data = {
            'updated_at': datetime.now().isoformat(),
            **site
        }
        
        filename = f"{site_id}.json"
        file_path = self.sites_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(site_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"エラー: サイト設定の保存に失敗しました - {e}")
            return False
    
    def load_site(self, site_id: str) -> Optional[Dict]:
        """
        個別サイト設定を読み込み
        
        Args:
            site_id: サイトID
            
        Returns:
            Dict: サイト設定データ。存在しない場合はNone
        """
        filename = f"{site_id}.json"
        file_path = self.sites_dir / filename
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"エラー: サイト設定の読み込みに失敗しました - {e}")
            return None
    
    def load_sites(self) -> Optional[Dict]:
        """
        全サイト設定を読み込み
        
        Returns:
            Dict: サイト設定データ（後方互換性のため従来の形式を維持）
        """
        sites = []
        
        # sitesディレクトリ内の全JSONファイルを読み込み
        for file_path in self.sites_dir.glob('*.json'):
            # _index.jsonなどの特殊ファイルはスキップ
            if file_path.name.startswith('_'):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    site_data = json.load(f)
                    # updated_atはメタデータなので除外
                    if 'updated_at' in site_data:
                        del site_data['updated_at']
                    sites.append(site_data)
            except Exception as e:
                print(f"警告: {file_path.name}の読み込みに失敗しました - {e}")
                continue
        
        return {
            'updated_at': datetime.now().isoformat(),
            'count': len(sites),
            'sites': sites
        }
    
    def save_sites(self, sites: List[Dict]) -> bool:
        """
        サイト設定リストを保存（後方互換性のため維持）
        
        Args:
            sites: サイト設定のリスト
            
        Returns:
            bool: 保存が成功したかどうか
        """
        success = True
        for site in sites:
            if not self.save_site(site):
                success = False
        return success
    
    def delete_site(self, site_id: str) -> bool:
        """
        サイト設定を削除
        
        Args:
            site_id: サイトID
            
        Returns:
            bool: 削除が成功したかどうか
        """
        filename = f"{site_id}.json"
        file_path = self.sites_dir / filename
        
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            return True
        except Exception as e:
            print(f"エラー: サイト設定の削除に失敗しました - {e}")
            return False
    
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
    
    def save_email_accounts(self, accounts: List[Dict]) -> bool:
        """
        メールアカウント情報を保存
        
        Args:
            accounts: メールアカウント情報のリスト
            
        Returns:
            bool: 保存が成功したかどうか
        """
        data = {
            'updated_at': datetime.now().isoformat(),
            'count': len(accounts),
            'accounts': accounts
        }
        return self.save_json('email_accounts.json', data)
    
    def load_email_accounts(self) -> Optional[Dict]:
        """
        メールアカウント情報を読み込み
        
        Returns:
            Dict: メールアカウント情報データ
        """
        return self.load_json('email_accounts.json')

