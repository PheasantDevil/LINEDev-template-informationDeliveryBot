"""ユーザー管理システム"""

from datetime import datetime
from typing import Dict, List, Optional

from src.storage import Storage


class UserManager:
    """ユーザー管理クラス"""
    
    def __init__(self, storage: Optional[Storage] = None):
        """
        初期化
        
        Args:
            storage: Storageインスタンス
        """
        self.storage = storage or Storage()
    
    def register_user(self, user_id: str, line_display_name: str = "") -> bool:
        """
        ユーザーを登録
        
        Args:
            user_id: LINEユーザーID
            line_display_name: LINE表示名
            
        Returns:
            bool: 登録が成功したかどうか
        """
        users_data = self.storage.load_users() or {'users': []}
        users = users_data.get('users', [])
        
        # 既存ユーザーかチェック
        existing_user = next((u for u in users if u['user_id'] == user_id), None)
        if existing_user:
            print(f"ユーザーは既に登録されています: {user_id[:10]}...")
            return True
        
        # 新規ユーザーを追加
        new_user = {
            'user_id': user_id,
            'line_display_name': line_display_name,
            'subscribed_categories': [],
            'subscribed_sites': [],
            'notification_groups': {},
            'registered_at': datetime.now().isoformat(),
            'last_active_at': datetime.now().isoformat()
        }
        
        users.append(new_user)
        return self.storage.save_users(users)
    
    def unregister_user(self, user_id: str) -> bool:
        """
        ユーザーを登録解除
        
        Args:
            user_id: LINEユーザーID
            
        Returns:
            bool: 解除が成功したかどうか
        """
        users_data = self.storage.load_users()
        if not users_data:
            return True
        
        users = users_data.get('users', [])
        users = [u for u in users if u['user_id'] != user_id]
        
        return self.storage.save_users(users)
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        ユーザー情報を取得
        
        Args:
            user_id: LINEユーザーID
            
        Returns:
            Dict: ユーザー情報。存在しない場合はNone
        """
        users_data = self.storage.load_users()
        if not users_data:
            return None
        
        users = users_data.get('users', [])
        return next((u for u in users if u['user_id'] == user_id), None)
    
    def subscribe_category(self, user_id: str, category: str) -> bool:
        """
        カテゴリを購読
        
        Args:
            user_id: LINEユーザーID
            category: カテゴリ名
            
        Returns:
            bool: 購読が成功したかどうか
        """
        user = self.get_user(user_id)
        if not user:
            print(f"ユーザーが見つかりません: {user_id[:10]}...")
            return False
        
        if category not in user['subscribed_categories']:
            user['subscribed_categories'].append(category)
            user['last_active_at'] = datetime.now().isoformat()
            return self._update_user(user)
        
        return True
    
    def unsubscribe_category(self, user_id: str, category: str) -> bool:
        """
        カテゴリの購読を解除
        
        Args:
            user_id: LINEユーザーID
            category: カテゴリ名
            
        Returns:
            bool: 解除が成功したかどうか
        """
        user = self.get_user(user_id)
        if not user:
            return False
        
        if category in user['subscribed_categories']:
            user['subscribed_categories'].remove(category)
            user['last_active_at'] = datetime.now().isoformat()
            return self._update_user(user)
        
        return True
    
    def get_subscribed_users(self, category: str) -> List[str]:
        """
        カテゴリを購読しているユーザーIDリストを取得
        
        Args:
            category: カテゴリ名
            
        Returns:
            List[str]: ユーザーIDリスト
        """
        users_data = self.storage.load_users()
        if not users_data:
            return []
        
        users = users_data.get('users', [])
        return [
            u['user_id'] for u in users
            if category in u.get('subscribed_categories', [])
        ]
    
    def _update_user(self, user: Dict) -> bool:
        """
        ユーザー情報を更新
        
        Args:
            user: 更新するユーザー情報
            
        Returns:
            bool: 更新が成功したかどうか
        """
        users_data = self.storage.load_users() or {'users': []}
        users = users_data.get('users', [])
        
        # 既存ユーザーを更新
        for i, u in enumerate(users):
            if u['user_id'] == user['user_id']:
                users[i] = user
                break
        
        return self.storage.save_users(users)

