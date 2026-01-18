"""LINE Webhook Server"""

import json
import os
from pathlib import Path

from flask import Flask, abort, request
from dotenv import load_dotenv

from src.line_notifier import LineNotifier
from src.user_manager import UserManager
from src.storage import Storage

# Load environment variables
project_root = Path(__file__).parent.parent
load_dotenv(project_root / ".env")

app = Flask(__name__)

# Global instances
storage = Storage()
user_manager = UserManager(storage)


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    LINE Webhook endpoint
    """
    print("=" * 60)
    print("Webhook received")
    print("=" * 60)

    # Signature verification
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    print(f"Body length: {len(body)} bytes")
    print(f"Signature: {signature[:20]}..." if signature else "Signature: None")

    try:
        notifier = LineNotifier()
        print("✓ LineNotifier initialized successfully")

        # Verify signature
        if notifier.channel_secret:
            if not notifier.verify_signature(body, signature):
                print("❌ Signature verification failed")
                abort(400)
            print("✓ Signature verification successful")
        else:
            print("⚠️  Channel secret not set (skipping signature verification)")

    except ValueError as e:
        print(f"❌ LINE Notifier initialization error: {e}")
        abort(500)

    # Process events
    try:
        # Handle empty body or invalid JSON
        if not body or body.strip() == "":
            print("⚠️  Empty request body received")
            return "OK", 200

        # Parse JSON
        body_json = json.loads(body)
        events = body_json.get("events", [])
        print(f"Number of events: {len(events)}")

        for i, event in enumerate(events, 1):
            event_type = event.get("type")
            print(f"\n--- Event {i}/{len(events)} ---")
            print(f"Type: {event_type}")

            # Message event
            if event_type == "message":
                message_type = event["message"].get("type")
                print(f"Message type: {message_type}")

                if message_type == "text":
                    handle_text_message(event, notifier)
                else:
                    handle_unsupported_message(event, notifier)

            # Follow/Unfollow event
            elif event_type == "follow":
                handle_follow_event(event, notifier)
            elif event_type == "unfollow":
                handle_unfollow_event(event)

        print("\n" + "=" * 60)
        print("Webhook processing completed")
        print("=" * 60)
        return "OK", 200

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        import traceback

        traceback.print_exc()
        abort(500)


def handle_text_message(event: dict, notifier: LineNotifier):
    """
    Process text message

    Args:
        event: LINE event
        notifier: LineNotifier instance
    """
    reply_token = event["replyToken"]
    message_text = event["message"]["text"].strip()
    user_id = event["source"].get("userId", "unknown")

    print(f"▶ Received message: '{message_text}' (User ID: {user_id[:10]}...)")

    # Command processing
    if message_text == "登録":
        handle_register_command(reply_token, user_id, notifier)
    elif message_text.startswith("購読 ") or message_text.startswith("購読　"):
        # Support both half-width and full-width spaces
        category = message_text.replace("購読 ", "").replace("購読　", "").strip()
        handle_subscribe_command(reply_token, user_id, category, notifier)
    elif message_text.startswith("購読解除 ") or message_text.startswith("購読解除　"):
        # Support both half-width and full-width spaces
        category = message_text.replace("購読解除 ", "").replace("購読解除　", "").strip()
        handle_unsubscribe_command(reply_token, user_id, category, notifier)
    elif message_text == "サイト一覧":
        handle_sites_list_command(reply_token, notifier)
    else:
        # Default: Help message
        handle_help_message(reply_token, notifier)


def handle_register_command(reply_token: str, user_id: str, notifier: LineNotifier):
    """
    Process user registration command

    Args:
        reply_token: Reply token
        user_id: User ID
        notifier: LineNotifier instance
    """
    print("  → Processing user registration")

    success = user_manager.register_user(user_id)
    if success:
        message = """✅ 登録が完了しました！

以下のコマンドが使用できます：
• 購読 [カテゴリ名] - カテゴリを購読
• 購読解除 [カテゴリ名] - 購読を解除
• サイト一覧 - 登録されているサイト一覧を表示"""
    else:
        message = "❌ 登録に失敗しました。しばらくしてから再度お試しください。"

    notifier.reply_text_message(reply_token, message)


def handle_subscribe_command(reply_token: str, user_id: str, category: str, notifier: LineNotifier):
    """
    Process category subscription command

    Args:
        reply_token: Reply token
        user_id: User ID
        category: Category name
        notifier: LineNotifier instance
    """
    print(f"  → Processing category subscription: {category}")

    # Check if user is registered
    user = user_manager.get_user(user_id)
    if not user:
        notifier.reply_text_message(reply_token, "❌ ユーザーが登録されていません。まず「登録」コマンドで登録してください。")
        return

    success = user_manager.subscribe_category(user_id, category)
    if success:
        message = f"✅ 「{category}」カテゴリを購読しました！\n\n新着情報が配信されます。"
    else:
        message = f"❌ 「{category}」カテゴリの購読に失敗しました。"

    notifier.reply_text_message(reply_token, message)


def handle_unsubscribe_command(reply_token: str, user_id: str, category: str, notifier: LineNotifier):
    """
    Process category unsubscribe command

    Args:
        reply_token: Reply token
        user_id: User ID
        category: Category name
        notifier: LineNotifier instance
    """
    print(f"  → Processing category unsubscribe: {category}")

    success = user_manager.unsubscribe_category(user_id, category)
    if success:
        message = f"✅ 「{category}」カテゴリの購読を解除しました。"
    else:
        message = f"❌ 「{category}」カテゴリの購読解除に失敗しました。"

    notifier.reply_text_message(reply_token, message)


def handle_sites_list_command(reply_token: str, notifier: LineNotifier):
    """
    Process sites list command

    Args:
        reply_token: Reply token
        notifier: LineNotifier instance
    """
    print("  → Displaying sites list")

    sites_data = storage.load_sites()
    if not sites_data or not sites_data.get("sites"):
        message = "現在登録されているサイトはありません。"
    else:
        sites = sites_data["sites"]
        lines = ["📰 登録されているサイト一覧\n"]
        for i, site in enumerate(sites, 1):
            status = "✅" if site.get("enabled", False) else "❌"
            lines.append(f"{i}. {status} {site.get('name', '不明')}")
            lines.append(f"   カテゴリ: {site.get('category', '不明')}")
            if site.get("url"):
                lines.append(f"   URL: {site['url']}")
            lines.append("")

        message = "\n".join(lines)

    notifier.reply_text_message(reply_token, message)


def handle_help_message(reply_token: str, notifier: LineNotifier):
    """
    Send help message

    Args:
        reply_token: Reply token
        notifier: LineNotifier instance
    """
    message = """📰 情報配信Bot ヘルプ

【コマンド一覧】
• 登録 - ユーザー登録
• 購読 [カテゴリ名] - カテゴリを購読
• 購読解除 [カテゴリ名] - 購読を解除
• サイト一覧 - 登録されているサイト一覧を表示

【例】
• 購読 AI
• 購読解除 ドローン"""

    notifier.reply_text_message(reply_token, message)


def handle_unsupported_message(event: dict, notifier: LineNotifier):
    """
    Handle unsupported message type

    Args:
        event: LINE event
        notifier: LineNotifier instance
    """
    reply_token = event["replyToken"]
    message_type = event["message"].get("type", "unknown")

    print(f"Unsupported message: {message_type}")

    notifier.reply_text_message(
        reply_token, "このメッセージタイプには対応していません。\nテキストメッセージでコマンドを送信してください。"
    )


def handle_follow_event(event: dict, notifier: LineNotifier):
    """
    Handle follow event (friend added)

    Args:
        event: LINE event
        notifier: LineNotifier instance
    """
    reply_token = event["replyToken"]
    user_id = event["source"].get("userId", "unknown")

    print(f"Friend added: {user_id[:10]}...")

    # Send welcome message
    welcome_message = """📰 情報配信Botへようこそ！

このBotは、AI、ドローン、SDGsなどの最新情報を自動で配信します。

まずは「登録」コマンドでユーザー登録を行ってください。

【コマンド一覧】
• 登録 - ユーザー登録
• 購読 [カテゴリ名] - カテゴリを購読
• 購読解除 [カテゴリ名] - 購読を解除
• サイト一覧 - 登録されているサイト一覧を表示"""

    notifier.reply_text_message(reply_token, welcome_message)


def handle_unfollow_event(event: dict):
    """
    Handle unfollow event (blocked)

    Args:
        event: LINE event
    """
    user_id = event["source"].get("userId", "unknown")
    print(f"Friend removed: {user_id[:10]}...")

    # Unregister user
    user_manager.unregister_user(user_id)


@app.route("/", methods=["GET"])
def index():
    """
    Root endpoint
    """
    return "📰 Information Delivery Bot Webhook Server is running!", 200


@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint
    """
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
