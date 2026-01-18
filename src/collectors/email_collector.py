"""メールから情報を収集するモジュール"""

import email
import imaplib
import os
import re
import sys
from datetime import datetime
from email.header import decode_header
from email.message import Message
from pathlib import Path
from typing import Dict, List, Optional

from bs4 import BeautifulSoup

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.collectors.base import BaseInformationCollector, InformationItem  # noqa: E402
from src.storage import Storage  # noqa: E402


class EmailCollector(BaseInformationCollector):
    """メールから情報を収集するクラス"""

    def __init__(self, storage: Optional[Storage] = None):
        """
        初期化

        Args:
            storage: Storageインスタンス
        """
        super().__init__(storage)
        self.processed_message_ids = set()
        self._load_processed_ids()

    def collect(self, site_config: Dict) -> List[InformationItem]:
        """
        メールから情報を収集

        Args:
            site_config: サイト設定

        Returns:
            List[InformationItem]: 収集した情報アイテムのリスト
        """
        collector_config = site_config.get("collector_config", {})
        email_account_id = collector_config.get("email_account_id")
        subscription_email = collector_config.get("subscription_email")
        sender_email = collector_config.get("sender_email")
        subject_pattern = collector_config.get("subject_pattern", "")

        if not email_account_id or not subscription_email:
            print(f"警告: メールアカウント設定が不完全です (site_id: {site_config.get('id')})")
            return []

        # メールアカウント情報を取得
        email_account = self._get_email_account(email_account_id)
        if not email_account:
            print(f"警告: メールアカウントが見つかりません (account_id: {email_account_id})")
            return []

        # メールを受信
        messages = self._fetch_emails(email_account, subscription_email, sender_email, subject_pattern)

        # 情報アイテムに変換
        items = []
        for msg in messages:
            item = self._parse_email_to_item(msg, site_config)
            if item:
                items.append(item)

        return items

    def _get_email_account(self, account_id: str) -> Optional[Dict]:
        """
        メールアカウント情報を取得

        Args:
            account_id: アカウントID

        Returns:
            Dict: メールアカウント情報
        """
        accounts_data = self.storage.load_email_accounts()
        if not accounts_data:
            return None

        accounts = accounts_data.get("accounts", [])
        return next((acc for acc in accounts if acc.get("id") == account_id), None)

    def _fetch_emails(
        self,
        email_account: Dict,
        subscription_email: str,
        sender_email: Optional[str] = None,
        subject_pattern: Optional[str] = None,
    ) -> List[Message]:
        """
        メールを受信

        Args:
            email_account: メールアカウント情報
            subscription_email: 購読に使用したメールアドレス（エイリアス含む）
            sender_email: 送信者メールアドレス（フィルタ用）
            subject_pattern: 件名パターン（フィルタ用）

        Returns:
            List[Message]: メールメッセージのリスト
        """
        try:
            # IMAP接続
            imap_server = email_account.get("imap_server", "imap.gmail.com")
            imap_port = email_account.get("imap_port", 993)
            username = email_account.get("username")
            # パスワードはemail_accounts.jsonまたは環境変数から取得
            # 環境変数GMAIL_APP_PASSWORDが優先される（セキュリティのため）
            password = os.getenv("GMAIL_APP_PASSWORD") or email_account.get("password")

            if not password:
                print("警告: メールアカウントのパスワードが設定されていません")
                return []

            mail = imaplib.IMAP4_SSL(imap_server, imap_port)
            mail.login(username, password)
            mail.select("INBOX")

            # 検索条件を構築
            search_criteria = ["UNSEEN"]  # 未読メール

            # エイリアスでのフィルタリング（TOフィールド）
            if subscription_email:
                search_criteria.append(f'TO "{subscription_email}"')

            # 送信者でのフィルタリング
            if sender_email:
                search_criteria.append(f'FROM "{sender_email}"')

            # 件名でのフィルタリング
            if subject_pattern:
                search_criteria.append(f'SUBJECT "{subject_pattern}"')

            # メールを検索
            status, message_numbers = mail.search(None, *search_criteria)

            if status != "OK":
                print("警告: メール検索に失敗しました")
                mail.close()
                mail.logout()
                return []

            messages = []
            for num in message_numbers[0].split():
                try:
                    status, msg_data = mail.fetch(num, "(RFC822)")
                    if status == "OK":
                        msg = email.message_from_bytes(msg_data[0][1])
                        message_id = msg.get("Message-ID", "")

                        # 重複チェック
                        if message_id and message_id in self.processed_message_ids:
                            continue

                        messages.append(msg)
                        self.processed_message_ids.add(message_id)
                except Exception as e:
                    print(f"警告: メールの取得に失敗しました: {e}")
                    continue

            mail.close()
            mail.logout()

            print(f"✓ {len(messages)}件の新着メールを取得しました")
            return messages

        except Exception as e:
            print(f"エラー: メール受信に失敗しました - {e}")
            return []

    def _parse_email_to_item(self, msg: Message, site_config: Dict) -> Optional[InformationItem]:
        """
        メールをInformationItemに変換

        Args:
            msg: メールメッセージ
            site_config: サイト設定

        Returns:
            InformationItem: 情報アイテム
        """
        try:
            # 件名を取得
            subject = self._decode_header(msg.get("Subject", ""))

            # 送信日時を取得
            date_str = msg.get("Date", "")
            published_at = self._parse_email_date(date_str)

            # メール本文を取得
            body = self._get_email_body(msg)

            # HTMLからリンクとテキストを抽出
            links = self._extract_links(body)
            main_link = links[0] if links else site_config.get("url", "")

            # タイトルを抽出（件名または本文から）
            title = subject or self._extract_title_from_body(body) or "メール通知"

            # 要約を生成（オプション）
            summary = None
            collector_config = site_config.get("collector_config", {})
            if collector_config.get("summary_enabled", False):
                summary = self._generate_summary(body, collector_config)

            # コンテンツハッシュを生成
            from src.diff_detector import DiffDetector

            detector = DiffDetector()
            content_hash = detector.generate_content_hash(title, main_link, summary)

            item = InformationItem(
                title=title,
                url=main_link,
                category=site_config.get("category", ""),
                site_id=site_config.get("id", ""),
                site_name=site_config.get("name", ""),
                published_at=published_at,
                summary=summary,
                content_hash=content_hash,
            )

            return item

        except Exception as e:
            print(f"エラー: メールのパースに失敗しました - {e}")
            return None

    def _decode_header(self, header: str) -> str:
        """
        メールヘッダーをデコード

        Args:
            header: ヘッダー文字列

        Returns:
            str: デコードされた文字列
        """
        if not header:
            return ""

        decoded_parts = decode_header(header)
        decoded_str = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded_str += part.decode(encoding)
                else:
                    decoded_str += part.decode("utf-8", errors="ignore")
            else:
                decoded_str += part

        return decoded_str

    def _parse_email_date(self, date_str: str) -> str:
        """
        メールの日時をパース

        Args:
            date_str: 日時文字列

        Returns:
            str: ISO形式の日時文字列
        """
        if not date_str:
            return datetime.now().isoformat()

        try:
            from email.utils import parsedate_to_datetime

            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except:
            return datetime.now().isoformat()

    def _get_email_body(self, msg: Message) -> str:
        """
        メール本文を取得

        Args:
            msg: メールメッセージ

        Returns:
            str: メール本文
        """
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # 添付ファイルはスキップ
                if "attachment" in content_disposition:
                    continue

                # HTMLまたはテキストを取得
                if content_type == "text/html":
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="ignore")
                            break
                    except:
                        pass
                elif content_type == "text/plain" and not body:
                    try:
                        payload = part.get_payload(decode=True)
                        if payload:
                            body = payload.decode("utf-8", errors="ignore")
                    except:
                        pass
        else:
            # シンプルなメール
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode("utf-8", errors="ignore")
            except:
                pass

        return body

    def _extract_links(self, html: str) -> List[str]:
        """
        HTMLからリンクを抽出

        Args:
            html: HTML文字列

        Returns:
            List[str]: リンクURLのリスト
        """
        if not html:
            return []

        try:
            soup = BeautifulSoup(html, "html.parser")
            links = []

            # <a>タグからリンクを抽出
            for a in soup.find_all("a", href=True):
                href = a["href"]
                # 相対URLを絶対URLに変換（必要に応じて）
                if href.startswith("http"):
                    links.append(href)

            return links
        except:
            # HTMLパースに失敗した場合は正規表現で抽出
            pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
            links = re.findall(pattern, html)
            return links[:10]  # 最大10件

    def _extract_title_from_body(self, html: str) -> Optional[str]:
        """
        メール本文からタイトルを抽出

        Args:
            html: HTML文字列

        Returns:
            str: タイトル
        """
        if not html:
            return None

        try:
            soup = BeautifulSoup(html, "html.parser")

            # <h1>タグを探す
            h1 = soup.find("h1")
            if h1:
                return h1.get_text(strip=True)

            # <title>タグを探す
            title = soup.find("title")
            if title:
                return title.get_text(strip=True)

            # 最初の見出しを探す
            for tag in ["h2", "h3", "strong", "b"]:
                elem = soup.find(tag)
                if elem:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 10:
                        return text

            return None
        except:
            return None

    def _generate_summary(self, body: str, collector_config: Dict) -> Optional[str]:
        """
        AI要約を生成

        Args:
            body: メール本文
            collector_config: コレクター設定

        Returns:
            str: 要約テキスト
        """
        summary_enabled = collector_config.get("summary_enabled", False)
        if not summary_enabled:
            return None

        try:
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("警告: GEMINI_API_KEYが設定されていません")
                return None

            genai.configure(api_key=api_key)
            model_name = collector_config.get("summary_model", "gemini-1.5-flash")
            model = genai.GenerativeModel(model_name)

            # メール本文をテキストに変換（HTMLタグを除去）
            soup = BeautifulSoup(body, "html.parser")
            text_body = soup.get_text(separator=" ", strip=True)

            # 長すぎる場合は切り詰め
            if len(text_body) > 10000:
                text_body = text_body[:10000] + "..."

            prompt = f"""以下のメール内容を3-5行で簡潔に要約してください。重要な情報やリンクを含めてください。

{text_body}"""

            response = model.generate_content(prompt)
            summary = response.text.strip()

            print(f"✓ AI要約を生成しました ({len(summary)}文字)")
            return summary

        except Exception as e:
            print(f"警告: AI要約の生成に失敗しました - {e}")
            return None

    def _load_processed_ids(self):
        """処理済みメールIDを読み込み"""
        items_data = self.storage.load_information_items()
        if items_data and items_data.get("items"):
            # 既存の情報アイテムからメールIDを抽出（実装は簡略化）
            pass

    def mark_as_collected(self, site_id: str, items: List[InformationItem]) -> bool:
        """
        収集完了を記録（メールIDも保存）

        Args:
            site_id: サイトID
            items: 収集した情報アイテムのリスト

        Returns:
            bool: 記録が成功したかどうか
        """
        # 親クラスのメソッドを呼び出し
        result = super().mark_as_collected(site_id, items)

        # 処理済みメールIDを保存（簡略化のため、ここでは実装しない）
        # 実際の実装では、itemsにメールIDを含めて保存する

        return result
