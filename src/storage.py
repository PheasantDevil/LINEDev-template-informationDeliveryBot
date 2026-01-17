"""データの永続化を管理するモジュール"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse


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
    
    def validate_site(self, site: Dict) -> Tuple[bool, List[str]]:
        """
        サイト設定をバリデーション
        
        Args:
            site: サイト設定
            
        Returns:
            Tuple[bool, List[str]]: (バリデーション成功, エラーメッセージのリスト)
        """
        errors = []
        
        # 必須フィールドチェック
        if not site.get('id'):
            errors.append('idは必須です')
        else:
            # idの形式チェック（英数字とアンダースコアのみ）
            site_id = site['id']
            if not re.match(r'^[a-zA-Z0-9_]+$', site_id):
                errors.append(f'idは英数字とアンダースコアのみ使用できます (現在の値: {site_id})')
        
        if not site.get('name'):
            errors.append('nameは必須です')
        
        if not site.get('url'):
            errors.append('urlは必須です')
        else:
            # URL形式の検証
            url = site['url']
            try:
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    errors.append(f'urlは有効なURL形式である必要があります (現在の値: {url})')
            except Exception:
                errors.append(f'urlは有効なURL形式である必要があります (現在の値: {url})')
        
        if not site.get('category'):
            errors.append('categoryは必須です')
        
        collector_type = site.get('collector_type')
        if not collector_type:
            errors.append('collector_typeは必須です')
        elif collector_type not in ['email', 'rss', 'scraper']:
            errors.append(f'collector_typeは email, rss, scraper のいずれかである必要があります (現在の値: {collector_type})')
        
        # 収集方式別の設定チェック
        collector_config = site.get('collector_config', {})
        
        if collector_type == 'email':
            # email方式の場合、email_account_idとsubscription_emailは必須
            if not collector_config.get('email_account_id'):
                errors.append('email方式の場合、collector_config.email_account_idは必須です')
            
            if not collector_config.get('subscription_email'):
                errors.append('email方式の場合、collector_config.subscription_emailは必須です')
            else:
                # メールアドレスの形式チェック（簡易的）
                email = collector_config['subscription_email']
                if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                    errors.append(f'subscription_emailは有効なメールアドレス形式である必要があります (現在の値: {email})')
        
        elif collector_type == 'rss':
            # rss方式の場合、feed_urlは必須（またはurlを使用）
            feed_url = collector_config.get('feed_url') or site.get('url', '')
            if not feed_url:
                errors.append('rss方式の場合、collector_config.feed_urlまたはurlが必須です')
            else:
                # URL形式の検証
                try:
                    parsed = urlparse(feed_url)
                    if not parsed.scheme or not parsed.netloc:
                        errors.append(f'feed_urlは有効なURL形式である必要があります (現在の値: {feed_url})')
                except Exception:
                    errors.append(f'feed_urlは有効なURL形式である必要があります (現在の値: {feed_url})')
        
        # scraper方式の場合、selectorは推奨（必須ではないため警告のみ）
        if collector_type == 'scraper' and not collector_config.get('selector'):
            # 警告はエラーとして扱わない（将来的に警告機能を追加する場合は別途実装）
            pass
        
        # check_interval_minutesの範囲チェック
        check_interval = collector_config.get('check_interval_minutes')
        if check_interval is not None:
            if not isinstance(check_interval, int):
                errors.append('check_interval_minutesは整数である必要があります')
            elif check_interval <= 0:
                errors.append('check_interval_minutesは1以上の正の数である必要があります')
        
        return len(errors) == 0, errors
    
    def save_site(self, site: Dict) -> bool:
        """
        個別サイト設定を保存し、sites.jsonも更新
        
        Args:
            site: サイト設定
            
        Returns:
            bool: 保存が成功したかどうか
        """
        # バリデーションを実行
        is_valid, errors = self.validate_site(site)
        if not is_valid:
            print("❌ サイト設定のバリデーションエラー:")
            for error in errors:
                print(f"  - {error}")
            return False
        
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
            # 個別ファイルを保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(site_data, f, ensure_ascii=False, indent=2)
            
            # sites.jsonも更新（集約ファイル）
            self._update_sites_json()
            
            return True
        except Exception as e:
            print(f"エラー: サイト設定の保存に失敗しました - {e}")
            return False
    
    def _update_sites_json(self):
        """
        data/sites/内の個別ファイルを集約してsites.jsonを更新
        """
        sites = []
        
        # sitesディレクトリ内の全JSONファイルを読み込み
        for file_path in self.sites_dir.glob('*.json'):
            # _index.jsonやexampleファイルはスキップ
            if file_path.name.startswith('_') or file_path.name.endswith('.example.json'):
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
        
        # sites.jsonを更新
        data = {
            'updated_at': datetime.now().isoformat(),
            'count': len(sites),
            'sites': sites
        }
        self.save_json('sites.json', data)
    
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
        # sites.jsonが存在する場合は優先的に読み込む
        sites_json_path = self.data_dir / 'sites.json'
        if sites_json_path.exists():
            data = self.load_json('sites.json')
            if data:
                return data
        
        # sites.jsonが存在しない場合は個別ファイルから集約
        sites = []
        
        # sitesディレクトリ内の全JSONファイルを読み込み
        for file_path in self.sites_dir.glob('*.json'):
            # _index.jsonやexampleファイルはスキップ
            if file_path.name.startswith('_') or file_path.name.endswith('.example.json'):
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
        
        data = {
            'updated_at': datetime.now().isoformat(),
            'count': len(sites),
            'sites': sites
        }
        
        # sites.jsonを更新（次回から読み込めるように）
        self.save_json('sites.json', data)
        
        return data
    
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
        # save_site内で_update_sites_jsonが呼ばれるが、最後に念のため更新
        self._update_sites_json()
        return success
    
    def delete_site(self, site_id: str) -> bool:
        """
        サイト設定を削除し、sites.jsonも更新
        
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
            # sites.jsonも更新
            self._update_sites_json()
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

