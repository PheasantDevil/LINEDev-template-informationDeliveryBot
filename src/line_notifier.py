"""LINE Messaging APIを使った通知機能"""

import base64
import hashlib
import hmac
import os
from typing import Dict, List, Optional

import requests


class LineNotifier:
    """LINE Messaging APIで通知を送信するクラス"""
    
    def __init__(
        self,
        channel_access_token: Optional[str] = None,
        channel_secret: Optional[str] = None
    ):
        """
        初期化
        
        Args:
            channel_access_token: LINEチャネルアクセストークン
            channel_secret: LINEチャネルシークレット（Webhook署名検証用）
        """
        self.channel_access_token = channel_access_token or os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.channel_secret = channel_secret or os.getenv('LINE_CHANNEL_SECRET')
        self.push_api_url = 'https://api.line.me/v2/bot/message/push'
        self.reply_api_url = 'https://api.line.me/v2/bot/message/reply'
        self.multicast_api_url = 'https://api.line.me/v2/bot/message/multicast'
        
        if not self.channel_access_token:
            raise ValueError("LINE_CHANNEL_ACCESS_TOKEN が設定されていません")
    
    def send_text_message(self, user_id: str, text: str) -> bool:
        """
        テキストメッセージを送信（プッシュ）
        
        Args:
            user_id: 送信先のユーザーID
            text: 送信するテキスト
            
        Returns:
            bool: 送信が成功したかどうか
        """
        headers = {
            'Authorization': f'Bearer {self.channel_access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'to': user_id,
            'messages': [
                {
                    'type': 'text',
                    'text': text
                }
            ]
        }
        
        try:
            response = requests.post(self.push_api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            print(f"✓ LINE通知を送信しました (to: {user_id[:10]}...)")
            return True
        except requests.RequestException as e:
            print(f"エラー: LINE通知の送信に失敗しました - {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"レスポンス: {e.response.text}")
            return False
    
    def reply_text_message(self, reply_token: str, text: str) -> bool:
        """
        テキストメッセージをReply
        
        Args:
            reply_token: リプライトークン
            text: 送信するテキスト
            
        Returns:
            bool: 送信が成功したかどうか
        """
        headers = {
            'Authorization': f'Bearer {self.channel_access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'replyToken': reply_token,
            'messages': [
                {
                    'type': 'text',
                    'text': text
                }
            ]
        }
        
        try:
            response = requests.post(self.reply_api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            print("✓ LINE Replyを送信しました")
            return True
        except requests.RequestException as e:
            print(f"エラー: LINE Replyの送信に失敗しました - {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"レスポンス: {e.response.text}")
            return False
    
    def send_information_items(self, user_id: str, items: List[Dict]) -> bool:
        """
        情報アイテムを通知
        
        Args:
            user_id: 送信先のユーザーID
            items: 情報アイテムのリスト
            
        Returns:
            bool: 送信が成功したかどうか
        """
        if not items:
            print("通知する情報がありません")
            return True
        
        message = self._format_information_message(items)
        return self.send_text_message(user_id, message)
    
    def _format_information_message(self, items: List[Dict]) -> str:
        """
        情報アイテムをメッセージ形式に整形
        
        Args:
            items: 情報アイテムのリスト
            
        Returns:
            str: 整形されたメッセージ
        """
        lines = []
        lines.append(f"📰 新着情報 ({len(items)}件)")
        lines.append("=" * 30)
        lines.append("")
        
        for i, item in enumerate(items[:10], 1):  # 最大10件まで
            lines.append(f"【{i}】{item.get('title', 'タイトルなし')}")
            if item.get('category'):
                lines.append(f"カテゴリ: {item['category']}")
            if item.get('site_name'):
                lines.append(f"出典: {item['site_name']}")
            if item.get('url'):
                lines.append(f"🔗 {item['url']}")
            lines.append("")
        
        if len(items) > 10:
            lines.append(f"...他 {len(items) - 10}件")
        
        return "\n".join(lines)
    
    def send_multicast(self, user_ids: List[str], text: str) -> bool:
        """
        複数ユーザーに一斉送信（Multicast）
        
        Args:
            user_ids: 送信先のユーザーIDリスト（最大500件）
            text: 送信するテキスト
            
        Returns:
            bool: 送信が成功したかどうか
        """
        if not user_ids:
            print("送信先ユーザーがありません")
            return True
        
        if len(user_ids) > 500:
            print("警告: 送信先が500件を超えています。最初の500件のみ送信します")
            user_ids = user_ids[:500]
        
        headers = {
            'Authorization': f'Bearer {self.channel_access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'to': user_ids,
            'messages': [
                {
                    'type': 'text',
                    'text': text
                }
            ]
        }
        
        try:
            response = requests.post(self.multicast_api_url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            print(f"✓ 一斉送信を送信しました ({len(user_ids)}件)")
            return True
        except requests.RequestException as e:
            print(f"エラー: 一斉送信に失敗しました - {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"レスポンス: {e.response.text}")
            return False
    
    def verify_signature(self, body: str, signature: str) -> bool:
        """
        Webhook署名を検証
        
        Args:
            body: リクエストボディ
            signature: X-Line-Signatureヘッダーの値
            
        Returns:
            bool: 署名が正しい場合True
        """
        if not self.channel_secret:
            print("警告: チャネルシークレットが設定されていません")
            return False
        
        hash_digest = hmac.new(
            self.channel_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        expected_signature = base64.b64encode(hash_digest).decode('utf-8')
        
        return signature == expected_signature

